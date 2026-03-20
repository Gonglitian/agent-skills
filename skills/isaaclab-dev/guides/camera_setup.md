# 相机和传感器设置指南

## 相机类型选择

| 类型 | 适用场景 | 内存效率 |
|------|----------|----------|
| `Camera` | 标准相机,灵活 | 中等 |
| `TiledCamera` | 大量并行环境 | 高 |

## 基本相机配置

### 1. 固定位置相机 (第三人称)

```python
from isaaclab.sensors import CameraCfg
import isaaclab.sim as sim_utils

# 场景前方俯视相机
front_camera = CameraCfg(
    prim_path="{ENV_REGEX_NS}/front_camera",
    update_period=0.0,  # 每步更新
    height=480,
    width=640,
    data_types=["rgb", "distance_to_image_plane"],
    spawn=sim_utils.PinholeCameraCfg(
        focal_length=24.0,
        focus_distance=400.0,
        horizontal_aperture=20.955,
        clipping_range=(0.1, 10.0)
    ),
    offset=CameraCfg.OffsetCfg(
        pos=(1.5, 0.0, 1.0),    # 前方上方
        rot=(0.35355, -0.61237, -0.61237, 0.35355),  # 朝向原点
        convention="ros"
    )
)
```

### 2. 腕部相机 (Eye-in-Hand)

```python
# 挂载在机器人末端
wrist_camera = CameraCfg(
    prim_path="{ENV_REGEX_NS}/Robot/panda_hand/wrist_cam",
    update_period=0.0,
    height=200,
    width=200,
    data_types=["rgb"],
    spawn=sim_utils.PinholeCameraCfg(
        focal_length=24.0,
        clipping_range=(0.01, 1.0)  # 近距离裁剪
    ),
    offset=CameraCfg.OffsetCfg(
        pos=(0.1, 0.0, 0.0),       # 相对于 panda_hand 的偏移
        rot=(-0.5, 0.5, 0.5, -0.5),  # 朝向前方
        convention="ros"
    )
)
```

### 3. 侧视相机

```python
side_camera = CameraCfg(
    prim_path="{ENV_REGEX_NS}/side_camera",
    update_period=0.0,
    height=480,
    width=640,
    data_types=["rgb"],
    spawn=sim_utils.PinholeCameraCfg(
        focal_length=24.0,
        horizontal_aperture=20.955,
        clipping_range=(0.1, 10.0)
    ),
    offset=CameraCfg.OffsetCfg(
        pos=(0.0, 1.5, 0.5),       # 侧方
        rot=(0.5, -0.5, -0.5, 0.5),  # 朝向中心
        convention="ros"
    )
)
```

## 将相机添加到场景

```python
@configclass
class MySceneCfg(InteractiveSceneCfg):
    robot: ArticulationCfg = ...
    
    # 添加相机
    front_cam: CameraCfg = front_camera
    wrist_cam: CameraCfg = wrist_camera
```

## 相机朝向配置

### convention 参数

| 值 | X 轴 | Y 轴 | Z 轴 |
|----|------|------|------|
| `"ros"` | 右 | 下 | 前 |
| `"opengl"` | 右 | 上 | 后 |
| `"world"` | 前 | 左 | 上 |

### 常用朝向四元数 (wxyz, ROS convention)

```python
# 朝向 -Z (向下看)
rot=(0.707, 0.0, 0.707, 0.0)

# 朝向 +X (向前看,沿 world X 轴)
rot=(0.5, -0.5, -0.5, 0.5)

# 朝向 -X (向后看)
rot=(0.5, 0.5, 0.5, 0.5)

# 朝向 +Y (向左看)
rot=(0.707, 0.0, 0.0, 0.707)

# 从上方俯视 (45度)
rot=(0.35355, -0.61237, -0.61237, 0.35355)
```

## 图像观测配置

```python
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import SceneEntityCfg
import isaaclab.envs.mdp as mdp

@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        # RGB 图像
        front_rgb = ObsTerm(
            func=mdp.image,
            params={
                "sensor_cfg": SceneEntityCfg("front_cam"),
                "data_type": "rgb",
                "normalize": False  # uint8: 0-255
            }
        )
        
        # 深度图像
        front_depth = ObsTerm(
            func=mdp.image,
            params={
                "sensor_cfg": SceneEntityCfg("front_cam"),
                "data_type": "distance_to_image_plane",
                "normalize": True  # float32: 0-1
            }
        )
        
        # 腕部相机
        wrist_rgb = ObsTerm(
            func=mdp.image,
            params={
                "sensor_cfg": SceneEntityCfg("wrist_cam"),
                "data_type": "rgb",
                "normalize": False
            }
        )
        
        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = False  # 图像不拼接
    
    policy: PolicyCfg = PolicyCfg()
```

## 渲染质量设置

```python
@configclass
class MyEnvCfg(ManagerBasedRLEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        
        # 重置后重新渲染次数 (解决渲染延迟)
        self.num_rerenders_on_reset = 3
        
        # 抗锯齿模式
        self.sim.render.antialiasing_mode = "DLAA"
        # 选项: "Off", "FXAA", "DLAA", "TAA"
        
        # 图像观测列表 (用于某些包装器)
        self.image_obs_list = ["front_rgb", "wrist_rgb"]
```

## 数据访问

```python
# 运行时访问相机数据
camera = env.scene["front_cam"]

# 图像数据
rgb = camera.data.output["rgb"]  # (num_envs, H, W, 3) uint8
depth = camera.data.output["distance_to_image_plane"]  # (num_envs, H, W, 1) float32

# 相机内参
K = camera.data.intrinsic_matrices  # (num_envs, 3, 3)

# 相机外参
pos = camera.data.pos_w            # (num_envs, 3)
quat = camera.data.quat_w_world    # (num_envs, 4)
```

## TiledCamera (高效内存)

大量环境时使用 TiledCamera 减少内存占用。

```python
from isaaclab.sensors import TiledCameraCfg

tiled_camera = TiledCameraCfg(
    prim_path="{ENV_REGEX_NS}/camera",
    update_period=0.0,
    height=200,
    width=200,
    data_types=["rgb"],
    spawn=sim_utils.PinholeCameraCfg(...),
    offset=TiledCameraCfg.OffsetCfg(...)
)
```

## 常见问题

### 1. 相机图像全黑

- 检查 `clipping_range`,确保物体在范围内
- 添加足够的灯光
- 确保 `--enable_cameras` 参数 (headless 模式)

### 2. 图像有延迟

```python
self.num_rerenders_on_reset = 3  # 增加重新渲染次数
```

### 3. 相机位置不对

- 检查 `convention` 参数
- 使用可视化调试相机位置

### 4. 渲染性能差

- 降低分辨率
- 使用 `TiledCamera`
- 减少 `data_types`
- 设置合适的 `update_period`
