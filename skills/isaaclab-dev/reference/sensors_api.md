# 传感器系统 API 参考

## 传感器类型概览

| 传感器 | 用途 | 数据类型 |
|--------|------|----------|
| `Camera` | RGB/深度图像 | rgb, depth, distance_to_image_plane |
| `TiledCamera` | 高效并行相机 | 同上,优化内存 |
| `ContactSensor` | 接触力检测 | 力、法向量、位置 |
| `FrameTransformer` | 坐标变换 | 相对位姿 |
| `RayCaster` | 射线投射 | 距离、法向量 |
| `IMU` | 惯性测量 | 加速度、角速度 |

## Camera

### 配置

```python
from isaaclab.sensors import CameraCfg
import isaaclab.sim as sim_utils

camera_cfg = CameraCfg(
    prim_path="{ENV_REGEX_NS}/Camera",
    
    # 更新周期 (0.0 = 每步更新)
    update_period=0.0,
    
    # 图像尺寸
    height=480,
    width=640,
    
    # 数据类型
    data_types=["rgb", "distance_to_image_plane"],
    # 可选: "rgb", "rgba", "depth", "distance_to_image_plane",
    #       "normals", "motion_vectors", "semantic_segmentation",
    #       "instance_segmentation_fast", "instance_id_segmentation_fast"
    
    # 相机参数
    spawn=sim_utils.PinholeCameraCfg(
        focal_length=24.0,              # 焦距 (mm)
        focus_distance=400.0,           # 对焦距离
        horizontal_aperture=20.955,     # 水平光圈 (mm)
        clipping_range=(0.1, 10.0)      # 裁剪范围 (near, far)
    ),
    
    # 位置/朝向偏移
    offset=CameraCfg.OffsetCfg(
        pos=(0.5, 0.0, 0.5),
        rot=(0.5, -0.5, -0.5, 0.5),    # wxyz
        convention="ros"                # "ros" | "opengl" | "world"
    )
)
```

### 挂载相机

```python
# 1. 固定位置相机 (第三人称)
front_cam = CameraCfg(
    prim_path="{ENV_REGEX_NS}/front_camera",
    offset=CameraCfg.OffsetCfg(
        pos=(1.0, 0.0, 0.5),
        rot=(0.35355, -0.61237, -0.61237, 0.35355),
        convention="ros"
    ),
    ...
)

# 2. 腕部相机 (挂载在机器人末端)
wrist_cam = CameraCfg(
    prim_path="{ENV_REGEX_NS}/Robot/panda_hand/wrist_camera",
    offset=CameraCfg.OffsetCfg(
        pos=(0.1, 0.0, 0.0),
        rot=(0.0, 0.0, 0.0, 1.0),
        convention="ros"
    ),
    ...
)

# 3. 头部相机 (humanoid)
head_cam = CameraCfg(
    prim_path="{ENV_REGEX_NS}/Robot/head/camera",
    ...
)
```

### 运行时 API

```python
camera: Camera = env.scene["camera"]

# 数据访问
camera.data.output["rgb"]                    # (num_envs, H, W, 3) uint8
camera.data.output["distance_to_image_plane"] # (num_envs, H, W, 1) float32
camera.data.output["depth"]                  # 同上

# 相机内参
camera.data.intrinsic_matrices               # (num_envs, 3, 3)

# 相机位姿
camera.data.pos_w                            # (num_envs, 3)
camera.data.quat_w_world                     # (num_envs, 4)

# 更新 (通常由 scene.update 调用)
camera.update(dt, force_recompute=True)
```

### 图像观测配置

```python
from isaaclab.managers import ObservationTermCfg as ObsTerm, SceneEntityCfg
import isaaclab.envs.mdp as mdp

# 在 ObservationsCfg 中使用
@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        # RGB 图像
        camera_rgb = ObsTerm(
            func=mdp.image,
            params={
                "sensor_cfg": SceneEntityCfg("camera"),
                "data_type": "rgb",
                "normalize": False    # True: 归一化到 [0, 1]
            }
        )
        
        # 深度图像
        camera_depth = ObsTerm(
            func=mdp.image,
            params={
                "sensor_cfg": SceneEntityCfg("camera"),
                "data_type": "distance_to_image_plane",
                "normalize": True
            }
        )
```

## TiledCamera

高效内存使用的相机实现,适合大量并行环境。

```python
from isaaclab.sensors import TiledCameraCfg

tiled_camera_cfg = TiledCameraCfg(
    prim_path="{ENV_REGEX_NS}/Camera",
    update_period=0.0,
    height=200,
    width=200,
    data_types=["rgb"],
    spawn=sim_utils.PinholeCameraCfg(...),
    offset=TiledCameraCfg.OffsetCfg(...)
)
```

## ContactSensor

### 配置

```python
from isaaclab.sensors import ContactSensorCfg

contact_cfg = ContactSensorCfg(
    prim_path="{ENV_REGEX_NS}/Robot/.*",      # 检测 body
    
    update_period=0.0,
    
    # 过滤碰撞检测的 prim
    filter_prim_paths_expr=["{ENV_REGEX_NS}/Object"],
    
    # 历史长度
    history_length=1,
    
    # 接触可视化
    debug_vis=False,
    
    # 是否跟踪气压 (soft contact)
    track_air_time=False
)
```

### 运行时 API

```python
contact_sensor: ContactSensor = env.scene["contact_sensor"]

# 接触数据
contact_sensor.data.net_forces_w           # (num_envs, num_bodies, 3) 净力
contact_sensor.data.net_forces_w_history   # (num_envs, history_len, num_bodies, 3)

contact_sensor.data.force_matrix_w         # (num_envs, num_bodies, num_shapes, 3)

# 当前时刻接触
contact_sensor.data.current_contact_time   # (num_envs, num_bodies)
contact_sensor.data.last_contact_time      # (num_envs, num_bodies)

# 工具方法
forces = contact_sensor.compute_first_contact(dt)
```

## FrameTransformer

用于追踪不同坐标系之间的相对变换。

### 配置

```python
from isaaclab.sensors.frame_transformer.frame_transformer_cfg import (
    FrameTransformerCfg,
    OffsetCfg
)

ee_frame_cfg = FrameTransformerCfg(
    prim_path="{ENV_REGEX_NS}/Robot/panda_link0",
    
    # 目标框架
    target_frames=[
        FrameTransformerCfg.FrameCfg(
            prim_path="{ENV_REGEX_NS}/Robot/panda_hand",
            name="ee_frame",
            offset=OffsetCfg(
                pos=(0.0, 0.0, 0.107),    # TCP 偏移
                rot=(1.0, 0.0, 0.0, 0.0)
            )
        ),
        FrameTransformerCfg.FrameCfg(
            prim_path="{ENV_REGEX_NS}/Object",
            name="object_frame"
        )
    ],
    
    debug_vis=False
)
```

### 运行时 API

```python
frame_transformer: FrameTransformer = env.scene["ee_frame"]

# 目标相对于源的位姿
frame_transformer.data.target_pos_w        # (num_envs, num_targets, 3)
frame_transformer.data.target_quat_w       # (num_envs, num_targets, 4)

frame_transformer.data.target_pos_source   # 相对于源框架
frame_transformer.data.target_quat_source
```

## RayCaster

射线投射传感器,用于地形感知、障碍物检测等。

```python
from isaaclab.sensors import RayCasterCfg
from isaaclab.sensors.ray_caster.patterns import GridPatternCfg

raycaster_cfg = RayCasterCfg(
    prim_path="{ENV_REGEX_NS}/Robot/base",
    
    # 射线模式
    pattern_cfg=GridPatternCfg(
        resolution=0.1,           # 分辨率
        size=(1.0, 1.0)          # 范围
    ),
    
    # 射线方向 (向下)
    attach_yaw_only=True,
    offset=RayCasterCfg.OffsetCfg(pos=(0.0, 0.0, 0.5)),
    
    # 碰撞检测目标
    mesh_prim_paths=["/World/ground"],
    
    debug_vis=False
)
```

### 运行时 API

```python
raycaster: RayCaster = env.scene["raycaster"]

# 射线命中数据
raycaster.data.ray_hits_w          # (num_envs, num_rays, 3) 命中点
raycaster.data.ray_distances       # (num_envs, num_rays) 距离
```

## IMU

```python
from isaaclab.sensors import ImuCfg

imu_cfg = ImuCfg(
    prim_path="{ENV_REGEX_NS}/Robot/base",
    update_period=0.0,
    
    # 噪声模型
    linear_acceleration_noise_model=...,
    angular_velocity_noise_model=...
)

# 运行时
imu: Imu = env.scene["imu"]
imu.data.lin_acc_b                 # (num_envs, 3) 本体加速度
imu.data.ang_vel_b                 # (num_envs, 3) 本体角速度
```

## 渲染设置

相机渲染质量相关设置:

```python
@configclass  
class MyEnvCfg(ManagerBasedRLEnvCfg):
    def __post_init__(self):
        # 重置后重新渲染次数 (解决渲染延迟)
        self.num_rerenders_on_reset = 3
        
        # 抗锯齿模式
        self.sim.render.antialiasing_mode = "DLAA"  # "Off" | "FXAA" | "DLAA"
```
