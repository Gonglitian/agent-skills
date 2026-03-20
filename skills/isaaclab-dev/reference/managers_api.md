# Manager 系统 API 参考

## ActionManager

### 预定义 Action Terms

```python
import isaaclab.envs.mdp as mdp

# ═══════════════════════════════════════════════════════════════════
# 关节位置控制
# ═══════════════════════════════════════════════════════════════════
mdp.JointPositionActionCfg(
    asset_name="robot",                    # 场景中的资产名
    joint_names=["joint.*"],               # 关节名正则
    scale=1.0,                             # 动作缩放
    use_default_offset=True,               # 是否使用默认位置作为偏移
    preserve_order=False                   # 是否保持关节顺序
)

# ═══════════════════════════════════════════════════════════════════
# 关节速度控制
# ═══════════════════════════════════════════════════════════════════
mdp.JointVelocityActionCfg(
    asset_name="robot",
    joint_names=["joint.*"],
    scale=1.0,
    use_default_offset=False
)

# ═══════════════════════════════════════════════════════════════════
# 关节力矩控制
# ═══════════════════════════════════════════════════════════════════
mdp.JointEffortActionCfg(
    asset_name="robot",
    joint_names=["joint.*"],
    scale=100.0  # 力矩通常需要较大缩放
)

# ═══════════════════════════════════════════════════════════════════
# 差分逆运动学控制 (末端位姿)
# ═══════════════════════════════════════════════════════════════════
from isaaclab.controllers.differential_ik_cfg import DifferentialIKControllerCfg

mdp.DifferentialInverseKinematicsActionCfg(
    asset_name="robot",
    joint_names=["panda_joint.*"],         # 控制的关节
    body_name="panda_hand",                # 末端执行器 body
    controller=DifferentialIKControllerCfg(
        command_type="pose",               # "position" | "pose"
        use_relative_mode=True,            # True: 相对位姿, False: 绝对位姿
        ik_method="dls",                   # "pinv" | "svd" | "dls"
        ik_params={"lambda_val": 0.01}     # DLS 正则化参数
    ),
    scale=0.5,                             # 动作缩放 (相对模式下很重要)
    body_offset=mdp.DifferentialInverseKinematicsActionCfg.OffsetCfg(
        pos=[0.0, 0.0, 0.107],            # TCP 相对于 body 的偏移
        rot=[1.0, 0.0, 0.0, 0.0]
    )
)

# ═══════════════════════════════════════════════════════════════════
# 二值关节控制 (夹爪)
# ═══════════════════════════════════════════════════════════════════
mdp.BinaryJointPositionActionCfg(
    asset_name="robot",
    joint_names=["panda_finger_joint.*"],
    open_command_expr={"panda_finger_joint.*": 0.04},   # 打开位置
    close_command_expr={"panda_finger_joint.*": 0.0}   # 关闭位置
)

# 单关节版本 (如 Robotiq)
mdp.BinaryJointVelocityActionCfg(
    asset_name="robot",
    joint_names=["finger_joint"],
    open_command_expr={"finger_joint": 0.8},
    close_command_expr={"finger_joint": 0.0}
)
```

### 自定义 Action Term

```python
from isaaclab.managers import ActionTerm, ActionTermCfg
from isaaclab.envs import ManagerBasedEnv

class MyCustomAction(ActionTerm):
    """自定义动作项"""
    
    cfg: "MyCustomActionCfg"
    
    def __init__(self, cfg: "MyCustomActionCfg", env: ManagerBasedEnv):
        super().__init__(cfg, env)
        # 初始化...
        self._asset = env.scene[cfg.asset_name]
    
    @property
    def action_dim(self) -> int:
        """动作维度"""
        return self._num_actions
    
    @property
    def raw_actions(self) -> torch.Tensor:
        """原始动作 (未处理)"""
        return self._raw_actions
    
    @property
    def processed_actions(self) -> torch.Tensor:
        """处理后的动作"""
        return self._processed_actions
    
    def process_actions(self, actions: torch.Tensor):
        """处理动作 (每步调用一次)"""
        self._raw_actions = actions
        self._processed_actions = actions * self.cfg.scale
    
    def apply_actions(self):
        """应用动作到仿真"""
        self._asset.set_joint_position_target(self._processed_actions)


@configclass
class MyCustomActionCfg(ActionTermCfg):
    """自定义动作配置"""
    class_type: type = MyCustomAction
    asset_name: str = "robot"
    scale: float = 1.0
```

## ObservationManager

### 预定义 Observation Terms

```python
import isaaclab.envs.mdp as mdp
from isaaclab.managers import ObservationTermCfg as ObsTerm, SceneEntityCfg

# ═══════════════════════════════════════════════════════════════════
# 关节状态
# ═══════════════════════════════════════════════════════════════════
ObsTerm(func=mdp.joint_pos)                # 绝对关节位置
ObsTerm(func=mdp.joint_pos_rel)            # 相对关节位置 (减去默认值)
ObsTerm(func=mdp.joint_vel)                # 关节速度
ObsTerm(func=mdp.joint_vel_rel)            # 相对关节速度

# 指定特定关节
ObsTerm(
    func=mdp.joint_pos,
    params={"asset_cfg": SceneEntityCfg("robot", joint_names=["joint1", "joint2"])}
)

# ═══════════════════════════════════════════════════════════════════
# 根/本体状态
# ═══════════════════════════════════════════════════════════════════
ObsTerm(func=mdp.root_pos_w)               # 世界坐标位置 (相对于环境原点)
ObsTerm(func=mdp.root_quat_w)              # 世界坐标四元数 (wxyz)
ObsTerm(func=mdp.root_lin_vel_w)           # 世界坐标线速度
ObsTerm(func=mdp.root_ang_vel_w)           # 世界坐标角速度
ObsTerm(func=mdp.base_lin_vel)             # 本体坐标线速度
ObsTerm(func=mdp.base_ang_vel)             # 本体坐标角速度
ObsTerm(func=mdp.base_pos_z)               # 高度
ObsTerm(func=mdp.projected_gravity)        # 投影重力向量

# 指定资产
ObsTerm(func=mdp.root_pos_w, params={"asset_cfg": SceneEntityCfg("object")})

# ═══════════════════════════════════════════════════════════════════
# Body 状态
# ═══════════════════════════════════════════════════════════════════
ObsTerm(
    func=mdp.body_pose_w,
    params={"asset_cfg": SceneEntityCfg("robot", body_names=["panda_hand"])}
)

# ═══════════════════════════════════════════════════════════════════
# 动作
# ═══════════════════════════════════════════════════════════════════
ObsTerm(func=mdp.last_action)              # 上一步动作

# ═══════════════════════════════════════════════════════════════════
# 图像
# ═══════════════════════════════════════════════════════════════════
ObsTerm(
    func=mdp.image,
    params={
        "sensor_cfg": SceneEntityCfg("camera"),
        "data_type": "rgb",                # "rgb" | "depth" | "distance_to_image_plane"
        "normalize": False                 # 是否归一化到 [0, 1]
    }
)
```

### ObservationGroupCfg 配置

```python
from isaaclab.managers import ObservationGroupCfg as ObsGroup

@configclass
class PolicyCfg(ObsGroup):
    """策略观测组"""
    
    # 观测项
    joint_pos = ObsTerm(func=mdp.joint_pos_rel)
    joint_vel = ObsTerm(func=mdp.joint_vel_rel)
    
    def __post_init__(self):
        # 是否启用噪声
        self.enable_corruption = False
        
        # 是否拼接所有观测为单一张量
        self.concatenate_terms = True
        
        # 历史长度 (>1 时堆叠历史观测)
        # self.history_length = 1

@configclass
class ObservationsCfg:
    """观测配置"""
    policy: PolicyCfg = PolicyCfg()
    
    # 可以有多个组
    # critic: CriticCfg = CriticCfg()  # 用于 asymmetric actor-critic
```

### 自定义 Observation Term

```python
from isaaclab.managers import ObservationTermCfg
from isaaclab.envs import ManagerBasedEnv

def my_custom_observation(
    env: ManagerBasedEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")
) -> torch.Tensor:
    """自定义观测函数"""
    asset = env.scene[asset_cfg.name]
    
    # 计算观测
    obs = asset.data.root_pos_w - env.scene.env_origins
    
    return obs  # shape: (num_envs, obs_dim)


# 使用
ObsTerm(
    func=my_custom_observation,
    params={"asset_cfg": SceneEntityCfg("object")}
)
```

## EventManager

### Event 模式

| 模式 | 触发时机 | 用途 |
|------|----------|------|
| `startup` | 仿真启动前 | 一次性随机化 (质量、惯性等) |
| `reset` | Episode 重置时 | 状态随机化 |
| `interval` | 周期性 | 扰动 (推力等) |

### 预定义 Event Terms

```python
import isaaclab.envs.mdp as mdp
from isaaclab.managers import EventTermCfg as EventTerm, SceneEntityCfg

# ═══════════════════════════════════════════════════════════════════
# 重置关节状态
# ═══════════════════════════════════════════════════════════════════
EventTerm(
    func=mdp.reset_joints_by_offset,
    mode="reset",
    params={
        "asset_cfg": SceneEntityCfg("robot"),
        "position_range": (-0.1, 0.1),      # 位置随机范围
        "velocity_range": (-0.1, 0.1)       # 速度随机范围
    }
)

EventTerm(
    func=mdp.reset_joints_by_scale,
    mode="reset",
    params={
        "asset_cfg": SceneEntityCfg("robot"),
        "position_range": (0.9, 1.1),       # 位置缩放范围
        "velocity_range": (0.0, 0.0)
    }
)

# ═══════════════════════════════════════════════════════════════════
# 重置根状态 (物体位姿)
# ═══════════════════════════════════════════════════════════════════
EventTerm(
    func=mdp.reset_root_state_uniform,
    mode="reset",
    params={
        "asset_cfg": SceneEntityCfg("object"),
        "pose_range": {
            "x": (-0.1, 0.1),
            "y": (-0.1, 0.1),
            "z": (0.0, 0.0),
            "roll": (-0.1, 0.1),
            "pitch": (-0.1, 0.1),
            "yaw": (-3.14, 3.14)
        },
        "velocity_range": {
            "x": (-0.1, 0.1),
            "y": (-0.1, 0.1),
            "z": (0.0, 0.0)
        }
    }
)

# ═══════════════════════════════════════════════════════════════════
# 质量随机化
# ═══════════════════════════════════════════════════════════════════
EventTerm(
    func=mdp.randomize_rigid_body_mass,
    mode="startup",                         # 只在启动时执行一次
    params={
        "asset_cfg": SceneEntityCfg("object"),
        "mass_distribution_params": (0.5, 1.5),  # 范围
        "operation": "scale"                # "scale" | "add" | "abs"
    }
)

# ═══════════════════════════════════════════════════════════════════
# 物理材质随机化
# ═══════════════════════════════════════════════════════════════════
EventTerm(
    func=mdp.randomize_rigid_body_material,
    mode="startup",
    params={
        "asset_cfg": SceneEntityCfg("object"),
        "static_friction_range": (0.4, 1.0),
        "dynamic_friction_range": (0.4, 1.0),
        "restitution_range": (0.0, 0.1),
        "num_buckets": 64
    }
)

# ═══════════════════════════════════════════════════════════════════
# 周期性扰动
# ═══════════════════════════════════════════════════════════════════
EventTerm(
    func=mdp.push_by_setting_velocity,
    mode="interval",
    interval_range_s=(10.0, 15.0),          # 触发间隔 (秒)
    params={
        "asset_cfg": SceneEntityCfg("robot"),
        "velocity_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5)}
    }
)

EventTerm(
    func=mdp.apply_external_force_torque,
    mode="interval",
    interval_range_s=(5.0, 10.0),
    params={
        "asset_cfg": SceneEntityCfg("robot", body_names=["base"]),
        "force_range": {"x": (-10, 10), "y": (-10, 10)},
        "torque_range": {}
    }
)
```

## RewardManager

### 预定义 Reward Terms

```python
import isaaclab.envs.mdp as mdp
from isaaclab.managers import RewardTermCfg as RewTerm, SceneEntityCfg

# ═══════════════════════════════════════════════════════════════════
# 动作惩罚
# ═══════════════════════════════════════════════════════════════════
RewTerm(func=mdp.action_l2, weight=-0.01)           # L2 范数
RewTerm(func=mdp.action_rate_l2, weight=-0.01)      # 动作变化率 L2

# ═══════════════════════════════════════════════════════════════════
# 关节惩罚
# ═══════════════════════════════════════════════════════════════════
RewTerm(func=mdp.joint_vel_l2, weight=-0.0001)      # 关节速度 L2
RewTerm(func=mdp.joint_acc_l2, weight=-0.00001)     # 关节加速度 L2
RewTerm(func=mdp.joint_torques_l2, weight=-0.0001)  # 关节力矩 L2
RewTerm(
    func=mdp.joint_pos_limits,                      # 关节限位惩罚
    weight=-1.0,
    params={"asset_cfg": SceneEntityCfg("robot")}
)

# ═══════════════════════════════════════════════════════════════════
# 终止惩罚
# ═══════════════════════════════════════════════════════════════════
RewTerm(func=mdp.is_terminated, weight=-10.0)
```

## TerminationManager

### 预定义 Termination Terms

```python
import isaaclab.envs.mdp as mdp
from isaaclab.managers import TerminationTermCfg as DoneTerm, SceneEntityCfg

# 超时
DoneTerm(func=mdp.time_out, time_out=True)

# 高度检查
DoneTerm(
    func=mdp.root_height_below_minimum,
    params={
        "asset_cfg": SceneEntityCfg("object"),
        "minimum_height": -0.1
    }
)

# 非法接触
DoneTerm(
    func=mdp.illegal_contact,
    params={
        "sensor_cfg": SceneEntityCfg("contact_forces"),
        "threshold": 1.0
    }
)
```

## SceneEntityCfg

用于在 Manager Term 中引用场景实体。

```python
from isaaclab.managers import SceneEntityCfg

# 基本用法 - 引用整个资产
SceneEntityCfg("robot")
SceneEntityCfg("object")

# 指定特定关节
SceneEntityCfg("robot", joint_names=["joint1", "joint2", "joint3"])
SceneEntityCfg("robot", joint_names=["panda_joint.*"])  # 正则表达式

# 指定特定 body
SceneEntityCfg("robot", body_names=["panda_hand"])
SceneEntityCfg("robot", body_names=["link.*"])

# 同时指定
SceneEntityCfg(
    "robot",
    joint_names=["panda_joint.*"],
    body_names=["panda_hand"]
)
```
