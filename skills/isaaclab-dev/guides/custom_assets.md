# 自定义资产加载指南

## 支持的资产格式

| 格式 | 用途 | 工具 |
|------|------|------|
| USD/USDA/USDC | 原生格式,推荐 | Omniverse |
| URDF | 机器人描述 | `sim_utils.UrdfFileCfg` |
| OBJ/STL | 网格文件 | 需转换 |
| MJCF | MuJoCo 格式 | 需转换 |

## 从 USD 加载

### 基本用法

```python
import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, RigidObjectCfg

# 机器人 (Articulation)
robot_cfg = ArticulationCfg(
    prim_path="{ENV_REGEX_NS}/Robot",
    spawn=sim_utils.UsdFileCfg(
        usd_path="/path/to/robot.usd",
        # 或使用 Nucleus 路径
        # usd_path=f"{ISAAC_NUCLEUS_DIR}/Robots/...",
        
        # 物理属性
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=10.0
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=8
        ),
        
        # 激活接触传感器
        activate_contact_sensors=True
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.0),
        rot=(1.0, 0.0, 0.0, 0.0),
        joint_pos={".*": 0.0}
    ),
    actuators={
        "arm": ImplicitActuatorCfg(
            joint_names_expr=["joint.*"],
            stiffness=100.0,
            damping=10.0
        )
    }
)

# 刚体物体
object_cfg = RigidObjectCfg(
    prim_path="{ENV_REGEX_NS}/Object",
    spawn=sim_utils.UsdFileCfg(
        usd_path="/path/to/object.usd",
        rigid_props=sim_utils.RigidBodyPropertiesCfg(),
        mass_props=sim_utils.MassPropertiesCfg(mass=0.1),
        collision_props=sim_utils.CollisionPropertiesCfg()
    ),
    init_state=RigidObjectCfg.InitialStateCfg(pos=(0.5, 0.0, 0.1))
)
```

### Nucleus 资产路径

```python
from isaaclab.utils.assets import (
    ISAAC_NUCLEUS_DIR,      # Isaac Sim 官方资产
    ISAACLAB_NUCLEUS_DIR,   # Isaac Lab 资产
    NVIDIA_NUCLEUS_DIR      # NVIDIA 资产
)

# 示例
usd_path = f"{ISAAC_NUCLEUS_DIR}/Props/Blocks/DexCube/dex_cube_instanceable.usd"
```

## 从 URDF 加载

### 转换 URDF 到 USD

```bash
# 使用命令行工具
./isaaclab.sh -p scripts/tools/convert_urdf.py \
    path/to/robot.urdf \
    path/to/output.usd \
    --merge-fixed-joints \
    --fix-base
```

### 直接使用 URDF

```python
from isaaclab.sim.converters import UrdfConverterCfg

robot_cfg = ArticulationCfg(
    prim_path="{ENV_REGEX_NS}/Robot",
    spawn=sim_utils.UrdfFileCfg(
        asset_path="/path/to/robot.urdf",
        fix_base=True,
        merge_fixed_joints=True
    ),
    ...
)
```

## 创建程序化资产

### 基本形状

```python
# 长方体
cube_cfg = RigidObjectCfg(
    prim_path="{ENV_REGEX_NS}/Cube",
    spawn=sim_utils.CuboidCfg(
        size=(0.05, 0.05, 0.05),
        rigid_props=sim_utils.RigidBodyPropertiesCfg(),
        mass_props=sim_utils.MassPropertiesCfg(mass=0.1),
        collision_props=sim_utils.CollisionPropertiesCfg(),
        visual_material=sim_utils.PreviewSurfaceCfg(
            diffuse_color=(0.8, 0.2, 0.2)
        )
    ),
    init_state=RigidObjectCfg.InitialStateCfg(pos=(0.5, 0.0, 0.1))
)

# 球体
sphere_cfg = RigidObjectCfg(
    prim_path="{ENV_REGEX_NS}/Sphere",
    spawn=sim_utils.SphereCfg(
        radius=0.05,
        ...
    ),
    ...
)

# 圆柱体
cylinder_cfg = RigidObjectCfg(
    prim_path="{ENV_REGEX_NS}/Cylinder",
    spawn=sim_utils.CylinderCfg(
        radius=0.03,
        height=0.1,
        axis="Z",
        ...
    ),
    ...
)
```

### 组合形状

```python
# 使用 USD Composer 创建复杂形状
# 或通过代码组合多个 prims
```

## 多资产随机生成

### 从多个文件随机选择

```python
from isaaclab.sim.spawners.from_files import spawn_multi_usd_file

spawn_cfg = sim_utils.MultiUsdFileCfg(
    usd_path=[
        "/path/to/object_variant_1.usd",
        "/path/to/object_variant_2.usd",
        "/path/to/object_variant_3.usd",
    ],
    random_choice=True,  # 随机选择
    rigid_props=sim_utils.RigidBodyPropertiesCfg(),
    mass_props=sim_utils.MassPropertiesCfg(mass=0.1)
)

# 需要设置
scene_cfg = MySceneCfg(replicate_physics=False)
```

## 资产物理属性配置

### 刚体属性

```python
rigid_props = sim_utils.RigidBodyPropertiesCfg(
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
```

### Articulation 属性

```python
articulation_props = sim_utils.ArticulationRootPropertiesCfg(
    enabled_self_collisions=False,
    solver_position_iteration_count=8,
    solver_velocity_iteration_count=0,
    sleep_threshold=0.005,
    stabilization_threshold=0.001
)
```

### 碰撞属性

```python
collision_props = sim_utils.CollisionPropertiesCfg(
    collision_enabled=True,
    contact_offset=0.005,
    rest_offset=0.0
)
```

### 质量属性

```python
# 直接指定质量
mass_props = sim_utils.MassPropertiesCfg(mass=1.0)

# 或使用密度 (自动计算质量)
mass_props = sim_utils.MassPropertiesCfg(density=1000.0)
```

## 执行器配置

```python
from isaaclab.actuators import (
    ImplicitActuatorCfg,
    IdealPDActuatorCfg,
    DCMotorCfg
)

actuators = {
    # 隐式 PD (使用 PhysX)
    "arm": ImplicitActuatorCfg(
        joint_names_expr=["joint1", "joint2", "joint3"],
        stiffness=100.0,
        damping=10.0,
        velocity_limit=10.0,
        effort_limit=50.0
    ),
    
    # 显式 PD (自定义计算)
    "gripper": IdealPDActuatorCfg(
        joint_names_expr=["finger.*"],
        stiffness={"finger.*": 1000.0},
        damping={"finger.*": 100.0}
    )
}
```

## 资产验证

### 检查实例化

```python
import isaaclab.sim as sim_utils

# 检查资产是否可实例化
is_instanceable = sim_utils.check_instanceable("/World/Object")
```

### 转换为可实例化

```python
# 转换为可实例化格式 (提高性能)
sim_utils.convert_to_instanceable(
    source_prim_path="/World/Object",
    instanceable_prim_path="/World/Object_Instanceable"
)
```

## 最佳实践

1. **使用可实例化资产**: 多环境时显著提高性能
2. **合理设置物理参数**: 避免仿真不稳定
3. **检查碰撞几何**: 确保碰撞体与视觉体匹配
4. **测试单环境**: 先在单环境中验证资产
5. **使用 Nucleus 缓存**: 加速资产加载
