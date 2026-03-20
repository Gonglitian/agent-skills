# cuRobo 集成指南

cuRobo 是 NVIDIA 的 GPU 加速运动规划库,可与 Isaac Lab 集成用于:
- 逆运动学 (IK)
- 运动规划
- 碰撞检测

## 安装

cuRobo 已包含在 Isaac Lab 的 Docker 镜像中。手动安装:

```bash
pip install nvidia-curobo
```

## 基本使用

### 逆运动学

```python
from curobo.types.math import Pose
from curobo.types.robot import RobotConfig
from curobo.cuda_robot_model.cuda_robot_model import CudaRobotModel
from curobo.wrap.reacher.ik_solver import IKSolver, IKSolverConfig

# 加载机器人配置
robot_cfg = RobotConfig.from_robot_config_file(
    robot_config_path="path/to/robot_config.yml",
    urdf_path="path/to/robot.urdf"
)

# 创建 IK 求解器
ik_config = IKSolverConfig(
    robot_config=robot_cfg,
    num_seeds=32,
    position_threshold=0.005,
    rotation_threshold=0.05
)
ik_solver = IKSolver(ik_config)

# 求解 IK
target_pose = Pose(
    position=torch.tensor([[0.5, 0.0, 0.5]]),
    quaternion=torch.tensor([[1.0, 0.0, 0.0, 0.0]])  # wxyz
)

result = ik_solver.solve(target_pose)

if result.success.item():
    joint_positions = result.solution
```

### 运动规划

```python
from curobo.wrap.reacher.motion_gen import MotionGen, MotionGenConfig

# 配置
motion_gen_config = MotionGenConfig(
    robot_config=robot_cfg,
    world_config=world_cfg,
    trajopt_tsteps=32,
    interpolation_dt=0.01
)

motion_gen = MotionGen(motion_gen_config)

# 规划
start_state = robot.data.joint_pos[0]
goal_pose = Pose(...)

result = motion_gen.plan_single(start_state, goal_pose)

if result.success.item():
    trajectory = result.interpolated_plan
    # trajectory: (num_timesteps, num_joints)
```

## 与 Isaac Lab 集成

### 在环境中使用 cuRobo

```python
from curobo.wrap.reacher.ik_solver import IKSolver
from curobo.wrap.reacher.motion_gen import MotionGen

class MyEnv(DirectRLEnv):
    def __init__(self, cfg, **kwargs):
        super().__init__(cfg, **kwargs)
        
        # 初始化 cuRobo
        self._setup_curobo()
    
    def _setup_curobo(self):
        """初始化 cuRobo 组件"""
        # IK 求解器
        self.ik_solver = IKSolver.from_config(
            robot_config_path="franka.yml"
        )
        
        # 运动规划器
        self.motion_gen = MotionGen.from_config(
            robot_config_path="franka.yml",
            world_config_path="world.yml"
        )
    
    def compute_ik(self, target_poses):
        """计算逆运动学"""
        # target_poses: (num_envs, 7) [pos, quat]
        
        pose = Pose(
            position=target_poses[:, :3],
            quaternion=target_poses[:, 3:]
        )
        
        result = self.ik_solver.solve_batch(
            pose,
            seed_config=self.robot.data.joint_pos
        )
        
        return result.solution, result.success
```

### 使用 cuRobo Action

```python
from isaaclab_mimic.motion_planners.curobo import CuroboMotionPlanner

@configclass
class ActionsCfg:
    # 使用 cuRobo 规划的末端控制
    arm_action = CuroboMotionPlannerActionCfg(
        asset_name="robot",
        robot_config_path="franka.yml",
        world_config_path="world.yml"
    )
```

## 世界配置

### 定义碰撞世界

```yaml
# world_config.yml
world_model:
  - type: cuboid
    name: table
    pose: [0.5, 0.0, 0.4, 1.0, 0.0, 0.0, 0.0]  # [x, y, z, qw, qx, qy, qz]
    dims: [0.8, 1.2, 0.02]  # [x, y, z]
    
  - type: cuboid
    name: obstacle
    pose: [0.3, 0.3, 0.5, 1.0, 0.0, 0.0, 0.0]
    dims: [0.1, 0.1, 0.2]

collision_checking:
  mesh_cache_dir: "/tmp/curobo_mesh_cache"
  collision_sphere_buffer: 0.005
```

### 动态更新世界

```python
from curobo.geom.types import WorldConfig, Cuboid

def update_collision_world(motion_gen, objects):
    """更新碰撞世界"""
    world_config = WorldConfig()
    
    for obj in objects:
        cuboid = Cuboid(
            name=obj.name,
            pose=obj.pose.tolist(),
            dims=obj.dims.tolist()
        )
        world_config.add_obstacle(cuboid)
    
    motion_gen.update_world(world_config)
```

## 批量处理

cuRobo 支持 GPU 批量处理多个查询:

```python
# 批量 IK
batch_size = 256
target_poses = torch.rand(batch_size, 7)  # [pos, quat]

results = ik_solver.solve_batch(
    Pose.from_tensor(target_poses),
    num_seeds=32
)

# 获取结果
solutions = results.solution  # (batch_size, num_joints)
success = results.success     # (batch_size,)
```

## 性能优化

### 1. 使用 CUDA Graph

```python
# 启用 CUDA Graph 加速
ik_solver = IKSolver.from_config(
    robot_config_path="franka.yml",
    use_cuda_graph=True
)
```

### 2. 预热

```python
# 首次调用预热
_ = ik_solver.solve(dummy_pose)
_ = motion_gen.plan_single(dummy_start, dummy_goal)
```

### 3. 共享实例

```python
# 多环境共享 cuRobo 实例
class CuroboPool:
    _ik_solver = None
    _motion_gen = None
    
    @classmethod
    def get_ik_solver(cls):
        if cls._ik_solver is None:
            cls._ik_solver = IKSolver.from_config(...)
        return cls._ik_solver
```

## 常见问题

### 1. IK 失败率高

- 增加 `num_seeds`
- 放宽阈值
- 检查目标是否在工作空间内

### 2. 规划速度慢

- 启用 CUDA Graph
- 减少 `trajopt_tsteps`
- 使用更粗糙的碰撞检测

### 3. 碰撞检测不准确

- 检查碰撞球体配置
- 增加 `collision_sphere_buffer`
- 更新网格缓存
