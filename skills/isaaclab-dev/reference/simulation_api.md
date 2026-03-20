# 仿真控制 API 参考

## AppLauncher

启动 Isaac Sim 应用,必须在导入其他 isaaclab 模块之前调用。

```python
import argparse
from isaaclab.app import AppLauncher

# 解析命令行参数
parser = argparse.ArgumentParser(description="My Isaac Lab script")
parser.add_argument("--num_envs", type=int, default=16, help="Number of environments")
parser.add_argument("--task", type=str, default="MyTask")

# 添加 AppLauncher 参数
AppLauncher.add_app_launcher_args(parser)
# 添加的参数包括:
# --headless: 无 GUI 模式
# --enable_cameras: 启用相机渲染
# --device: 设备 (cuda:0, cpu)
# --livestream: 直播模式
# 等等...

args = parser.parse_args()

# 启动应用
app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

# 现在可以导入其他 isaaclab 模块
import isaaclab.sim as sim_utils
from isaaclab.envs import ManagerBasedEnv
# ...

def main():
    # 主逻辑
    ...

if __name__ == "__main__":
    main()
    simulation_app.close()
```

### 命令行参数

```bash
# 常用参数
--num_envs 32                    # 环境数量
--headless                       # 无 GUI 模式
--enable_cameras                 # 启用相机 (headless 模式需要)
--device cuda:0                  # 仿真设备
--livestream 1                   # 启用直播 (1=native, 2=webrtc)

# 示例
python my_script.py --num_envs 128 --headless --enable_cameras
```

## SimulationContext

仿真上下文,控制物理步进和渲染。

### 配置

```python
from isaaclab.sim import SimulationCfg

sim_cfg = SimulationCfg(
    # 时间步
    dt=0.01,                         # 物理时间步 (秒)
    render_interval=2,               # 渲染间隔 (仿真步数)
    
    # 设备
    device="cuda:0",
    
    # 物理场景路径
    physics_prim_path="/physicsScene",
    
    # 重力
    gravity=(0.0, 0.0, -9.81),
    
    # PhysX 设置
    physx=SimulationCfg.PhysxCfg(
        # 求解器类型 (0: PGS, 1: TGS)
        solver_type=1,
        
        # 迭代次数
        min_position_iteration_count=1,
        max_position_iteration_count=255,
        min_velocity_iteration_count=0,
        max_velocity_iteration_count=255,
        
        # GPU 设置
        enable_ccd=False,                    # 连续碰撞检测
        enable_stabilization=True,           # 稳定化
        enable_enhanced_determinism=False,   # 增强确定性
        
        # 碰撞参数
        bounce_threshold_velocity=0.2,
        friction_offset_threshold=0.04,
        friction_correlation_distance=0.025,
        
        # GPU 缓冲区
        gpu_max_rigid_contact_count=2**23,
        gpu_max_rigid_patch_count=5*2**15,
        gpu_found_lost_pairs_capacity=2**21,
        gpu_found_lost_aggregate_pairs_capacity=2**25,
        gpu_total_aggregate_pairs_capacity=2**21,
        gpu_collision_stack_size=2**26
    ),
    
    # Fabric (高性能数据传输)
    use_fabric=True,
    
    # 物理材质
    physics_material=SimulationCfg.PhysicsMaterialCfg(
        static_friction=0.5,
        dynamic_friction=0.5,
        restitution=0.0
    )
)
```

### 运行时 API

```python
from isaaclab.sim import SimulationContext

# 获取实例 (单例)
sim = SimulationContext.instance()

# 基本控制
sim.reset()                          # 重置仿真
sim.step(render=True)                # 步进一步
sim.render()                         # 仅渲染
sim.play()                           # 开始仿真
sim.pause()                          # 暂停仿真
sim.stop()                           # 停止仿真

# 状态查询
sim.is_playing()                     # 是否正在运行
sim.is_stopped()                     # 是否已停止
sim.has_gui()                        # 是否有 GUI
sim.has_rtx_sensors()                # 是否有 RTX 传感器

# 属性
sim.device                           # 设备
sim.physics_dt                       # 物理时间步
sim.cfg                              # 配置

# 相机视角设置
sim.set_camera_view(
    eye=(3.0, 3.0, 3.0),
    target=(0.0, 0.0, 0.0),
    camera_prim_path="/OmniverseKit_Persp"
)

# 设置仿真参数
sim.set_setting("/physics/parameter", value)
sim.get_setting("/physics/parameter")

# 渲染模式
from isaaclab.sim import SimulationContext
sim.set_render_mode(SimulationContext.RenderMode.FULL_RENDERING)
# 模式: NO_GUI_OR_RENDERING, NO_RENDERING, PARTIAL_RENDERING, FULL_RENDERING
```

## InteractiveScene

场景管理,处理环境克隆和实体管理。

### 配置

```python
from isaaclab.scene import InteractiveSceneCfg

scene_cfg = InteractiveSceneCfg(
    num_envs=1024,                   # 环境数量
    env_spacing=2.5,                 # 环境间距
    
    replicate_physics=True,          # 复制物理 (同质环境)
    # True: 高效,适合相同资产
    # False: 支持异质环境,但较慢
    
    filter_collisions=True,          # 过滤环境间碰撞
    
    lazy_sensor_update=True,         # 延迟更新传感器
    
    clone_in_fabric=True             # 在 Fabric 中克隆
)
```

### 运行时 API

```python
from isaaclab.scene import InteractiveScene

# 访问实体
scene = env.scene
robot = scene["robot"]               # 通过名称访问
robot = scene.articulations["robot"] # 通过类型访问

# 实体字典
scene.articulations                  # Dict[str, Articulation]
scene.rigid_objects                  # Dict[str, RigidObject]
scene.deformable_objects             # Dict[str, DeformableObject]
scene.sensors                        # Dict[str, SensorBase]
scene.extras                         # Dict[str, XformPrimView]
scene.terrain                        # TerrainImporter | None

# 属性
scene.num_envs                       # 环境数量
scene.env_origins                    # (num_envs, 3) 环境原点
scene.device                         # 设备
scene.physics_dt                     # 物理时间步

# 操作
scene.reset(env_ids=None)            # 重置场景
scene.write_data_to_sim()            # 写入数据到仿真
scene.update(dt)                     # 更新场景 (读取仿真数据)

# 状态管理
state = scene.get_state(is_relative=False)  # 获取状态
scene.reset_to(state, env_ids=None, is_relative=False)  # 恢复状态
```

## 常用工具函数

```python
import isaaclab.sim as sim_utils

# 创建新 stage
sim_utils.create_new_stage()

# 保存 stage
sim_utils.save_stage(path, save_and_reload_in_place=False)

# 获取当前 stage
stage = sim_utils.get_current_stage()

# 查找匹配 prim 路径
prim_paths = sim_utils.find_matching_prim_paths("/World/envs/env_.*/Robot")

# 绑定物理材质
sim_utils.bind_physics_material(prim_path, material_path)

# 检查 prim 是否存在
exists = sim_utils.is_prim_path_valid(prim_path)

# 获取 prim
prim = sim_utils.get_prim_at_path(prim_path)
```

## Context Manager 方式

```python
from isaaclab.sim import build_simulation_context

with build_simulation_context(
    create_new_stage=True,
    gravity_enabled=True,
    device="cuda:0",
    dt=0.01,
    add_ground_plane=True,
    add_lighting=True
) as sim:
    # 设计场景
    ...
    
    # 运行仿真
    sim.reset()
    while sim.is_playing():
        sim.step()
```

## 数学工具

```python
import isaaclab.utils.math as math_utils

# 四元数操作
math_utils.quat_mul(q1, q2)                    # 四元数乘法
math_utils.quat_inv(q)                         # 四元数逆
math_utils.quat_apply(q, v)                    # 四元数旋转向量
math_utils.quat_apply_inverse(q, v)            # 逆旋转
math_utils.quat_from_euler_xyz(roll, pitch, yaw)
math_utils.euler_xyz_from_quat(q)
math_utils.quat_unique(q)                      # 规范化四元数符号

# 矩阵操作
math_utils.matrix_from_quat(q)                 # 四元数转旋转矩阵
math_utils.quat_from_matrix(m)                 # 旋转矩阵转四元数

# 变换
math_utils.combine_frame_transforms(t1, q1, t2, q2)
math_utils.subtract_frame_transforms(t1, q1, t2, q2)

# 采样
math_utils.sample_uniform(low, high, size, device)
math_utils.sample_log_uniform(low, high, size, device)
math_utils.random_orientation(num, device)

# 向量操作
math_utils.normalize(v)
math_utils.saturate(x, lower, upper)
math_utils.wrap_to_pi(angles)
```

## 配置类装饰器

```python
from isaaclab.utils import configclass

@configclass
class MyConfigCfg:
    """配置类"""
    
    # 基本类型
    param1: int = 10
    param2: float = 0.5
    param3: str = "default"
    param4: bool = True
    
    # 列表/元组
    param5: tuple = (1.0, 2.0, 3.0)
    param6: list = [1, 2, 3]
    
    # 嵌套配置
    nested: "NestedCfg" = None
    
    def __post_init__(self):
        """初始化后调用"""
        if self.nested is None:
            self.nested = NestedCfg()

# 使用 .replace() 方法创建修改后的副本
new_cfg = old_cfg.replace(param1=20, param2=0.8)
```
