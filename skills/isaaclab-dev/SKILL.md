---
name: isaaclab-dev
description: Isaac Lab 机器人仿真开发参考手册。提供环境创建、Manager 系统、传感器配置、域随机化、模仿学习数据生成、cuRobo 集成等 API 参考和最佳实践。当开发 Isaac Lab 环境、配置机器人仿真场景、或使用 isaaclab 相关 API 时使用此技能。
---

# Isaac Lab 开发参考手册

## 核心概念速览

### 两种环境设计工作流

| 工作流 | 适用场景 | 核心类 |
|--------|----------|--------|
| **Manager-Based** | 模块化开发、快速原型、团队协作 | `ManagerBasedEnv`, `ManagerBasedRLEnv` |
| **Direct** | 性能优化、复杂逻辑、从 IsaacGym 迁移 | `DirectRLEnv`, `DirectMARLEnv` |

### 核心模块导入

```python
# 仿真和应用
from isaaclab.app import AppLauncher
from isaaclab.sim import SimulationContext, SimulationCfg
import isaaclab.sim as sim_utils

# 环境
from isaaclab.envs import ManagerBasedEnv, ManagerBasedEnvCfg
from isaaclab.envs import ManagerBasedRLEnv, ManagerBasedRLEnvCfg
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg
import isaaclab.envs.mdp as mdp

# 场景和资产
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.assets import Articulation, ArticulationCfg
from isaaclab.assets import RigidObject, RigidObjectCfg

# Manager 系统
from isaaclab.managers import (
    ActionManager, ActionTermCfg,
    ObservationManager, ObservationTermCfg, ObservationGroupCfg,
    EventManager, EventTermCfg,
    RewardManager, RewardTermCfg,
    TerminationManager, TerminationTermCfg,
    SceneEntityCfg
)

# 传感器
from isaaclab.sensors import Camera, CameraCfg, TiledCamera
from isaaclab.sensors import ContactSensor, ContactSensorCfg
from isaaclab.sensors import FrameTransformer, FrameTransformerCfg

# 控制器
from isaaclab.controllers import DifferentialIKController, DifferentialIKControllerCfg

# 配置装饰器
from isaaclab.utils import configclass
```

## Manager-Based 环境结构

```python
@configclass
class MySceneCfg(InteractiveSceneCfg):
    """场景配置 - 定义环境中的所有实体"""
    robot: ArticulationCfg = FRANKA_PANDA_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    object: RigidObjectCfg = ...
    table: AssetBaseCfg = ...

@configclass
class MyActionsCfg:
    """动作配置"""
    arm_action: mdp.JointPositionActionCfg = ...
    gripper_action: mdp.BinaryJointPositionActionCfg = ...

@configclass
class MyObservationsCfg:
    """观测配置"""
    @configclass
    class PolicyCfg(ObservationGroupCfg):
        joint_pos = ObservationTermCfg(func=mdp.joint_pos_rel)
        joint_vel = ObservationTermCfg(func=mdp.joint_vel_rel)
        # ...
    policy: PolicyCfg = PolicyCfg()

@configclass
class MyEventsCfg:
    """事件配置 (域随机化)"""
    reset_robot = EventTermCfg(func=mdp.reset_joints_by_offset, mode="reset", ...)
    randomize_mass = EventTermCfg(func=mdp.randomize_rigid_body_mass, mode="startup", ...)

@configclass
class MyEnvCfg(ManagerBasedRLEnvCfg):
    scene: MySceneCfg = MySceneCfg(num_envs=1024, env_spacing=2.5)
    actions: MyActionsCfg = MyActionsCfg()
    observations: MyObservationsCfg = MyObservationsCfg()
    events: MyEventsCfg = MyEventsCfg()
    # rewards, terminations, curriculum...
```

详细指南: [reference/env_workflows.md](reference/env_workflows.md)

## Direct 环境结构

```python
class MyDirectEnv(DirectRLEnv):
    cfg: MyDirectEnvCfg
    
    def _setup_scene(self):
        """设置场景 - 创建资产和克隆环境"""
        self.robot = Articulation(self.cfg.robot_cfg)
        spawn_ground_plane(...)
        self.scene.clone_environments(copy_from_source=False)
        self.scene.articulations["robot"] = self.robot
    
    def _pre_physics_step(self, actions: torch.Tensor):
        """物理步之前 - 处理动作"""
        self.actions = actions.clone()
    
    def _apply_action(self):
        """应用动作到机器人"""
        self.robot.set_joint_position_target(self.actions)
    
    def _get_observations(self) -> dict:
        """计算观测"""
        return {"policy": torch.cat([self.joint_pos, self.joint_vel], dim=-1)}
    
    def _get_rewards(self) -> torch.Tensor:
        """计算奖励"""
        return compute_rewards(...)
    
    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        """返回 (terminated, time_out)"""
        return out_of_bounds, time_out
    
    def _reset_idx(self, env_ids):
        """重置指定环境"""
        super()._reset_idx(env_ids)
        # 重置机器人状态...
```

## 常用 Action 配置

```python
# 关节位置控制
mdp.JointPositionActionCfg(
    asset_name="robot",
    joint_names=["panda_joint.*"],
    scale=1.0,
    use_default_offset=True
)

# 关节速度控制
mdp.JointVelocityActionCfg(asset_name="robot", joint_names=[".*"], scale=1.0)

# 关节力矩控制
mdp.JointEffortActionCfg(asset_name="robot", joint_names=[".*"], scale=5.0)

# 末端 IK 控制 (相对位姿)
mdp.DifferentialInverseKinematicsActionCfg(
    asset_name="robot",
    joint_names=["panda_joint.*"],
    body_name="panda_hand",
    controller=DifferentialIKControllerCfg(
        command_type="pose",
        use_relative_mode=True,
        ik_method="dls"
    ),
    scale=0.5,
    body_offset=mdp.DifferentialInverseKinematicsActionCfg.OffsetCfg(pos=[0, 0, 0.107])
)

# 二值夹爪控制
mdp.BinaryJointPositionActionCfg(
    asset_name="robot",
    joint_names=["panda_finger_joint.*"],
    open_command_expr={"panda_finger_joint.*": 0.04},
    close_command_expr={"panda_finger_joint.*": 0.0}
)
```

完整参考: [reference/managers_api.md](reference/managers_api.md)

## 常用 Observation 函数

```python
# 关节状态
ObservationTermCfg(func=mdp.joint_pos)           # 绝对位置
ObservationTermCfg(func=mdp.joint_pos_rel)       # 相对位置 (减去默认值)
ObservationTermCfg(func=mdp.joint_vel)           # 速度
ObservationTermCfg(func=mdp.joint_vel_rel)       # 相对速度

# 根状态
ObservationTermCfg(func=mdp.root_pos_w)          # 世界坐标位置
ObservationTermCfg(func=mdp.root_quat_w)         # 世界坐标四元数
ObservationTermCfg(func=mdp.base_lin_vel)        # 本体线速度
ObservationTermCfg(func=mdp.base_ang_vel)        # 本体角速度
ObservationTermCfg(func=mdp.projected_gravity)   # 投影重力

# 相机图像
ObservationTermCfg(
    func=mdp.image,
    params={"sensor_cfg": SceneEntityCfg("camera"), "data_type": "rgb", "normalize": False}
)

# 上一步动作
ObservationTermCfg(func=mdp.last_action)
```

完整参考: [reference/mdp_functions.md](reference/mdp_functions.md)

## 相机配置

```python
from isaaclab.sensors import CameraCfg
import isaaclab.sim as sim_utils

# 场景中添加相机
@configclass
class MySceneCfg(InteractiveSceneCfg):
    # 第三人称相机 (固定位置)
    front_cam = CameraCfg(
        prim_path="{ENV_REGEX_NS}/front_cam",
        update_period=0.0,  # 0.0 表示每步更新
        height=200,
        width=200,
        data_types=["rgb", "distance_to_image_plane"],
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=24.0,
            focus_distance=400.0,
            horizontal_aperture=20.955,
            clipping_range=(0.1, 2.0)
        ),
        offset=CameraCfg.OffsetCfg(
            pos=(1.0, 0.0, 0.5),
            rot=(0.35355, -0.61237, -0.61237, 0.35355),
            convention="ros"
        )
    )
    
    # 腕部相机 (挂载在机器人末端)
    wrist_cam = CameraCfg(
        prim_path="{ENV_REGEX_NS}/Robot/panda_hand/wrist_cam",
        update_period=0.0,
        height=200,
        width=200,
        data_types=["rgb"],
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=24.0,
            clipping_range=(0.01, 1.0)
        ),
        offset=CameraCfg.OffsetCfg(
            pos=(0.13, 0.0, -0.15),
            rot=(-0.70614, 0.03701, 0.03701, -0.70614),
            convention="ros"
        )
    )
```

详细指南: [guides/camera_setup.md](guides/camera_setup.md)

## 域随机化 (Events)

```python
@configclass
class EventCfg:
    # 启动时 - 只执行一次
    randomize_mass = EventTermCfg(
        func=mdp.randomize_rigid_body_mass,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("object"),
            "mass_distribution_params": (0.5, 1.5),
            "operation": "scale"
        }
    )
    
    # 重置时 - 每个 episode 开始
    reset_robot_joints = EventTermCfg(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot"),
            "position_range": (-0.1, 0.1),
            "velocity_range": (-0.1, 0.1)
        }
    )
    
    reset_object_pose = EventTermCfg(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("object"),
            "pose_range": {"x": (-0.1, 0.1), "y": (-0.1, 0.1), "z": (0.0, 0.0)},
            "velocity_range": {}
        }
    )
    
    # 周期性 - 每隔 N 步
    push_robot = EventTermCfg(
        func=mdp.push_by_setting_velocity,
        mode="interval",
        interval_range_s=(10.0, 15.0),
        params={...}
    )
```

详细指南: [guides/domain_randomization.md](guides/domain_randomization.md)

## Spawners 快速参考

```python
import isaaclab.sim as sim_utils

# 从 USD 文件加载
sim_utils.UsdFileCfg(usd_path="path/to/asset.usd")

# 基本形状
sim_utils.CuboidCfg(size=(0.1, 0.1, 0.1))
sim_utils.SphereCfg(radius=0.05)
sim_utils.CylinderCfg(radius=0.05, height=0.1)
sim_utils.ConeCfg(radius=0.05, height=0.1)

# 地面平面
sim_utils.GroundPlaneCfg()

# 灯光
sim_utils.DomeLightCfg(color=(0.75, 0.75, 0.75), intensity=3000.0)
sim_utils.DistantLightCfg(color=(1.0, 1.0, 1.0), intensity=3000.0)

# 物理材质
sim_utils.RigidBodyPropertiesCfg(
    disable_gravity=False,
    max_depenetration_velocity=10.0
)
```

完整参考: [reference/spawners_api.md](reference/spawners_api.md)

## 资产配置模式

```python
# Articulation (机器人)
robot_cfg = ArticulationCfg(
    prim_path="{ENV_REGEX_NS}/Robot",
    spawn=sim_utils.UsdFileCfg(usd_path="path/to/robot.usd"),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.0),
        joint_pos={"joint1": 0.0, "joint2": 0.5}
    ),
    actuators={
        "arm": ImplicitActuatorCfg(
            joint_names_expr=["joint.*"],
            stiffness=100.0,
            damping=10.0
        )
    }
)

# RigidObject (可操作物体)
object_cfg = RigidObjectCfg(
    prim_path="{ENV_REGEX_NS}/Object",
    spawn=sim_utils.UsdFileCfg(usd_path="path/to/object.usd"),
    init_state=RigidObjectCfg.InitialStateCfg(
        pos=(0.5, 0.0, 0.1),
        rot=(1.0, 0.0, 0.0, 0.0)
    )
)

# 静态资产 (桌子等)
table_cfg = AssetBaseCfg(
    prim_path="{ENV_REGEX_NS}/Table",
    spawn=sim_utils.UsdFileCfg(usd_path="path/to/table.usd"),
    init_state=AssetBaseCfg.InitialStateCfg(pos=(0.5, 0.0, 0.0))
)
```

详细指南: [guides/custom_assets.md](guides/custom_assets.md)

## 应用启动模板

```python
import argparse
from isaaclab.app import AppLauncher

# 解析命令行参数
parser = argparse.ArgumentParser(description="My Isaac Lab script")
parser.add_argument("--num_envs", type=int, default=16)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

# 启动应用 (必须在导入其他 isaaclab 模块之前)
app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

# 现在可以导入 isaaclab 模块
import isaaclab.sim as sim_utils
from isaaclab.envs import ManagerBasedEnv
# ...

def main():
    env_cfg = MyEnvCfg()
    env_cfg.scene.num_envs = args.num_envs
    env = ManagerBasedEnv(cfg=env_cfg)
    
    env.reset()
    while simulation_app.is_running():
        with torch.inference_mode():
            actions = torch.randn_like(env.action_manager.action)
            obs, _ = env.step(actions)
    
    env.close()

if __name__ == "__main__":
    main()
    simulation_app.close()
```

## 详细参考文档

### API 参考
- [reference/env_workflows.md](reference/env_workflows.md) - 环境工作流详解
- [reference/managers_api.md](reference/managers_api.md) - Manager 系统 API
- [reference/assets_api.md](reference/assets_api.md) - 资产系统 API
- [reference/sensors_api.md](reference/sensors_api.md) - 传感器系统 API
- [reference/mdp_functions.md](reference/mdp_functions.md) - MDP 预定义函数
- [reference/spawners_api.md](reference/spawners_api.md) - Spawners API
- [reference/simulation_api.md](reference/simulation_api.md) - 仿真控制 API

### 开发指南
- [guides/create_env.md](guides/create_env.md) - 创建新环境步骤
- [guides/camera_setup.md](guides/camera_setup.md) - 相机和传感器设置
- [guides/domain_randomization.md](guides/domain_randomization.md) - 域随机化
- [guides/custom_assets.md](guides/custom_assets.md) - 自定义资产加载
- [guides/mimic_datagen.md](guides/mimic_datagen.md) - 模仿学习数据生成
- [guides/curobo_integration.md](guides/curobo_integration.md) - cuRobo 集成
- [guides/rl_training.md](guides/rl_training.md) - RL 训练脚本

### 代码示例
- [examples/manager_based_env.py](examples/manager_based_env.py)
- [examples/direct_env.py](examples/direct_env.py)
