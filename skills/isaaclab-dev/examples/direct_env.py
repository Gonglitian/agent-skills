"""Direct 环境示例

演示如何创建一个 Direct 风格的 RL 环境。

运行:
    ./isaaclab.sh -p examples/direct_env.py --num_envs 32
"""

import argparse
from isaaclab.app import AppLauncher

# 命令行参数
parser = argparse.ArgumentParser(description="Direct Environment Example")
parser.add_argument("--num_envs", type=int, default=16, help="Number of environments")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

# 启动应用
app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

# ═══════════════════════════════════════════════════════════════════════════════
# 导入
# ═══════════════════════════════════════════════════════════════════════════════

import math
from collections.abc import Sequence
import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation, ArticulationCfg
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.sim.spawners.from_files import GroundPlaneCfg, spawn_ground_plane
from isaaclab.utils import configclass
from isaaclab.utils.math import sample_uniform


# ═══════════════════════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════════════════════

@configclass
class SimpleArmEnvCfg(DirectRLEnvCfg):
    """简单机械臂环境配置"""
    
    # 环境参数
    decimation = 2
    episode_length_s = 10.0
    action_scale = 0.5
    action_space = 7      # 7 DOF 手臂
    observation_space = 14  # 关节位置 + 速度
    state_space = 0
    
    # 仿真配置
    sim: SimulationCfg = SimulationCfg(
        dt=1.0 / 120.0,
        render_interval=2,
    )
    
    # 场景配置
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=4096,
        env_spacing=2.5,
        replicate_physics=True,
    )
    
    # 机器人配置
    robot_cfg: ArticulationCfg = ArticulationCfg(
        prim_path="/World/envs/env_.*/Robot",
        spawn=sim_utils.UsdFileCfg(
            usd_path="omniverse://localhost/NVIDIA/Assets/Isaac/4.1/Isaac/Robots/FrankaRobotics/FrankaPanda/franka_panda_instanceable.usd",
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.0),
            joint_pos={
                "panda_joint1": 0.0,
                "panda_joint2": -0.569,
                "panda_joint3": 0.0,
                "panda_joint4": -2.810,
                "panda_joint5": 0.0,
                "panda_joint6": 3.037,
                "panda_joint7": 0.741,
                "panda_finger_joint.*": 0.04,
            },
        ),
        actuators={
            "panda_shoulder": ImplicitActuatorCfg(
                joint_names_expr=["panda_joint[1-4]"],
                stiffness=400.0,
                damping=80.0,
            ),
            "panda_forearm": ImplicitActuatorCfg(
                joint_names_expr=["panda_joint[5-7]"],
                stiffness=400.0,
                damping=80.0,
            ),
        },
    )
    
    # 奖励参数
    rew_scale_alive = 0.1
    rew_scale_joint_vel = -0.0001
    rew_scale_action_rate = -0.01


# ═══════════════════════════════════════════════════════════════════════════════
# 环境类
# ═══════════════════════════════════════════════════════════════════════════════

class SimpleArmEnv(DirectRLEnv):
    """简单机械臂 Direct 环境"""
    
    cfg: SimpleArmEnvCfg
    
    def __init__(self, cfg: SimpleArmEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)
        
        # 获取手臂关节索引
        self._arm_joint_ids, _ = self.robot.find_joints("panda_joint[1-7]")
        
        # 缓存数据引用
        self.joint_pos = self.robot.data.joint_pos
        self.joint_vel = self.robot.data.joint_vel
        
        # 保存上一步动作用于动作率惩罚
        self._prev_actions = torch.zeros(
            self.num_envs, len(self._arm_joint_ids),
            device=self.device
        )
    
    def _setup_scene(self):
        """设置场景"""
        # 创建机器人
        self.robot = Articulation(self.cfg.robot_cfg)
        
        # 添加地面
        spawn_ground_plane(prim_path="/World/ground", cfg=GroundPlaneCfg())
        
        # 克隆环境
        self.scene.clone_environments(copy_from_source=False)
        
        # CPU 需要过滤碰撞
        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[])
        
        # 注册到场景
        self.scene.articulations["robot"] = self.robot
        
        # 添加灯光
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)
    
    def _pre_physics_step(self, actions: torch.Tensor):
        """物理步之前处理动作"""
        self.actions = self.cfg.action_scale * actions.clone()
    
    def _apply_action(self):
        """应用动作到机器人"""
        # 获取当前关节位置
        current_pos = self.joint_pos[:, self._arm_joint_ids]
        
        # 计算目标位置 (增量控制)
        target_pos = current_pos + self.actions
        
        # 设置目标
        self.robot.set_joint_position_target(target_pos, joint_ids=self._arm_joint_ids)
    
    def _get_observations(self) -> dict:
        """计算观测"""
        obs = torch.cat([
            self.joint_pos[:, self._arm_joint_ids],
            self.joint_vel[:, self._arm_joint_ids],
        ], dim=-1)
        
        return {"policy": obs}
    
    def _get_rewards(self) -> torch.Tensor:
        """计算奖励"""
        # 存活奖励
        alive_reward = self.cfg.rew_scale_alive * torch.ones(self.num_envs, device=self.device)
        
        # 关节速度惩罚
        joint_vel_penalty = self.cfg.rew_scale_joint_vel * torch.sum(
            self.joint_vel[:, self._arm_joint_ids] ** 2, dim=-1
        )
        
        # 动作率惩罚
        action_rate_penalty = self.cfg.rew_scale_action_rate * torch.sum(
            (self.actions - self._prev_actions) ** 2, dim=-1
        )
        
        # 更新上一步动作
        self._prev_actions = self.actions.clone()
        
        return alive_reward + joint_vel_penalty + action_rate_penalty
    
    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        """计算终止条件"""
        # 更新数据
        self.joint_pos = self.robot.data.joint_pos
        self.joint_vel = self.robot.data.joint_vel
        
        # 超时
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        
        # 无异常终止
        terminated = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        
        return terminated, time_out
    
    def _reset_idx(self, env_ids: Sequence[int] | None):
        """重置指定环境"""
        if env_ids is None:
            env_ids = self.robot._ALL_INDICES
        
        super()._reset_idx(env_ids)
        
        # 获取默认状态
        joint_pos = self.robot.data.default_joint_pos[env_ids]
        joint_vel = self.robot.data.default_joint_vel[env_ids]
        
        # 添加随机化
        arm_indices = self._arm_joint_ids
        joint_pos[:, arm_indices] += sample_uniform(
            -0.1, 0.1,
            (len(env_ids), len(arm_indices)),
            device=self.device
        )
        
        # 获取默认根状态
        default_root_state = self.robot.data.default_root_state[env_ids]
        default_root_state[:, :3] += self.scene.env_origins[env_ids]
        
        # 更新内部状态
        self.joint_pos[env_ids] = joint_pos
        self.joint_vel[env_ids] = joint_vel
        
        # 写入仿真
        self.robot.write_root_pose_to_sim(default_root_state[:, :7], env_ids)
        self.robot.write_root_velocity_to_sim(default_root_state[:, 7:], env_ids)
        self.robot.write_joint_state_to_sim(joint_pos, joint_vel, None, env_ids)
        
        # 重置上一步动作
        self._prev_actions[env_ids] = 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# 主函数
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """主函数"""
    # 创建环境配置
    env_cfg = SimpleArmEnvCfg()
    env_cfg.scene.num_envs = args.num_envs
    
    # 创建环境
    env = SimpleArmEnv(cfg=env_cfg)
    
    print(f"[INFO] Created environment with {env.num_envs} environments")
    print(f"[INFO] Observation space: {env.observation_space}")
    print(f"[INFO] Action space: {env.action_space}")
    
    # 重置
    obs, info = env.reset()
    print(f"[INFO] Initial observation shape: {obs['policy'].shape}")
    
    # 运行仿真
    step_count = 0
    while simulation_app.is_running():
        with torch.inference_mode():
            # 随机动作
            actions = torch.randn(env.num_envs, env.cfg.action_space, device=env.device)
            actions = actions.clamp(-1.0, 1.0)
            
            # 步进
            obs, reward, terminated, truncated, info = env.step(actions)
            
            step_count += 1
            if step_count % 100 == 0:
                print(f"[INFO] Step {step_count}, mean reward: {reward.mean().item():.4f}")
    
    # 关闭
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
