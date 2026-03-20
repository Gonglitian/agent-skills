# 资产系统 API 参考

## 资产类型概览

| 类型 | 用途 | 特性 |
|------|------|------|
| `Articulation` | 机器人、多关节物体 | 关节控制、执行器建模 |
| `RigidObject` | 可交互刚体 | 位姿控制、碰撞检测 |
| `DeformableObject` | 柔性物体 | 节点级变形 |
| `AssetBase` | 静态物体 | 仅视觉/碰撞,无物理交互 |
| `RigidObjectCollection` | 多刚体集合 | 批量管理相似物体 |

## Articulation (机器人)

### 配置

```python
from isaaclab.assets import ArticulationCfg
from isaaclab.actuators import ImplicitActuatorCfg
import isaaclab.sim as sim_utils

robot_cfg = ArticulationCfg(
    prim_path="{ENV_REGEX_NS}/Robot",
    
    # 生成配置 (从文件加载)
    spawn=sim_utils.UsdFileCfg(
        usd_path="path/to/robot.usd",
        activate_contact_sensors=True,  # 启用接触传感器
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=10.0
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=8,
            solver_velocity_iteration_count=0
        )
    ),
    
    # 初始状态
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.0),
        rot=(1.0, 0.0, 0.0, 0.0),  # wxyz
        joint_pos={
            "panda_joint1": 0.0,
            "panda_joint2": -0.785,
            "panda_joint3": 0.0,
            "panda_joint4": -2.356,
            "panda_joint5": 0.0,
            "panda_joint6": 1.571,
            "panda_joint7": 0.785,
            "panda_finger_joint.*": 0.04
        },
        joint_vel={".*": 0.0}
    ),
    
    # 执行器配置
    actuators={
        "arm": ImplicitActuatorCfg(
            joint_names_expr=["panda_joint.*"],
            stiffness=400.0,
            damping=80.0,
            velocity_limit=100.0,
            effort_limit=87.0
        ),
        "gripper": ImplicitActuatorCfg(
            joint_names_expr=["panda_finger_joint.*"],
            stiffness=2000.0,
            damping=100.0
        )
    },
    
    # 软关节限位 (可选)
    soft_joint_pos_limit_factor=0.95
)
```

### 运行时 API

```python
# 访问
robot: Articulation = env.scene["robot"]

# ═══════════════════════════════════════════════════════════════════
# 数据属性 (只读)
# ═══════════════════════════════════════════════════════════════════
robot.data.root_pos_w          # (num_envs, 3) 根位置
robot.data.root_quat_w         # (num_envs, 4) 根四元数 (wxyz)
robot.data.root_vel_w          # (num_envs, 6) 根速度 [lin, ang]
robot.data.root_lin_vel_w      # (num_envs, 3) 根线速度
robot.data.root_ang_vel_w      # (num_envs, 3) 根角速度
robot.data.root_lin_vel_b      # (num_envs, 3) 本体坐标线速度
robot.data.root_ang_vel_b      # (num_envs, 3) 本体坐标角速度

robot.data.joint_pos           # (num_envs, num_joints) 关节位置
robot.data.joint_vel           # (num_envs, num_joints) 关节速度
robot.data.joint_acc           # (num_envs, num_joints) 关节加速度

robot.data.body_pos_w          # (num_envs, num_bodies, 3) body 位置
robot.data.body_quat_w         # (num_envs, num_bodies, 4) body 四元数
robot.data.body_vel_w          # (num_envs, num_bodies, 6) body 速度

robot.data.default_root_state  # (num_envs, 13) 默认根状态
robot.data.default_joint_pos   # (num_envs, num_joints) 默认关节位置
robot.data.default_joint_vel   # (num_envs, num_joints) 默认关节速度

robot.data.joint_names         # List[str] 关节名列表
robot.data.body_names          # List[str] body 名列表

# ═══════════════════════════════════════════════════════════════════
# 写入方法
# ═══════════════════════════════════════════════════════════════════

# 写入根位姿
robot.write_root_pose_to_sim(
    root_pose,                 # (num_envs, 7) [pos, quat]
    env_ids=None               # 可选,指定环境索引
)

# 写入根速度
robot.write_root_velocity_to_sim(
    root_velocity,             # (num_envs, 6) [lin_vel, ang_vel]
    env_ids=None
)

# 写入关节状态
robot.write_joint_state_to_sim(
    joint_pos,                 # (num_envs, num_joints)
    joint_vel,                 # (num_envs, num_joints)
    joint_ids=None,            # 可选,指定关节索引
    env_ids=None
)

# ═══════════════════════════════════════════════════════════════════
# 控制方法 (设置目标,需调用 write_data_to_sim 应用)
# ═══════════════════════════════════════════════════════════════════

# 位置控制
robot.set_joint_position_target(
    target,                    # (num_envs, num_joints)
    joint_ids=None,
    env_ids=None
)

# 速度控制
robot.set_joint_velocity_target(target, joint_ids=None, env_ids=None)

# 力矩控制
robot.set_joint_effort_target(target, joint_ids=None, env_ids=None)

# 应用到仿真
robot.write_data_to_sim()

# ═══════════════════════════════════════════════════════════════════
# 工具方法
# ═══════════════════════════════════════════════════════════════════

# 查找关节
joint_ids, joint_names = robot.find_joints("panda_joint.*")
joint_ids, joint_names = robot.find_joints(["joint1", "joint2"])

# 查找 body
body_ids, body_names = robot.find_bodies("panda_hand")

# 重置
robot.reset(env_ids=None)

# 更新 (通常由 scene.update 调用)
robot.update(dt)
```

## RigidObject (可操作物体)

### 配置

```python
from isaaclab.assets import RigidObjectCfg
import isaaclab.sim as sim_utils

object_cfg = RigidObjectCfg(
    prim_path="{ENV_REGEX_NS}/Object",
    
    spawn=sim_utils.UsdFileCfg(
        usd_path="path/to/object.usd",
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=10.0
        ),
        mass_props=sim_utils.MassPropertiesCfg(mass=0.1),
        collision_props=sim_utils.CollisionPropertiesCfg()
    ),
    
    init_state=RigidObjectCfg.InitialStateCfg(
        pos=(0.5, 0.0, 0.1),
        rot=(1.0, 0.0, 0.0, 0.0),
        lin_vel=(0.0, 0.0, 0.0),
        ang_vel=(0.0, 0.0, 0.0)
    )
)
```

### 运行时 API

```python
obj: RigidObject = env.scene["object"]

# 数据属性
obj.data.root_pos_w           # (num_envs, 3)
obj.data.root_quat_w          # (num_envs, 4)
obj.data.root_vel_w           # (num_envs, 6)
obj.data.root_pose_w          # (num_envs, 7) [pos, quat]
obj.data.root_state_w         # (num_envs, 13) [pos, quat, lin_vel, ang_vel]

obj.data.default_root_state   # (num_envs, 13)

# 写入方法
obj.write_root_pose_to_sim(root_pose, env_ids=None)
obj.write_root_velocity_to_sim(root_velocity, env_ids=None)
obj.write_root_state_to_sim(root_state, env_ids=None)

# 重置
obj.reset(env_ids=None)
```

## AssetBase (静态物体)

用于不需要物理交互的物体,如桌子、背景等。

```python
from isaaclab.assets import AssetBaseCfg
import isaaclab.sim as sim_utils

table_cfg = AssetBaseCfg(
    prim_path="{ENV_REGEX_NS}/Table",
    spawn=sim_utils.UsdFileCfg(usd_path="path/to/table.usd"),
    init_state=AssetBaseCfg.InitialStateCfg(
        pos=(0.5, 0.0, 0.0),
        rot=(0.707, 0, 0, 0.707)
    ),
    collision_group=-1  # -1 表示全局碰撞组 (与所有环境碰撞)
)
```

## 预定义机器人配置

```python
# Franka Panda
from isaaclab_assets.robots.franka import (
    FRANKA_PANDA_CFG,           # 标准配置
    FRANKA_PANDA_HIGH_PD_CFG    # 高刚度 PD 控制
)

# UR 系列
from isaaclab_assets.robots.ur import UR10_CFG

# Anymal
from isaaclab_assets.robots.anymal import ANYMAL_C_CFG, ANYMAL_D_CFG

# Unitree
from isaaclab_assets.robots.unitree import (
    UNITREE_GO1_CFG,
    UNITREE_GO2_CFG,
    UNITREE_H1_CFG,
    UNITREE_G1_CFG
)

# 使用方式
robot_cfg = FRANKA_PANDA_HIGH_PD_CFG.replace(
    prim_path="{ENV_REGEX_NS}/Robot"
)
```

## 执行器配置

```python
from isaaclab.actuators import (
    ImplicitActuatorCfg,       # 隐式 PD 控制器
    IdealPDActuatorCfg,        # 理想 PD 控制器
    DCMotorCfg,                # DC 电机模型
    ActuatorNetMLPCfg,         # 神经网络执行器
)

# 隐式执行器 (使用 PhysX 内置 PD)
ImplicitActuatorCfg(
    joint_names_expr=["joint.*"],
    stiffness=100.0,           # kp
    damping=10.0,              # kd
    velocity_limit=10.0,       # 最大速度
    effort_limit=50.0          # 最大力矩
)

# 理想 PD 执行器 (自定义 PD 计算)
IdealPDActuatorCfg(
    joint_names_expr=["joint.*"],
    stiffness={"joint.*": 100.0},
    damping={"joint.*": 10.0}
)

# DC 电机模型
DCMotorCfg(
    joint_names_expr=["joint.*"],
    saturation_effort=100.0,
    motor_constant=0.1,
    winding_resistance=0.1,
    gear_ratio=10.0
)
```
