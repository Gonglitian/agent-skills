---
name: isaaclab-async-pipeline-dev
description: Isaac Lab 异步数据生成流水线开发指南。用于实现并行仿真环境中的异步轨迹生成、动作执行和数据收集。当开发 Isaac Lab 数据生成器、实现异步仿真流水线、或改写 MimicGen 风格的数据生成系统时使用此技能。
---

# Isaac Lab 异步数据生成流水线开发指南

本指南总结了 Isaac Lab Mimic 模块中异步数据生成流水线的核心架构和编写范式。

## 核心架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      Main Event Loop                             │
│  (同步) env_loop() - 运行 env.step(), 处理 reset/action queues   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ DataGenerator│ │ DataGenerator│ │ DataGenerator│
    │   (env_id=0) │ │   (env_id=1) │ │   (env_id=N) │
    │   (async)    │ │   (async)    │ │   (async)    │
    └──────────────┘ └──────────────┘ └──────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           ▼
              ┌────────────────────────┐
              │   DataGenInfoPool      │
              │   (asyncio.Lock 保护)   │
              └────────────────────────┘
```

## 核心组件

### 1. 双队列通信机制

异步流水线的核心是两个 `asyncio.Queue`：

```python
import asyncio

# 创建队列
env_reset_queue = asyncio.Queue()   # 环境重置请求队列
env_action_queue = asyncio.Queue()  # 动作执行请求队列
```

**通信流程：**

```python
# DataGenerator (async) 端
async def generate(self, env_id, env_reset_queue, env_action_queue, ...):
    # 1. 请求重置环境
    await env_reset_queue.put(env_id)
    await env_reset_queue.join()  # 等待重置完成
    
    # 2. 请求执行动作
    await env_action_queue.put((env_id, action))
    await env_action_queue.join()  # 等待动作执行完成
    
    # 3. 读取观测
    obs = self.env.obs_buf

# Main Loop (sync) 端
def env_loop(env, env_reset_queue, env_action_queue, ...):
    while True:
        # 处理重置请求
        while not env_reset_queue.empty():
            env_id = env_reset_queue.get_nowait()
            env.reset(env_ids=torch.tensor([env_id]))
            env_reset_queue.task_done()
        
        # 等待所有环境提交动作
        while env_action_queue.qsize() != env.num_envs:
            asyncio_event_loop.run_until_complete(asyncio.sleep(0))
        
        # 收集所有动作
        actions = torch.zeros(env.action_space.shape)
        for i in range(env.num_envs):
            env_id, action = asyncio_event_loop.run_until_complete(
                env_action_queue.get()
            )
            actions[env_id] = action
        
        # 执行单步仿真 (所有环境同步)
        env.step(actions)
        
        # 通知所有生成器继续
        for i in range(env.num_envs):
            env_action_queue.task_done()
```

### 2. DataGenInfoPool - 共享数据池

```python
class DataGenInfoPool:
    """支持异步安全访问的数据池"""
    
    def __init__(self, env, env_cfg, device, asyncio_lock=None):
        self._datagen_infos = []
        self._subtask_boundaries = {}
        self._asyncio_lock = asyncio_lock  # asyncio.Lock
    
    @property
    def asyncio_lock(self):
        return self._asyncio_lock
    
    async def add_episode(self, episode):
        """异步安全地添加新 episode"""
        if self._asyncio_lock is not None:
            async with self._asyncio_lock:
                self._add_episode(episode)
        else:
            self._add_episode(episode)
```

**使用共享锁：**

```python
# 在 DataGenerator 中安全访问共享数据
async with self.src_demo_datagen_info_pool.asyncio_lock:
    # 检查是否有新数据
    if len(pool.datagen_infos) > prev_size:
        # 重新计算边界
        boundaries = self.randomize_subtask_boundaries()
```

### 3. DataGenerator - 异步数据生成器

```python
class DataGenerator:
    def __init__(self, env, src_demo_datagen_info_pool, ...):
        self.env = env
        self.src_demo_datagen_info_pool = src_demo_datagen_info_pool
    
    async def generate(
        self,
        env_id: int,
        success_term: TerminationTermCfg,
        env_reset_queue: asyncio.Queue,
        env_action_queue: asyncio.Queue,
        ...
    ) -> dict:
        """生成单条轨迹的异步方法"""
        
        # 1. 重置环境
        await env_reset_queue.put(env_id)
        await env_reset_queue.join()
        
        # 2. 主生成循环
        while not done:
            # 构建 waypoint
            waypoint = self.build_waypoint(...)
            
            # 3. 异步执行动作
            result = await waypoint.execute(
                env=self.env,
                env_id=env_id,
                env_action_queue=env_action_queue,
            )
            
            # 4. 累积结果
            generated_data.extend(result)
        
        return generated_data
```

### 4. Waypoint 异步执行

```python
class MultiWaypoint:
    async def execute(
        self,
        env: ManagerBasedRLMimicEnv,
        success_term: TerminationTermCfg,
        env_id: int,
        env_action_queue: asyncio.Queue | None = None,
    ):
        """异步执行 waypoint"""
        # 获取当前状态
        state = env.scene.get_state(is_relative=True)
        
        # 构建动作
        action = env.target_eef_pose_to_action(...)
        
        # 提交动作并等待执行
        if env_action_queue is not None:
            await env_action_queue.put((env_id, action[0]))
            await env_action_queue.join()  # 等待 env.step() 完成
            obs = env.obs_buf
        else:
            # 直接执行（单环境模式）
            obs, _, _, _, _ = env.step(action)
        
        return dict(states=[state], observations=[obs], actions=[action], ...)
```

## 完整流水线设置

```python
def setup_async_generation(env, num_envs, input_file, success_term, ...):
    """设置异步生成任务"""
    
    # 1. 获取事件循环
    asyncio_event_loop = asyncio.get_event_loop()
    
    # 2. 创建通信队列
    env_reset_queue = asyncio.Queue()
    env_action_queue = asyncio.Queue()
    
    # 3. 创建共享数据池（带锁）
    shared_lock = asyncio.Lock()
    shared_pool = DataGenInfoPool(env, env.cfg, env.device, asyncio_lock=shared_lock)
    shared_pool.load_from_dataset_file(input_file)
    
    # 4. 创建数据生成器
    data_generator = DataGenerator(env=env, src_demo_datagen_info_pool=shared_pool)
    
    # 5. 为每个环境创建异步任务
    tasks = []
    for i in range(num_envs):
        task = asyncio_event_loop.create_task(
            run_data_generator(
                env, i, env_reset_queue, env_action_queue,
                data_generator, success_term, ...
            )
        )
        tasks.append(task)
    
    return {
        "tasks": tasks,
        "event_loop": asyncio_event_loop,
        "reset_queue": env_reset_queue,
        "action_queue": env_action_queue,
        "info_pool": shared_pool,
    }

async def run_data_generator(env, env_id, reset_queue, action_queue, generator, ...):
    """持续运行数据生成的协程"""
    while True:
        try:
            results = await generator.generate(
                env_id=env_id,
                env_reset_queue=reset_queue,
                env_action_queue=action_queue,
                ...
            )
            # 处理结果
            update_statistics(results)
        except Exception as e:
            handle_error(e)
            raise
```

## 主循环实现

```python
def env_loop(env, env_reset_queue, env_action_queue, shared_pool, event_loop):
    """主环境循环 - 同步运行"""
    
    env_id_tensor = torch.tensor([0], dtype=torch.int64, device=env.device)
    
    with torch.inference_mode():
        while True:
            # 1. 等待所有环境提交动作，同时处理重置请求
            while env_action_queue.qsize() != env.num_envs:
                # 让出控制权给异步任务
                event_loop.run_until_complete(asyncio.sleep(0))
                
                # 处理待处理的重置请求
                while not env_reset_queue.empty():
                    env_id_tensor[0] = env_reset_queue.get_nowait()
                    env.reset(env_ids=env_id_tensor)
                    env_reset_queue.task_done()
            
            # 2. 收集所有环境的动作
            actions = torch.zeros(env.action_space.shape)
            for i in range(env.num_envs):
                env_id, action = event_loop.run_until_complete(
                    env_action_queue.get()
                )
                actions[env_id] = action
            
            # 3. 执行仿真步
            env.step(actions)
            
            # 4. 通知所有生成器动作已执行
            for i in range(env.num_envs):
                env_action_queue.task_done()
            
            # 5. 检查终止条件
            if should_terminate():
                break
    
    env.close()
```

## 关键设计模式

### 1. 生产者-消费者模式

```python
# 生产者 (DataGenerator)
await queue.put(item)      # 提交请求
await queue.join()         # 等待处理完成

# 消费者 (env_loop)
item = queue.get_nowait()  # 非阻塞获取
# ... 处理 ...
queue.task_done()          # 标记完成
```

### 2. 异步锁保护共享状态

```python
shared_lock = asyncio.Lock()

# 读写共享数据时
async with shared_lock:
    # 安全地访问/修改共享数据
    data = shared_pool.get_data()
    shared_pool.add_data(new_data)
```

### 3. 协程任务管理

```python
# 创建多个并发任务
tasks = [
    event_loop.create_task(coroutine(env_id=i))
    for i in range(num_envs)
]

# 主循环中让出控制权
event_loop.run_until_complete(asyncio.sleep(0))
```

## 常见陷阱与解决方案

### 1. 死锁预防

```python
# ❌ 错误：在持有锁时等待队列
async with lock:
    await queue.join()  # 可能死锁！

# ✅ 正确：先释放锁再等待
async with lock:
    data = get_data()
# 锁已释放
await queue.join()
```

### 2. 队列同步

```python
# 确保所有环境动作收集完毕后再执行 step
while env_action_queue.qsize() != env.num_envs:
    event_loop.run_until_complete(asyncio.sleep(0))
```

### 3. 异常处理

```python
async def run_data_generator(...):
    while True:
        try:
            results = await generator.generate(...)
        except Exception as e:
            # 记录错误但不中断其他环境
            sys.stderr.write(traceback.format_exc())
            raise  # 或 continue 跳过本次
```

## 扩展指南

### 添加新的数据源

```python
class CustomDataGenInfoPool(DataGenInfoPool):
    async def add_from_custom_source(self, source):
        async with self.asyncio_lock:
            episode = self._convert_source_to_episode(source)
            self._add_episode(episode)
```

### 自定义生成策略

```python
class CustomDataGenerator(DataGenerator):
    async def generate(self, ...):
        # 自定义生成逻辑
        ...
        # 复用基类的执行逻辑
        result = await self.execute_trajectory(...)
        return result
```

## 相关文件参考

- `libs/isaaclab/source/isaaclab_mimic/isaaclab_mimic/datagen/generation.py` - 主要流程编排
- `libs/isaaclab/source/isaaclab_mimic/isaaclab_mimic/datagen/data_generator.py` - 核心生成器
- `libs/isaaclab/source/isaaclab_mimic/isaaclab_mimic/datagen/datagen_info_pool.py` - 共享数据池
- `libs/isaaclab/source/isaaclab_mimic/isaaclab_mimic/datagen/waypoint.py` - 路径点执行
