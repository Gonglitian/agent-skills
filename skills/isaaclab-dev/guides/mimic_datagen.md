# 模仿学习数据生成指南

Isaac Lab 通过 `isaaclab_mimic` 模块支持模仿学习数据生成。

## 概述

### 数据生成流程

```
人类演示 → 轨迹记录 → 数据增强 → HDF5 数据集 → 模型训练
```

### 关键组件

| 组件 | 用途 |
|------|------|
| `ManagerBasedRLMimicEnv` | 支持数据记录的环境 |
| `RecorderManager` | 管理数据记录 |
| `DataGenerator` | 批量生成数据 |
| `SelectionStrategy` | 演示选择策略 |

## 环境配置

### 创建 Mimic 环境

```python
from isaaclab.envs import ManagerBasedRLMimicEnv
from isaaclab.envs.mimic_env_cfg import MimicEnvCfg
from isaaclab.managers import RecorderManagerBaseCfg
from isaaclab.managers.recorder_manager import DatasetExportMode

@configclass
class MyMimicEnvCfg(MimicEnvCfg):
    """Mimic 环境配置"""
    
    # 继承基础环境配置
    scene: MySceneCfg = MySceneCfg(...)
    actions: ActionsCfg = ActionsCfg()
    observations: ObservationsCfg = ObservationsCfg()
    # ...
    
    # Mimic 特定配置
    recorder: RecorderManagerBaseCfg = RecorderManagerBaseCfg(
        dataset_export_mode=DatasetExportMode.EXPORT_ALL,
        dataset_export_dir_path="./datasets",
        dataset_filename="my_dataset.hdf5"
    )
```

### 启用 Subtask 观测

```python
@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        # 策略观测...
        pass
    
    @configclass
    class SubtaskCfg(ObsGroup):
        """子任务完成标志 (用于数据生成选择)"""
        
        grasp_object = ObsTerm(
            func=my_grasp_check,
            params={...}
        )
        
        lift_object = ObsTerm(
            func=my_lift_check,
            params={...}
        )
        
        def __post_init__(self):
            self.concatenate_terms = False
    
    policy: PolicyCfg = PolicyCfg()
    subtask_terms: SubtaskCfg = SubtaskCfg()
```

## 遥操作数据收集

### 设备配置

```python
# 键盘
from isaaclab.devices import Se3Keyboard

keyboard = Se3Keyboard(
    pos_sensitivity=0.01,
    rot_sensitivity=0.01
)

# SpaceMouse
from isaaclab.devices import Se3SpaceMouse

spacemouse = Se3SpaceMouse(
    pos_sensitivity=0.01,
    rot_sensitivity=0.01
)

# 游戏手柄
from isaaclab.devices import Se3Gamepad

gamepad = Se3Gamepad(
    pos_sensitivity=0.01,
    rot_sensitivity=0.01
)
```

### 遥操作脚本

```python
import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=str, default="keyboard")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

import torch
from isaaclab.devices import Se3Keyboard

def main():
    # 创建环境
    env = ManagerBasedRLMimicEnv(cfg=MyMimicEnvCfg())
    
    # 创建遥操作设备
    teleop = Se3Keyboard()
    teleop.reset()
    
    obs, _ = env.reset()
    
    while simulation_app.is_running():
        with torch.inference_mode():
            # 获取遥操作命令
            delta_pose, gripper_cmd = teleop.advance()
            
            # 构建动作
            actions = torch.zeros(env.num_envs, env.action_manager.total_action_dim)
            actions[:, :6] = torch.tensor(delta_pose)
            actions[:, 6] = gripper_cmd
            
            # 步进
            obs, reward, terminated, truncated, info = env.step(actions)
            
            # 检查是否保存演示
            if teleop.save_demo_requested():
                env.recorder_manager.save_current_episode()
    
    env.close()

if __name__ == "__main__":
    main()
    simulation_app.close()
```

## 自动数据生成

### 使用 DataGenerator

```python
from isaaclab_mimic.datagen import DataGenerator, DataGeneratorConfig

# 配置
config = DataGeneratorConfig(
    num_envs=256,
    num_demos=1000,
    output_path="./datasets/generated_demos.hdf5",
    
    # 选择策略
    selection_strategy="round_robin",  # 或 "random"
    
    # 数据增强
    enable_augmentation=True,
    augmentation_noise_scale=0.01
)

# 生成
generator = DataGenerator(env_cfg=MyMimicEnvCfg(), config=config)
generator.generate()
```

### 从现有演示生成变体

```python
from isaaclab_mimic.datagen import augment_demonstrations

# 加载原始演示
demos = load_demonstrations("./demos/human_demos.hdf5")

# 生成变体
augmented_demos = augment_demonstrations(
    demos,
    num_variations=10,
    noise_scale=0.01,
    randomize_start=True
)

# 保存
save_demonstrations(augmented_demos, "./demos/augmented_demos.hdf5")
```

## HDF5 数据格式

### 数据结构

```
dataset.hdf5
├── data/
│   ├── demo_0/
│   │   ├── obs/
│   │   │   ├── joint_pos (T, D)
│   │   │   ├── joint_vel (T, D)
│   │   │   └── ...
│   │   ├── actions (T, A)
│   │   ├── rewards (T,)
│   │   ├── dones (T,)
│   │   └── states (T, S)
│   ├── demo_1/
│   │   └── ...
│   └── ...
├── env_args/
│   └── ...
└── mask/
    └── ...
```

### 读取数据

```python
import h5py
import numpy as np

with h5py.File("dataset.hdf5", "r") as f:
    # 列出所有演示
    demo_keys = list(f["data"].keys())
    
    # 读取单个演示
    demo = f["data/demo_0"]
    obs = demo["obs/joint_pos"][:]
    actions = demo["actions"][:]
    
    # 获取元数据
    env_args = dict(f["env_args"].attrs)
```

## 与 robomimic 集成

### 转换为 robomimic 格式

```python
from isaaclab_mimic.utils import convert_to_robomimic

convert_to_robomimic(
    input_path="./datasets/isaaclab_demos.hdf5",
    output_path="./datasets/robomimic_demos.hdf5",
    env_name="MyEnv"
)
```

### 使用 robomimic 训练

```bash
# 训练 BC 策略
python scripts/train.py \
    --config configs/bc_rnn_image.json \
    --dataset ./datasets/robomimic_demos.hdf5
```

## 数据质量检查

### 可视化演示

```python
from isaaclab_mimic.utils import visualize_demonstration

visualize_demonstration(
    hdf5_path="./datasets/demos.hdf5",
    demo_key="demo_0",
    output_video="./demo_0.mp4"
)
```

### 统计分析

```python
from isaaclab_mimic.utils import analyze_dataset

stats = analyze_dataset("./datasets/demos.hdf5")
print(f"Total demos: {stats['num_demos']}")
print(f"Average length: {stats['avg_length']}")
print(f"Success rate: {stats['success_rate']}")
```

## 最佳实践

1. **多样化演示**: 收集不同初始条件的演示
2. **数据增强**: 使用噪声和变换增加数据多样性
3. **质量过滤**: 移除失败或异常的演示
4. **子任务标注**: 使用 subtask 观测自动标注关键事件
5. **平衡数据**: 确保成功/失败比例合理
