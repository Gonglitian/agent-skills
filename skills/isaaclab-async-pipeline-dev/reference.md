# 异步流水线 API 参考

## DatagenInfo

数据生成信息的核心数据结构。

```python
class DatagenInfo:
    """存储数据生成所需的环境信息"""
    
    def __init__(
        self,
        eef_pose=None,              # torch.Tensor [..., 4, 4] - 末端执行器姿态
        object_poses=None,          # dict[str, Tensor] - 对象姿态字典
        subtask_term_signals=None,  # dict[str, Tensor] - 子任务终止信号
        subtask_start_signals=None, # dict[str, Tensor] - 子任务开始信号 (skillgen)
        target_eef_pose=None,       # torch.Tensor [..., 4, 4] - 目标末端姿态
        gripper_action=None,        # torch.Tensor [..., D] - 夹爪动作
    ):
        ...
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        ...
```

### 使用示例

```python
from isaaclab_mimic.datagen import DatagenInfo

# 从环境观测创建
datagen_info = DatagenInfo(
    eef_pose=obs["eef_pose"],
    object_poses={"cube": obs["cube_pose"]},
    target_eef_pose=target_pose,
    gripper_action=gripper_state,
)

# 访问数据
poses = datagen_info.eef_pose  # [T, 4, 4]
obj_pose = datagen_info.object_poses["cube"]  # [T, 4, 4]
```

## DataGenInfoPool

支持异步安全访问的演示数据池。

```python
class DataGenInfoPool:
    def __init__(
        self,
        env,
        env_cfg,
        device,
        asyncio_lock: asyncio.Lock | None = None,
    ):
        """
        Args:
            env: 环境实例
            env_cfg: 环境配置
            device: torch 设备
            asyncio_lock: 用于线程安全的异步锁
        """
        self._datagen_infos = []
        self._subtask_boundaries: dict[str, list[list[tuple[int, int]]]] = {}
        self._asyncio_lock = asyncio_lock
    
    @property
    def datagen_infos(self) -> list[DatagenInfo]:
        """返回所有 datagen 信息"""
        ...
    
    @property
    def subtask_boundaries(self) -> dict[str, list[list[tuple[int, int]]]]:
        """返回子任务边界: {eef_name: [[ep0_subtask_bounds], [ep1_subtask_bounds], ...]}"""
        ...
    
    @property
    def asyncio_lock(self) -> asyncio.Lock | None:
        """返回异步锁"""
        ...
    
    async def add_episode(self, episode: EpisodeData):
        """异步安全地添加 episode"""
        if self._asyncio_lock is not None:
            async with self._asyncio_lock:
                self._add_episode(episode)
        else:
            self._add_episode(episode)
    
    def load_from_dataset_file(self, file_path: str, select_demo_keys: list[str] | None = None):
        """从 HDF5 文件加载数据"""
        ...
```

### 子任务边界格式

```python
# subtask_boundaries 结构
{
    "ee_0": [
        # Episode 0
        [(start_0, end_0), (start_1, end_1), ...],  # 各子任务的 (开始帧, 结束帧)
        # Episode 1
        [(start_0, end_0), (start_1, end_1), ...],
        ...
    ],
    "ee_1": [...],  # 多末端执行器时
}
```

## DataGenerator

核心数据生成器类。

```python
class DataGenerator:
    def __init__(
        self,
        env: ManagerBasedRLMimicEnv,
        src_demo_datagen_info_pool: DataGenInfoPool | None = None,
        dataset_path: str | None = None,
        demo_keys: list[str] | None = None,
    ):
        """
        Args:
            env: 仿真环境
            src_demo_datagen_info_pool: 预加载的数据池
            dataset_path: HDF5 数据集路径
            demo_keys: 要使用的演示 key 列表
        """
        ...
    
    async def generate(
        self,
        env_id: int,
        success_term: TerminationTermCfg,
        env_reset_queue: asyncio.Queue | None = None,
        env_action_queue: asyncio.Queue | None = None,
        pause_subtask: bool = False,
        export_demo: bool = True,
        motion_planner: Any | None = None,
    ) -> dict:
        """
        生成单条轨迹。
        
        Args:
            env_id: 环境索引
            success_term: 成功判定函数配置
            env_reset_queue: 环境重置请求队列
            env_action_queue: 动作执行请求队列
            pause_subtask: 是否在子任务间暂停
            export_demo: 是否导出演示
            motion_planner: 运动规划器 (skillgen 模式)
        
        Returns:
            dict: {
                "initial_state": 初始状态,
                "states": 状态序列,
                "observations": 观测序列,
                "actions": 动作序列,
                "success": 是否成功,
            }
        """
        ...
    
    def randomize_subtask_boundaries(self) -> dict[str, np.ndarray]:
        """随机化子任务边界偏移"""
        ...
    
    def select_source_demo(
        self,
        eef_name: str,
        eef_pose: np.ndarray,
        object_pose: np.ndarray,
        src_demo_current_subtask_boundaries: np.ndarray,
        subtask_object_name: str,
        selection_strategy_name: str,
        selection_strategy_kwargs: dict | None = None,
    ) -> int:
        """选择源演示索引"""
        ...
    
    def generate_eef_subtask_trajectory(
        self,
        env_id: int,
        eef_name: str,
        subtask_ind: int,
        all_randomized_subtask_boundaries: dict,
        runtime_subtask_constraints_dict: dict,
        selected_src_demo_inds: dict,
    ) -> WaypointTrajectory:
        """生成单个子任务的轨迹"""
        ...
```

## Waypoint 类族

### Waypoint

单个路径点。

```python
class Waypoint:
    def __init__(
        self,
        pose: torch.Tensor,           # 4x4 目标姿态
        gripper_action: torch.Tensor,  # 夹爪动作
        noise: float | None = None,    # 动作噪声幅度
    ):
        ...
```

### WaypointSequence

路径点序列。

```python
class WaypointSequence:
    def __init__(self, sequence: list[Waypoint] | None = None):
        ...
    
    @classmethod
    def from_poses(
        cls,
        poses: torch.Tensor,           # [T, 4, 4]
        gripper_actions: torch.Tensor,  # [T, D]
        action_noise: float | torch.Tensor,
    ) -> "WaypointSequence":
        """从姿态序列创建"""
        ...
    
    def split(self, ind: int) -> tuple["WaypointSequence", "WaypointSequence"]:
        """在索引处分割"""
        ...
    
    @property
    def last_waypoint(self) -> Waypoint:
        """返回最后一个路径点"""
        ...
```

### WaypointTrajectory

完整轨迹（多个序列组成）。

```python
class WaypointTrajectory:
    def __init__(self):
        self.waypoint_sequences = []
    
    def add_waypoint_sequence(self, sequence: WaypointSequence):
        """添加序列（无插值）"""
        ...
    
    def add_waypoint_sequence_for_target_pose(
        self,
        pose: torch.Tensor,
        gripper_action: torch.Tensor,
        num_steps: int,
        skip_interpolation: bool = False,
        action_noise: float = 0.0,
    ):
        """添加到目标姿态的序列（可选插值）"""
        ...
    
    def merge(
        self,
        other: "WaypointTrajectory",
        num_steps_interp: int | None = None,
        num_steps_fixed: int | None = None,
        action_noise: float = 0.0,
    ):
        """合并另一个轨迹（带插值段）"""
        ...
    
    def pop_first(self) -> WaypointSequence:
        """移除并返回第一个路径点"""
        ...
    
    def get_full_sequence(self) -> WaypointSequence:
        """获取完整序列"""
        ...
```

### MultiWaypoint

多末端执行器路径点。

```python
class MultiWaypoint:
    def __init__(self, waypoints: dict[str, Waypoint]):
        """
        Args:
            waypoints: {eef_name: Waypoint} 字典
        """
        ...
    
    async def execute(
        self,
        env: ManagerBasedRLMimicEnv,
        success_term: TerminationTermCfg,
        env_id: int = 0,
        env_action_queue: asyncio.Queue | None = None,
    ) -> dict:
        """
        异步执行多末端路径点。
        
        Returns:
            dict: {"states": [...], "observations": [...], "actions": [...], "success": bool}
        """
        ...
```

## SelectionStrategy

源演示选择策略。

```python
# 注册新策略
class MyStrategy(SelectionStrategy):
    NAME = "my_strategy"
    
    def select_source_demo(
        self,
        eef_pose: torch.Tensor,
        object_pose: torch.Tensor,
        src_subtask_datagen_infos: list[DatagenInfo],
        **kwargs,
    ) -> int:
        """返回选中的源演示索引"""
        ...

# 使用策略
from isaaclab_mimic.datagen import make_selection_strategy

strategy = make_selection_strategy("nearest_neighbor_object")
selected_idx = strategy.select_source_demo(
    eef_pose=current_eef,
    object_pose=current_obj,
    src_subtask_datagen_infos=src_infos,
    pos_weight=1.0,
    rot_weight=1.0,
    nn_k=3,
)
```

### 内置策略

| 名称 | 描述 |
|------|------|
| `random` | 随机选择 |
| `nearest_neighbor_object` | 选择对象姿态最接近的源演示 |
| `nearest_neighbor_robot_distance` | 选择使机器人移动距离最小的源演示 |

## 流程编排函数

### setup_env_config

```python
def setup_env_config(
    env_name: str,
    output_dir: str,
    output_file_name: str,
    num_envs: int,
    device: str,
    generation_num_trials: int | None = None,
    recorder_cfg: RecorderManagerBaseCfg | None = None,
) -> tuple[Any, Any]:
    """
    配置数据生成环境。
    
    Returns:
        (env_cfg, success_term): 环境配置和成功判定
    """
    ...
```

### setup_async_generation

```python
def setup_async_generation(
    env: Any,
    num_envs: int,
    input_file: str,
    success_term: Any,
    pause_subtask: bool = False,
    motion_planners: Any = None,
) -> dict[str, Any]:
    """
    设置异步生成任务。
    
    Returns:
        dict: {
            "tasks": list[asyncio.Task],      # 生成任务列表
            "event_loop": asyncio.EventLoop,  # 事件循环
            "reset_queue": asyncio.Queue,     # 重置队列
            "action_queue": asyncio.Queue,    # 动作队列
            "info_pool": DataGenInfoPool,     # 共享数据池
        }
    """
    ...
```

### env_loop

```python
def env_loop(
    env: ManagerBasedRLMimicEnv,
    env_reset_queue: asyncio.Queue,
    env_action_queue: asyncio.Queue,
    shared_datagen_info_pool: DataGenInfoPool,
    asyncio_event_loop: asyncio.AbstractEventLoop,
):
    """
    主环境循环。同步运行，协调异步生成器。
    
    在 torch.inference_mode() 下运行以提高性能。
    """
    ...
```

### run_data_generator

```python
async def run_data_generator(
    env: ManagerBasedRLMimicEnv,
    env_id: int,
    env_reset_queue: asyncio.Queue,
    env_action_queue: asyncio.Queue,
    data_generator: DataGenerator,
    success_term: TerminationTermCfg,
    pause_subtask: bool = False,
    motion_planner: Any = None,
):
    """
    持续运行数据生成的异步协程。
    
    循环调用 data_generator.generate() 直到达到目标数量。
    """
    ...
```

## 坐标变换工具

```python
import isaaclab.utils.math as PoseUtils

# 姿态逆
inv_pose = PoseUtils.pose_inv(pose)  # [N, 4, 4] -> [N, 4, 4]

# 坐标系变换: A 系中的姿态 -> B 系中的姿态
pose_in_B = PoseUtils.pose_in_A_to_pose_in_B(
    pose_in_A=pose,      # [N, 4, 4]
    pose_A_in_B=T_A_B,   # [1, 4, 4] 或 [N, 4, 4]
)

# 分解姿态为位置和旋转
pos, rot = PoseUtils.unmake_pose(pose)  # -> [N, 3], [N, 3, 3]

# 组合位置和旋转为姿态
pose = PoseUtils.make_pose(pos, rot)

# 姿态插值
interp_poses, num_steps = PoseUtils.interpolate_poses(
    pose_1=start_pose,
    pose_2=end_pose,
    num_steps=10,
)

# 计算 delta 姿态
delta_pose = PoseUtils.get_delta_object_pose(current_pose, reference_pose)

# 添加均匀噪声
noisy_pos, noisy_rot = PoseUtils.add_uniform_noise_to_pose(
    pos, rot, pos_noise_scale=0.01, rot_noise_scale=0.05
)
```

## 数据集文件操作

```python
from isaaclab.utils.datasets import HDF5DatasetFileHandler, EpisodeData

# 读取数据集
handler = HDF5DatasetFileHandler()
handler.open("path/to/dataset.hdf5")

# 获取环境名
env_name = handler.get_env_name()

# 获取所有 episode 名称
episode_names = handler.get_episode_names()

# 加载单个 episode
episode = handler.load_episode(episode_name, device)

# EpisodeData 结构
episode.data  # dict: {"obs": {...}, "actions": Tensor, ...}
episode.data["obs"]["datagen_info"]  # datagen 信息
episode.data["actions"]  # 动作序列
```
