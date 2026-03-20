# Spawners API 参考

Spawners 用于在 USD 场景中创建 prims。

## 导入

```python
import isaaclab.sim as sim_utils
```

## 从文件加载

```python
# USD 文件
sim_utils.UsdFileCfg(
    usd_path="path/to/asset.usd",
    
    # 物理属性
    rigid_props=sim_utils.RigidBodyPropertiesCfg(
        disable_gravity=False,
        max_depenetration_velocity=10.0,
        enable_gyroscopic_forces=True
    ),
    
    # 质量属性
    mass_props=sim_utils.MassPropertiesCfg(
        mass=1.0,
        density=None  # 如果设置,优先使用密度计算质量
    ),
    
    # 碰撞属性
    collision_props=sim_utils.CollisionPropertiesCfg(
        collision_enabled=True,
        contact_offset=0.005,
        rest_offset=0.0
    ),
    
    # Articulation 属性 (机器人)
    articulation_props=sim_utils.ArticulationRootPropertiesCfg(
        enabled_self_collisions=False,
        solver_position_iteration_count=8,
        solver_velocity_iteration_count=0
    ),
    
    # 激活接触传感器
    activate_contact_sensors=False,
    
    # 语义标签 (用于分割)
    semantic_tags=[("class", "robot"), ("type", "arm")]
)

# URDF 文件
sim_utils.UrdfFileCfg(
    asset_path="path/to/robot.urdf",
    fix_base=True,
    ...
)
```

## 基本形状

```python
# 长方体
sim_utils.CuboidCfg(
    size=(0.1, 0.1, 0.1),              # (x, y, z)
    
    # 可视属性
    visual_material=sim_utils.PreviewSurfaceCfg(
        diffuse_color=(0.8, 0.2, 0.2)
    ),
    
    # 物理属性
    rigid_props=sim_utils.RigidBodyPropertiesCfg(...),
    mass_props=sim_utils.MassPropertiesCfg(mass=0.1),
    collision_props=sim_utils.CollisionPropertiesCfg()
)

# 球体
sim_utils.SphereCfg(
    radius=0.05,
    visual_material=...,
    rigid_props=...,
    mass_props=...,
    collision_props=...
)

# 圆柱体
sim_utils.CylinderCfg(
    radius=0.05,
    height=0.1,
    axis="Z",  # 轴向: "X" | "Y" | "Z"
    ...
)

# 圆锥
sim_utils.ConeCfg(
    radius=0.05,
    height=0.1,
    axis="Z",
    ...
)

# 胶囊
sim_utils.CapsuleCfg(
    radius=0.05,
    height=0.1,
    axis="Z",
    ...
)
```

## 地面

```python
# 无限平面
sim_utils.GroundPlaneCfg(
    size=(100.0, 100.0),
    
    # 物理材质
    physics_material=sim_utils.RigidBodyMaterialCfg(
        static_friction=0.5,
        dynamic_friction=0.5,
        restitution=0.0
    ),
    
    # 可视材质
    visual_material=sim_utils.PreviewSurfaceCfg(
        diffuse_color=(0.4, 0.4, 0.4)
    ),
    
    color=(0.4, 0.4, 0.4)  # 简化颜色设置
)
```

## 灯光

```python
# 穹顶光 (环境光)
sim_utils.DomeLightCfg(
    intensity=3000.0,
    color=(0.75, 0.75, 0.75),
    
    # HDR 纹理 (可选)
    texture_file="path/to/hdri.hdr",
    
    # 色温模式
    enable_color_temperature=False,
    color_temperature=6500
)

# 平行光 (太阳光)
sim_utils.DistantLightCfg(
    intensity=3000.0,
    color=(1.0, 1.0, 1.0),
    
    # 方向由 prim 朝向决定
)

# 圆盘光
sim_utils.DiskLightCfg(
    intensity=1000.0,
    radius=0.1,
    color=(1.0, 1.0, 1.0)
)

# 球光
sim_utils.SphereLightCfg(
    intensity=1000.0,
    radius=0.1,
    color=(1.0, 1.0, 1.0)
)

# 圆柱光
sim_utils.CylinderLightCfg(
    intensity=1000.0,
    radius=0.05,
    length=0.5
)
```

## 相机

```python
# 针孔相机
sim_utils.PinholeCameraCfg(
    focal_length=24.0,              # 焦距 (mm)
    focus_distance=400.0,           # 对焦距离
    horizontal_aperture=20.955,     # 水平光圈 (mm),影响视场角
    vertical_aperture=None,         # 自动计算
    clipping_range=(0.1, 10.0),     # (near, far) 裁剪
    
    # 鱼眼/畸变参数
    f_stop=0.0,
    lock_camera=True
)

# 或使用焦距快捷设置
sim_utils.FisheyeCameraCfg(...)
```

## 材质

### 物理材质

```python
# 刚体材质
sim_utils.RigidBodyMaterialCfg(
    static_friction=0.5,
    dynamic_friction=0.5,
    restitution=0.0,
    
    # 各向异性摩擦
    friction_combine_mode="average",  # "average" | "min" | "multiply" | "max"
    restitution_combine_mode="average"
)
```

### 可视材质

```python
# 预览材质 (简单)
sim_utils.PreviewSurfaceCfg(
    diffuse_color=(0.8, 0.2, 0.2),
    metallic=0.0,
    roughness=0.5,
    opacity=1.0
)

# MDL 材质 (高级)
sim_utils.MdlFileCfg(
    mdl_path="path/to/material.mdl",
    project_uvw=True
)

# Glass 材质
sim_utils.GlassMdlCfg(
    glass_ior=1.5,
    glass_color=(1.0, 1.0, 1.0)
)
```

## 物理属性配置

```python
# 刚体属性
sim_utils.RigidBodyPropertiesCfg(
    disable_gravity=False,
    max_depenetration_velocity=10.0,
    enable_gyroscopic_forces=True,
    retain_accelerations=False,
    linear_damping=0.0,
    angular_damping=0.0,
    max_linear_velocity=1000.0,
    max_angular_velocity=1000.0,
    max_contact_impulse=1e32,
    solver_position_iteration_count=4,
    solver_velocity_iteration_count=0,
    sleep_threshold=0.005
)

# Articulation 根属性
sim_utils.ArticulationRootPropertiesCfg(
    enabled_self_collisions=False,
    solver_position_iteration_count=8,
    solver_velocity_iteration_count=0,
    sleep_threshold=0.005,
    stabilization_threshold=0.001
)

# 质量属性
sim_utils.MassPropertiesCfg(
    mass=1.0,                        # 质量 (kg)
    density=None,                    # 密度 (kg/m³),与 mass 互斥
    inertia=None                     # 惯性矩阵 (自动计算)
)

# 碰撞属性
sim_utils.CollisionPropertiesCfg(
    collision_enabled=True,
    contact_offset=0.005,            # 接触检测偏移
    rest_offset=0.0                  # 静止偏移
)
```

## 使用 Spawner

### 方法 1: 通过配置类

```python
from isaaclab.assets import AssetBaseCfg

table_cfg = AssetBaseCfg(
    prim_path="{ENV_REGEX_NS}/Table",
    spawn=sim_utils.UsdFileCfg(usd_path="..."),
    init_state=AssetBaseCfg.InitialStateCfg(pos=(0.5, 0, 0))
)
```

### 方法 2: 直接调用

```python
# 创建 prim
sim_utils.spawn_from_usd(
    prim_path="/World/Object",
    cfg=sim_utils.UsdFileCfg(usd_path="...")
)

# 或使用配置的 func 引用
cfg = sim_utils.CuboidCfg(size=(0.1, 0.1, 0.1), ...)
cfg.func(prim_path="/World/Cube", cfg=cfg, translation=(0, 0, 0.5))
```

## 多资产生成

```python
from isaaclab.sim.spawners.from_files import spawn_multi_usd_file

# 从多个 USD 文件中随机选择
spawn_cfg = sim_utils.MultiUsdFileCfg(
    usd_path=[
        "path/to/object1.usd",
        "path/to/object2.usd",
        "path/to/object3.usd"
    ],
    random_choice=True,
    ...
)
```

## 实例化资产

```python
# 检查是否可实例化
sim_utils.check_instanceable(prim_path)

# 转换为可实例化
sim_utils.convert_to_instanceable(
    source_prim_path="/World/Object",
    instanceable_prim_path="/World/Object_Instanceable"
)
```
