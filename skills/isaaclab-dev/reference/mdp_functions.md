# MDP 预定义函数参考

`isaaclab.envs.mdp` 模块提供了大量预定义的 MDP 组件函数。

```python
import isaaclab.envs.mdp as mdp
```

## Actions 动作

### 关节控制

```python
# 关节位置
mdp.JointPositionActionCfg(
    asset_name="robot",
    joint_names=["joint.*"],
    scale=1.0,
    use_default_offset=True
)

# 关节速度
mdp.JointVelocityActionCfg(
    asset_name="robot",
    joint_names=["joint.*"],
    scale=1.0
)

# 关节力矩
mdp.JointEffortActionCfg(
    asset_name="robot",
    joint_names=["joint.*"],
    scale=100.0
)

# 关节位置到限位
mdp.JointPositionToLimitsActionCfg(
    asset_name="robot",
    joint_names=["joint.*"],
    rescale_to_limits=True
)
```

### 末端控制

```python
from isaaclab.controllers.differential_ik_cfg import DifferentialIKControllerCfg

# 差分 IK
mdp.DifferentialInverseKinematicsActionCfg(
    asset_name="robot",
    joint_names=["panda_joint.*"],
    body_name="panda_hand",
    controller=DifferentialIKControllerCfg(
        command_type="pose",           # "position" | "pose"
        use_relative_mode=True,        # True: delta pose, False: absolute
        ik_method="dls"                # "pinv" | "svd" | "dls"
    ),
    scale=0.5,
    body_offset=mdp.DifferentialInverseKinematicsActionCfg.OffsetCfg(
        pos=[0.0, 0.0, 0.107]
    )
)
```

### 夹爪控制

```python
# 二值位置控制
mdp.BinaryJointPositionActionCfg(
    asset_name="robot",
    joint_names=["finger_joint.*"],
    open_command_expr={"finger_joint.*": 0.04},
    close_command_expr={"finger_joint.*": 0.0}
)

# 二值速度控制
mdp.BinaryJointVelocityActionCfg(...)
```

### 非完整约束

```python
# 差速驱动 (轮式机器人)
mdp.NonHolonomicActionCfg(
    asset_name="robot",
    body_name="base",
    x_scale=1.0,
    yaw_scale=1.0
)
```

## Observations 观测

### 关节状态

```python
mdp.joint_pos                    # 绝对关节位置
mdp.joint_pos_rel                # 相对关节位置 (减去默认值)
mdp.joint_vel                    # 关节速度
mdp.joint_vel_rel                # 相对关节速度
mdp.joint_pos_limit_normalized   # 归一化到关节限位
```

### 根/本体状态

```python
mdp.base_pos_z                   # 高度
mdp.base_lin_vel                 # 本体线速度
mdp.base_ang_vel                 # 本体角速度
mdp.projected_gravity            # 投影重力

mdp.root_pos_w                   # 世界坐标位置
mdp.root_quat_w                  # 世界坐标四元数
mdp.root_lin_vel_w               # 世界坐标线速度
mdp.root_ang_vel_w               # 世界坐标角速度
```

### Body 状态

```python
mdp.body_pose_w                  # body 位姿
mdp.body_projected_gravity_b     # body 投影重力
```

### 图像/传感器

```python
mdp.image                        # 相机图像
# params: sensor_cfg, data_type, normalize
```

### 动作

```python
mdp.last_action                  # 上一步动作
mdp.generated_commands           # 生成的命令
```

### 示例配置

```python
from isaaclab.managers import ObservationTermCfg as ObsTerm, SceneEntityCfg

ObsTerm(func=mdp.joint_pos_rel)

ObsTerm(
    func=mdp.root_pos_w,
    params={"asset_cfg": SceneEntityCfg("object")}
)

ObsTerm(
    func=mdp.image,
    params={
        "sensor_cfg": SceneEntityCfg("camera"),
        "data_type": "rgb",
        "normalize": False
    }
)
```

## Events 事件

### 关节重置

```python
mdp.reset_joints_by_offset       # 默认值 + 随机偏移
# params: asset_cfg, position_range, velocity_range

mdp.reset_joints_by_scale        # 默认值 * 随机缩放
# params: asset_cfg, position_range, velocity_range

mdp.reset_joints_within_limits_range  # 在限位范围内随机
# params: asset_cfg, position_range, velocity_range
```

### 根状态重置

```python
mdp.reset_root_state_uniform     # 均匀分布随机
# params: asset_cfg, pose_range, velocity_range

mdp.reset_root_state_with_random_orientation
# params: asset_cfg, pose_range, velocity_range, orientation_distribution
```

### 物理属性随机化

```python
mdp.randomize_rigid_body_mass    # 质量随机化
# params: asset_cfg, mass_distribution_params, operation

mdp.randomize_rigid_body_material  # 物理材质随机化
# params: asset_cfg, static_friction_range, dynamic_friction_range, 
#         restitution_range, num_buckets

mdp.randomize_actuator_gains     # 执行器增益随机化
# params: asset_cfg, stiffness_distribution_params, 
#         damping_distribution_params, operation
```

### 尺度随机化

```python
mdp.randomize_rigid_body_scale   # 尺度随机化 (启动时)
# params: asset_cfg, scale_range

# 注意: 只能在 mode="usd" 使用,仿真开始前执行
```

### 扰动

```python
mdp.push_by_setting_velocity     # 设置速度扰动
# params: asset_cfg, velocity_range

mdp.apply_external_force_torque  # 外力/力矩扰动
# params: asset_cfg, force_range, torque_range
```

### 示例配置

```python
from isaaclab.managers import EventTermCfg as EventTerm, SceneEntityCfg

# 启动时随机化质量
EventTerm(
    func=mdp.randomize_rigid_body_mass,
    mode="startup",
    params={
        "asset_cfg": SceneEntityCfg("object"),
        "mass_distribution_params": (0.5, 1.5),
        "operation": "scale"  # "scale" | "add" | "abs"
    }
)

# 重置时随机化关节
EventTerm(
    func=mdp.reset_joints_by_offset,
    mode="reset",
    params={
        "asset_cfg": SceneEntityCfg("robot"),
        "position_range": (-0.1, 0.1),
        "velocity_range": (0.0, 0.0)
    }
)

# 周期性扰动
EventTerm(
    func=mdp.push_by_setting_velocity,
    mode="interval",
    interval_range_s=(10.0, 15.0),
    params={
        "asset_cfg": SceneEntityCfg("robot"),
        "velocity_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5)}
    }
)
```

## Rewards 奖励

### 动作惩罚

```python
mdp.action_l2                    # 动作 L2 范数
mdp.action_rate_l2               # 动作变化率 L2
```

### 关节惩罚

```python
mdp.joint_vel_l2                 # 关节速度 L2
mdp.joint_acc_l2                 # 关节加速度 L2
mdp.joint_torques_l2             # 关节力矩 L2
mdp.joint_pos_limits             # 关节限位惩罚
mdp.joint_vel_limits             # 关节速度限位惩罚
```

### 终止

```python
mdp.is_terminated                # 终止惩罚
```

### 示例配置

```python
from isaaclab.managers import RewardTermCfg as RewTerm

RewTerm(func=mdp.action_rate_l2, weight=-0.01)
RewTerm(func=mdp.joint_vel_l2, weight=-0.0001)
RewTerm(func=mdp.is_terminated, weight=-10.0)
```

## Terminations 终止

```python
mdp.time_out                     # 超时
# 使用: DoneTerm(func=mdp.time_out, time_out=True)

mdp.root_height_below_minimum    # 高度低于阈值
# params: asset_cfg, minimum_height

mdp.illegal_contact              # 非法接触
# params: sensor_cfg, threshold

mdp.joint_pos_out_of_limit       # 关节超出限位
# params: asset_cfg

mdp.joint_pos_out_of_manual_limit  # 关节超出手动限位
# params: asset_cfg, lower_bounds, upper_bounds

mdp.joint_vel_out_of_limit       # 关节速度超限
# params: asset_cfg
```

### 示例配置

```python
from isaaclab.managers import TerminationTermCfg as DoneTerm, SceneEntityCfg

DoneTerm(func=mdp.time_out, time_out=True)

DoneTerm(
    func=mdp.root_height_below_minimum,
    params={
        "asset_cfg": SceneEntityCfg("object"),
        "minimum_height": -0.1
    }
)
```

## Commands 命令

用于生成目标位置、速度等命令。

```python
from isaaclab.envs.mdp.commands import (
    UniformPose2dCommandCfg,
    UniformPoseCommandCfg,
    UniformVelocityCommandCfg
)

# 2D 位姿命令 (x, y, yaw)
UniformPose2dCommandCfg(
    asset_name="robot",
    resampling_time_range=(5.0, 10.0),
    ranges=UniformPose2dCommandCfg.Ranges(
        pos_x=(-1.0, 1.0),
        pos_y=(-1.0, 1.0),
        heading=(-3.14, 3.14)
    )
)

# 3D 位姿命令
UniformPoseCommandCfg(
    asset_name="robot",
    body_name="ee_link",
    resampling_time_range=(5.0, 10.0),
    ranges=UniformPoseCommandCfg.Ranges(
        pos_x=(-0.1, 0.1),
        pos_y=(-0.1, 0.1),
        pos_z=(-0.1, 0.1),
        roll=(-0.1, 0.1),
        pitch=(-0.1, 0.1),
        yaw=(-0.1, 0.1)
    )
)

# 速度命令
UniformVelocityCommandCfg(
    asset_name="robot",
    resampling_time_range=(5.0, 10.0),
    ranges=UniformVelocityCommandCfg.Ranges(
        lin_vel_x=(-1.0, 1.0),
        lin_vel_y=(-1.0, 1.0),
        ang_vel_z=(-1.0, 1.0)
    )
)
```

## Curriculums 课程

```python
from isaaclab.envs.mdp.curriculums import modify_reward_weight

# 动态调整奖励权重
modify_reward_weight(
    env,
    env_ids,
    term_name="reward_name",
    weight=1.0,
    num_steps=1000
)
```
