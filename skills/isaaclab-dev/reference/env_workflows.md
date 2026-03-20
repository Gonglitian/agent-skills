# 环境工作流详解

## Manager-Based vs Direct 对比

| 特性 | Manager-Based | Direct |
|------|---------------|--------|
| 代码结构 | 配置类 + Manager | 单一环境类 |
| 模块化 | 高 (各组件独立) | 低 (集中实现) |
| 性能 | 良好 | 最优 |
| 灵活性 | 通过配置切换 | 完全自定义 |
| 学习曲线 | 需理解 Manager 系统 | 更直观 |
| 适用场景 | 快速原型、团队协作 | 性能优化、复杂逻辑 |

## Manager-Based 工作流

### 环境类继承关系

```
ManagerBasedEnvCfg
    └── ManagerBasedRLEnvCfg (增加 rewards, terminations, curriculum)
        └── MimicEnvCfg (增加 mimic 数据生成配置)

ManagerBasedEnv
    └── ManagerBasedRLEnv
        └── ManagerBasedRLMimicEnv
```

### 核心 Manager 类型

```python
# 1. ActionManager - 处理动作
# 配置通过 ActionsCfg 定义,包含多个 ActionTermCfg

# 2. ObservationManager - 计算观测
# 配置通过 ObservationsCfg 定义,包含多个 ObservationGroupCfg

# 3. RewardManager - 计算奖励 (仅 RL 环境)
# 配置通过 RewardsCfg 定义,每个 RewardTermCfg 有 weight 参数

# 4. TerminationManager - 检测终止条件 (仅 RL 环境)
# 配置通过 TerminationsCfg 定义

# 5. EventManager - 域随机化和重置逻辑
# 配置通过 EventsCfg 定义,支持 startup/reset/interval 三种模式

# 6. CurriculumManager - 课程学习 (可选)
# 配置通过 CurriculumCfg 定义

# 7. CommandManager - 命令生成 (可选,如目标位置)
# 配置通过 CommandsCfg 定义
```

### 完整 ManagerBasedRLEnvCfg 示例

```python
from dataclasses import MISSING
import isaaclab.sim as sim_utils
import isaaclab.envs.mdp as mdp
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.assets import ArticulationCfg, RigidObjectCfg, AssetBaseCfg
from isaaclab.managers import (
    ObservationGroupCfg as ObsGroup,
    ObservationTermCfg as ObsTerm,
    RewardTermCfg as RewTerm,
    TerminationTermCfg as DoneTerm,
    EventTermCfg as EventTerm,
    SceneEntityCfg
)
from isaaclab.utils import configclass

##
# Scene
##
@configclass
class ManipulationSceneCfg(InteractiveSceneCfg):
    """场景配置"""
    
    # 机器人
    robot: ArticulationCfg = MISSING  # 由具体环境配置覆盖
    
    # 末端执行器参考框架
    ee_frame: FrameTransformerCfg = MISSING
    
    # 操作物体
    object: RigidObjectCfg = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Object",
        spawn=sim_utils.UsdFileCfg(usd_path="..."),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(0.5, 0.0, 0.1))
    )
    
    # 桌子
    table = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Table",
        spawn=sim_utils.UsdFileCfg(usd_path="..."),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.5, 0.0, 0.0))
    )
    
    # 地面
    ground = AssetBaseCfg(
        prim_path="/World/Ground",
        spawn=sim_utils.GroundPlaneCfg()
    )
    
    # 灯光
    light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=3000.0)
    )

##
# Actions
##
@configclass
class ActionsCfg:
    """动作配置"""
    arm_action: mdp.JointPositionActionCfg = MISSING
    gripper_action: mdp.BinaryJointPositionActionCfg = MISSING

##
# Observations
##
@configclass
class ObservationsCfg:
    """观测配置"""
    
    @configclass
    class PolicyCfg(ObsGroup):
        """策略观测组"""
        # 关节状态
        joint_pos = ObsTerm(func=mdp.joint_pos_rel)
        joint_vel = ObsTerm(func=mdp.joint_vel_rel)
        
        # 物体状态
        object_pos = ObsTerm(
            func=mdp.root_pos_w,
            params={"asset_cfg": SceneEntityCfg("object")}
        )
        
        # 上一步动作
        actions = ObsTerm(func=mdp.last_action)
        
        def __post_init__(self):
            self.enable_corruption = False  # 是否添加噪声
            self.concatenate_terms = True   # 是否拼接为单一张量
    
    policy: PolicyCfg = PolicyCfg()

##
# Rewards
##
@configclass
class RewardsCfg:
    """奖励配置"""
    # 接近奖励
    reaching_object = RewTerm(
        func=mdp.object_ee_distance,
        weight=-1.0,
        params={"object_cfg": SceneEntityCfg("object")}
    )
    
    # 提起奖励
    lifting_object = RewTerm(
        func=mdp.object_is_lifted,
        weight=15.0,
        params={
            "object_cfg": SceneEntityCfg("object"),
            "minimal_height": 0.04
        }
    )
    
    # 动作惩罚
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-0.01)

##
# Terminations
##
@configclass
class TerminationsCfg:
    """终止条件配置"""
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    
    object_dropped = DoneTerm(
        func=mdp.root_height_below_minimum,
        params={"asset_cfg": SceneEntityCfg("object"), "minimum_height": -0.05}
    )

##
# Events
##
@configclass
class EventsCfg:
    """事件配置 (域随机化)"""
    
    # 重置机器人
    reset_robot = EventTerm(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot"),
            "position_range": (-0.1, 0.1),
            "velocity_range": (0.0, 0.0)
        }
    )
    
    # 重置物体
    reset_object = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("object"),
            "pose_range": {"x": (-0.1, 0.1), "y": (-0.1, 0.1)},
            "velocity_range": {}
        }
    )

##
# Environment Config
##
@configclass
class MyManipulationEnvCfg(ManagerBasedRLEnvCfg):
    """完整环境配置"""
    
    # 场景
    scene: ManipulationSceneCfg = ManipulationSceneCfg(
        num_envs=1024,
        env_spacing=2.5,
        replicate_physics=True
    )
    
    # MDP 组件
    actions: ActionsCfg = ActionsCfg()
    observations: ObservationsCfg = ObservationsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventsCfg = EventsCfg()
    
    # 可选组件
    commands = None
    curriculum = None
    
    def __post_init__(self):
        # 仿真参数
        self.decimation = 4              # 环境步 = 4 个仿真步
        self.episode_length_s = 10.0     # episode 时长
        self.sim.dt = 0.01               # 仿真时间步 (100Hz)
        self.sim.render_interval = 2     # 渲染间隔
        
        # 视角设置
        self.viewer.eye = (3.0, 3.0, 3.0)
        self.viewer.lookat = (0.0, 0.0, 0.5)
```

## Direct 工作流

### 环境类继承关系

```
DirectRLEnvCfg
    └── 用户自定义配置

DirectRLEnv
    └── 用户自定义环境类

DirectMARLEnvCfg / DirectMARLEnv  # 多智能体版本
```

### 完整 DirectRLEnv 示例

```python
from collections.abc import Sequence
import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation, ArticulationCfg
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.sim.spawners.from_files import GroundPlaneCfg, spawn_ground_plane
from isaaclab.utils import configclass

@configclass
class MyDirectEnvCfg(DirectRLEnvCfg):
    """Direct 环境配置"""
    
    # 基本设置
    decimation = 2
    episode_length_s = 10.0
    action_scale = 1.0
    action_space = 7      # 动作维度
    observation_space = 16  # 观测维度
    state_space = 0       # 状态维度 (用于 asymmetric actor-critic)
    
    # 仿真配置
    sim: SimulationCfg = SimulationCfg(dt=1/120, render_interval=2)
    
    # 场景配置
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=4096,
        env_spacing=2.5,
        replicate_physics=True
    )
    
    # 机器人配置
    robot_cfg: ArticulationCfg = ArticulationCfg(
        prim_path="/World/envs/env_.*/Robot",
        spawn=sim_utils.UsdFileCfg(usd_path="..."),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0, 0, 0),
            joint_pos={}
        ),
        actuators={}
    )


class MyDirectEnv(DirectRLEnv):
    """Direct 环境实现"""
    
    cfg: MyDirectEnvCfg
    
    def __init__(self, cfg: MyDirectEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)
        
        # 获取关节索引
        self._arm_joint_ids, _ = self.robot.find_joints("joint.*")
        
        # 缓存数据引用
        self.joint_pos = self.robot.data.joint_pos
        self.joint_vel = self.robot.data.joint_vel
    
    def _setup_scene(self):
        """设置场景"""
        # 创建机器人
        self.robot = Articulation(self.cfg.robot_cfg)
        
        # 添加地面
        spawn_ground_plane(prim_path="/World/ground", cfg=GroundPlaneCfg())
        
        # 克隆环境
        self.scene.clone_environments(copy_from_source=False)
        
        # CPU 仿真需要过滤碰撞
        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[])
        
        # 注册到场景
        self.scene.articulations["robot"] = self.robot
        
        # 添加灯光
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0)
        light_cfg.func("/World/Light", light_cfg)
    
    def _pre_physics_step(self, actions: torch.Tensor):
        """物理步之前处理动作"""
        self.actions = self.cfg.action_scale * actions.clone()
    
    def _apply_action(self):
        """应用动作"""
        self.robot.set_joint_position_target(
            self.actions,
            joint_ids=self._arm_joint_ids
        )
    
    def _get_observations(self) -> dict:
        """计算观测"""
        obs = torch.cat([
            self.joint_pos[:, self._arm_joint_ids],
            self.joint_vel[:, self._arm_joint_ids],
        ], dim=-1)
        
        return {"policy": obs}
    
    def _get_rewards(self) -> torch.Tensor:
        """计算奖励"""
        return self._compute_rewards()
    
    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        """计算终止条件"""
        # 更新数据
        self.joint_pos = self.robot.data.joint_pos
        self.joint_vel = self.robot.data.joint_vel
        
        # 超时
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        
        # 异常终止 (如超出范围)
        terminated = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        
        return terminated, time_out
    
    def _reset_idx(self, env_ids: Sequence[int] | None):
        """重置指定环境"""
        if env_ids is None:
            env_ids = self.robot._ALL_INDICES
        
        super()._reset_idx(env_ids)
        
        # 重置关节状态
        joint_pos = self.robot.data.default_joint_pos[env_ids]
        joint_vel = self.robot.data.default_joint_vel[env_ids]
        
        # 可以添加随机化
        joint_pos += torch.randn_like(joint_pos) * 0.1
        
        # 设置根状态
        default_root_state = self.robot.data.default_root_state[env_ids]
        default_root_state[:, :3] += self.scene.env_origins[env_ids]
        
        # 写入
        self.joint_pos[env_ids] = joint_pos
        self.joint_vel[env_ids] = joint_vel
        
        self.robot.write_root_pose_to_sim(default_root_state[:, :7], env_ids)
        self.robot.write_root_velocity_to_sim(default_root_state[:, 7:], env_ids)
        self.robot.write_joint_state_to_sim(joint_pos, joint_vel, None, env_ids)
    
    @torch.jit.script
    def _compute_rewards(self) -> torch.Tensor:
        """JIT 编译的奖励计算 (性能优化)"""
        # 实现奖励逻辑
        return torch.zeros(self.num_envs, device=self.device)
```

## 运行和调试

```python
import argparse
from isaaclab.app import AppLauncher

# 命令行参数
parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=16)
parser.add_argument("--headless", action="store_true")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

# 启动 (必须在其他 isaaclab 导入之前)
app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

# 导入环境
from my_envs import MyEnvCfg, MyEnv  # 或使用 gym.make

def main():
    # 创建环境
    env_cfg = MyEnvCfg()
    env_cfg.scene.num_envs = args.num_envs
    env = MyEnv(cfg=env_cfg)
    
    # 重置
    obs, info = env.reset()
    
    # 主循环
    while simulation_app.is_running():
        with torch.inference_mode():
            # 采样动作
            actions = torch.randn_like(env.action_manager.action)
            
            # 步进
            obs, reward, terminated, truncated, info = env.step(actions)
            
            # 处理重置
            done = terminated | truncated
            if done.any():
                pass  # env.step 内部自动处理重置
    
    env.close()

if __name__ == "__main__":
    main()
    simulation_app.close()
```
