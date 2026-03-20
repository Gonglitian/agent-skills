# 域随机化指南

域随机化 (Domain Randomization) 通过在仿真中引入变化来提高策略的 sim-to-real 迁移能力。

## Event 模式

| 模式 | 触发时机 | 典型用途 |
|------|----------|----------|
| `startup` | 仿真开始前 (一次) | 质量、惯性、执行器增益 |
| `usd` | USD stage 设置时 | 尺度、几何形状 |
| `reset` | Episode 重置时 | 初始状态、位姿 |
| `interval` | 周期性 (训练中) | 外部扰动 |

## 物理属性随机化

### 质量随机化

```python
from isaaclab.managers import EventTermCfg as EventTerm, SceneEntityCfg
import isaaclab.envs.mdp as mdp

@configclass
class EventsCfg:
    # 缩放质量 (0.5x ~ 1.5x)
    randomize_object_mass = EventTerm(
        func=mdp.randomize_rigid_body_mass,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("object"),
            "mass_distribution_params": (0.5, 1.5),
            "operation": "scale"  # "scale" | "add" | "abs"
        }
    )
    
    # 添加质量 (-0.1 ~ 0.1 kg)
    add_mass_variation = EventTerm(
        func=mdp.randomize_rigid_body_mass,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("object"),
            "mass_distribution_params": (-0.1, 0.1),
            "operation": "add"
        }
    )
```

### 摩擦力随机化

```python
randomize_friction = EventTerm(
    func=mdp.randomize_rigid_body_material,
    mode="startup",
    params={
        "asset_cfg": SceneEntityCfg("object"),
        "static_friction_range": (0.4, 1.0),
        "dynamic_friction_range": (0.4, 1.0),
        "restitution_range": (0.0, 0.1),
        "num_buckets": 64,           # 材质桶数量
        "make_consistent": True      # 确保动摩擦 <= 静摩擦
    }
)
```

### 执行器增益随机化

```python
randomize_actuator_gains = EventTerm(
    func=mdp.randomize_actuator_gains,
    mode="startup",
    params={
        "asset_cfg": SceneEntityCfg("robot"),
        "stiffness_distribution_params": (0.8, 1.2),
        "damping_distribution_params": (0.8, 1.2),
        "operation": "scale"
    }
)
```

## 初始状态随机化

### 关节状态

```python
# 偏移模式 (默认值 + 随机偏移)
reset_robot_joints = EventTerm(
    func=mdp.reset_joints_by_offset,
    mode="reset",
    params={
        "asset_cfg": SceneEntityCfg("robot"),
        "position_range": (-0.1, 0.1),   # 弧度
        "velocity_range": (-0.1, 0.1)    # rad/s
    }
)

# 缩放模式 (默认值 * 随机系数)
reset_robot_joints_scaled = EventTerm(
    func=mdp.reset_joints_by_scale,
    mode="reset",
    params={
        "asset_cfg": SceneEntityCfg("robot"),
        "position_range": (0.9, 1.1),
        "velocity_range": (0.0, 0.0)
    }
)

# 限位范围内随机
reset_joints_in_limits = EventTerm(
    func=mdp.reset_joints_within_limits_range,
    mode="reset",
    params={
        "asset_cfg": SceneEntityCfg("robot"),
        "position_range": (0.1, 0.9),    # 限位的 10%-90%
        "velocity_range": (0.0, 0.0)
    }
)
```

### 物体位姿

```python
reset_object_pose = EventTerm(
    func=mdp.reset_root_state_uniform,
    mode="reset",
    params={
        "asset_cfg": SceneEntityCfg("object"),
        "pose_range": {
            "x": (-0.1, 0.1),        # 位置范围
            "y": (-0.1, 0.1),
            "z": (0.0, 0.0),
            "roll": (-0.1, 0.1),     # 姿态范围 (弧度)
            "pitch": (-0.1, 0.1),
            "yaw": (-3.14, 3.14)     # 完整旋转
        },
        "velocity_range": {
            "x": (0.0, 0.0),
            "y": (0.0, 0.0),
            "z": (0.0, 0.0),
            "roll": (0.0, 0.0),
            "pitch": (0.0, 0.0),
            "yaw": (0.0, 0.0)
        }
    }
)

# 随机朝向
reset_with_random_orientation = EventTerm(
    func=mdp.reset_root_state_with_random_orientation,
    mode="reset",
    params={
        "asset_cfg": SceneEntityCfg("object"),
        "pose_range": {"x": (-0.1, 0.1), "y": (-0.1, 0.1)},
        "velocity_range": {}
    }
)
```

## 外部扰动

### 速度扰动

```python
push_robot = EventTerm(
    func=mdp.push_by_setting_velocity,
    mode="interval",
    interval_range_s=(10.0, 15.0),   # 每 10-15 秒触发
    params={
        "asset_cfg": SceneEntityCfg("robot"),
        "velocity_range": {
            "x": (-0.5, 0.5),
            "y": (-0.5, 0.5),
            "z": (0.0, 0.0)
        }
    }
)
```

### 外力扰动

```python
apply_external_force = EventTerm(
    func=mdp.apply_external_force_torque,
    mode="interval",
    interval_range_s=(5.0, 10.0),
    params={
        "asset_cfg": SceneEntityCfg("robot", body_names=["base"]),
        "force_range": {
            "x": (-10.0, 10.0),
            "y": (-10.0, 10.0),
            "z": (0.0, 0.0)
        },
        "torque_range": {
            "x": (0.0, 0.0),
            "y": (0.0, 0.0),
            "z": (-5.0, 5.0)
        }
    }
)
```

## 视觉随机化

### 灯光随机化

```python
# 自定义灯光随机化函数
def randomize_scene_lighting(
    env,
    env_ids,
    intensity_range: tuple,
    color_variation: float
):
    """随机化场景灯光"""
    import omni.usd
    from pxr import UsdLux
    
    stage = omni.usd.get_context().get_stage()
    light_prim = stage.GetPrimAtPath("/World/Light")
    
    if light_prim.IsValid():
        light = UsdLux.DomeLight(light_prim)
        
        # 随机强度
        intensity = torch.rand(1).item() * (intensity_range[1] - intensity_range[0]) + intensity_range[0]
        light.GetIntensityAttr().Set(intensity)
        
        # 随机颜色偏移
        base_color = (0.75, 0.75, 0.75)
        color = tuple(
            max(0, min(1, c + (torch.rand(1).item() - 0.5) * 2 * color_variation))
            for c in base_color
        )
        light.GetColorAttr().Set(color)

randomize_lighting = EventTerm(
    func=randomize_scene_lighting,
    mode="reset",
    params={
        "intensity_range": (1000.0, 5000.0),
        "color_variation": 0.2
    }
)
```

### 纹理随机化

```python
# 需要自定义实现
def randomize_texture(env, env_ids, asset_cfg, textures):
    """随机化材质纹理"""
    # 实现纹理切换逻辑
    pass
```

## 尺度随机化

⚠️ 尺度随机化只能在 `mode="usd"` 使用 (仿真开始前)。

```python
randomize_scale = EventTerm(
    func=mdp.randomize_rigid_body_scale,
    mode="usd",  # 特殊模式
    params={
        "asset_cfg": SceneEntityCfg("object"),
        "scale_range": (0.8, 1.2)  # 80% ~ 120%
    }
)
```

需要设置 `replicate_physics=False`:

```python
scene_cfg = MySceneCfg(
    num_envs=1024,
    replicate_physics=False  # 必须为 False
)
```

## 噪声注入

### 观测噪声

```python
@configclass
class PolicyCfg(ObsGroup):
    joint_pos = ObsTerm(
        func=mdp.joint_pos_rel,
        noise=GaussianNoiseCfg(mean=0.0, std=0.01)  # 添加噪声
    )
    
    def __post_init__(self):
        self.enable_corruption = True  # 启用噪声
```

### 动作噪声

```python
arm_action = mdp.JointPositionActionCfg(
    asset_name="robot",
    joint_names=["joint.*"],
    scale=1.0,
    noise=GaussianNoiseCfg(mean=0.0, std=0.01)
)
```

## 最佳实践

### 1. 渐进式增加随机化

```python
# 从小范围开始
position_range = (-0.01, 0.01)  # 初始
# 逐步增加
position_range = (-0.1, 0.1)   # 最终
```

### 2. 分层随机化策略

```python
# Level 1: 基础随机化
basic_randomization = [
    reset_joints,
    reset_object_pose
]

# Level 2: 添加物理随机化
physics_randomization = [
    randomize_mass,
    randomize_friction
]

# Level 3: 添加扰动
disturbance_randomization = [
    push_robot,
    apply_external_force
]
```

### 3. 监控随机化效果

- 记录随机化参数
- 分析不同随机化对性能的影响
- 确保策略在所有变化范围内都能工作
