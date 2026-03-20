"""Manager-Based 环境示例

演示如何创建一个完整的 Manager-Based RL 环境。

运行:
    ./isaaclab.sh -p examples/manager_based_env.py --num_envs 32
"""

import argparse
from isaaclab.app import AppLauncher

# 命令行参数
parser = argparse.ArgumentParser(description="Manager-Based Environment Example")
parser.add_argument("--num_envs", type=int, default=16, help="Number of environments")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

# 启动应用 (必须在其他 isaaclab 导入之前)
app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

# ═══════════════════════════════════════════════════════════════════════════════
# 现在可以导入 isaaclab 模块
# ═══════════════════════════════════════════════════════════════════════════════

import torch
import isaaclab.sim as sim_utils
import isaaclab.envs.mdp as mdp

from isaaclab.assets import ArticulationCfg, RigidObjectCfg, AssetBaseCfg
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.envs import ManagerBasedRLEnv, ManagerBasedRLEnvCfg
from isaaclab.managers import (
    ObservationGroupCfg as ObsGroup,
    ObservationTermCfg as ObsTerm,
    RewardTermCfg as RewTerm,
    TerminationTermCfg as DoneTerm,
    EventTermCfg as EventTerm,
    SceneEntityCfg
)
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass

# ═══════════════════════════════════════════════════════════════════════════════
# 场景配置
# ═══════════════════════════════════════════════════════════════════════════════

@configclass
class ReachSceneCfg(InteractiveSceneCfg):
    """Reach 任务场景配置"""
    
    # 机器人 (使用简化的机械臂)
    robot: ArticulationCfg = ArticulationCfg(
        prim_path="{ENV_REGEX_NS}/Robot",
        spawn=sim_utils.UsdFileCfg(
            usd_path="omniverse://localhost/NVIDIA/Assets/Isaac/4.1/Isaac/Robots/FrankaRobotics/FrankaPanda/franka_panda_instanceable.usd",
            activate_contact_sensors=False,
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
            "panda_hand": ImplicitActuatorCfg(
                joint_names_expr=["panda_finger_joint.*"],
                stiffness=400.0,
                damping=80.0,
            ),
        },
    )
    
    # 目标物体 (简单球体)
    target: RigidObjectCfg = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Target",
        spawn=sim_utils.SphereCfg(
            radius=0.02,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(disable_gravity=True),
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=False),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.0, 1.0, 0.0)),
        ),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(0.5, 0.0, 0.5)),
    )
    
    # 地面
    ground = AssetBaseCfg(
        prim_path="/World/Ground",
        spawn=sim_utils.GroundPlaneCfg(),
    )
    
    # 灯光
    light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75)),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MDP 配置
# ═══════════════════════════════════════════════════════════════════════════════

@configclass
class ActionsCfg:
    """动作配置"""
    
    arm_action: mdp.JointPositionActionCfg = mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=["panda_joint.*"],
        scale=0.5,
        use_default_offset=True,
    )


@configclass
class ObservationsCfg:
    """观测配置"""
    
    @configclass
    class PolicyCfg(ObsGroup):
        """策略观测组"""
        
        joint_pos = ObsTerm(func=mdp.joint_pos_rel)
        joint_vel = ObsTerm(func=mdp.joint_vel_rel)
        
        target_pos = ObsTerm(
            func=mdp.root_pos_w,
            params={"asset_cfg": SceneEntityCfg("target")},
        )
        
        actions = ObsTerm(func=mdp.last_action)
        
        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True
    
    policy: PolicyCfg = PolicyCfg()


@configclass
class RewardsCfg:
    """奖励配置"""
    
    # 这是一个简化示例,实际需要自定义奖励函数
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-0.01)
    joint_vel = RewTerm(func=mdp.joint_vel_l2, weight=-0.0001)


@configclass
class TerminationsCfg:
    """终止条件"""
    
    time_out = DoneTerm(func=mdp.time_out, time_out=True)


@configclass
class EventsCfg:
    """事件配置"""
    
    reset_robot = EventTerm(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot"),
            "position_range": (-0.1, 0.1),
            "velocity_range": (0.0, 0.0),
        },
    )
    
    reset_target = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("target"),
            "pose_range": {
                "x": (0.35, 0.65),
                "y": (-0.2, 0.2),
                "z": (0.3, 0.7),
            },
            "velocity_range": {},
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 环境配置
# ═══════════════════════════════════════════════════════════════════════════════

@configclass
class ReachEnvCfg(ManagerBasedRLEnvCfg):
    """完整环境配置"""
    
    # 场景
    scene: ReachSceneCfg = ReachSceneCfg(num_envs=1024, env_spacing=2.5)
    
    # MDP
    actions: ActionsCfg = ActionsCfg()
    observations: ObservationsCfg = ObservationsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventsCfg = EventsCfg()
    
    # 不使用的 manager
    commands = None
    curriculum = None
    
    def __post_init__(self):
        # 仿真参数
        self.decimation = 4
        self.episode_length_s = 5.0
        self.sim.dt = 0.01
        self.sim.render_interval = 2
        
        # 视角
        self.viewer.eye = (2.5, 2.5, 2.5)
        self.viewer.lookat = (0.0, 0.0, 0.5)


# ═══════════════════════════════════════════════════════════════════════════════
# 主函数
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """主函数"""
    # 创建环境配置
    env_cfg = ReachEnvCfg()
    env_cfg.scene.num_envs = args.num_envs
    
    # 创建环境
    env = ManagerBasedRLEnv(cfg=env_cfg)
    
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
            actions = torch.randn(env.num_envs, env.action_manager.total_action_dim, device=env.device)
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
