# RL 训练脚本指南

Isaac Lab 支持多个 RL 框架进行策略训练。

## 支持的框架

| 框架 | 特点 | 推荐场景 |
|------|------|----------|
| RSL-RL | 轻量级,快速迭代 | Locomotion |
| rl_games | 高性能,GPU 优化 | 通用 |
| SKRL | 模块化,易扩展 | 研究 |
| Stable-Baselines3 | 稳定,社区广泛 | 入门 |

## RSL-RL 训练

### 配置

```python
# agents/rsl_rl_ppo_cfg.py
from isaaclab_rl.rsl_rl import RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg

@configclass
class PPORunnerCfg:
    """RSL-RL PPO 配置"""
    
    # 算法
    algorithm = RslRlPpoAlgorithmCfg(
        clip_param=0.2,
        entropy_coef=0.01,
        learning_rate=1e-3,
        max_grad_norm=1.0,
        num_learning_epochs=5,
        num_mini_batches=4,
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        schedule="adaptive",
        desired_kl=0.01
    )
    
    # Actor-Critic 网络
    policy = RslRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_hidden_dims=[256, 256, 256],
        critic_hidden_dims=[256, 256, 256],
        activation="elu"
    )
    
    # 训练参数
    seed = 42
    device = "cuda:0"
    num_steps_per_env = 24
    max_iterations = 1000
    
    # 日志
    save_interval = 50
    experiment_name = "my_experiment"
    run_name = ""
    logger = "tensorboard"
```

### 训练脚本

```bash
# 训练
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Anymal-D-v0 \
    --num_envs 4096 \
    --headless

# 评估
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Velocity-Flat-Anymal-D-v0 \
    --num_envs 32 \
    --checkpoint /path/to/model.pt
```

## rl_games 训练

### 配置

```yaml
# agents/rl_games_ppo_cfg.yaml
params:
  seed: 42
  
  algo:
    name: a2c_continuous
    
  model:
    name: continuous_a2c_logstd
    
  network:
    name: actor_critic
    separate: False
    space:
      continuous:
        mu_activation: None
        sigma_activation: None
        mu_init:
          name: default
        sigma_init:
          name: const_initializer
          val: 0.0
        fixed_sigma: True
    mlp:
      units: [256, 128, 64]
      activation: elu
      d2rl: False
      initializer:
        name: default
      regularizer:
        name: None
        
  config:
    name: MyTask
    env_name: rlgpu
    multi_gpu: False
    ppo: True
    mixed_precision: False
    normalize_input: True
    normalize_value: True
    value_bootstrap: True
    num_actors: 4096
    reward_shaper:
      scale_value: 1.0
    normalize_advantage: True
    gamma: 0.99
    tau: 0.95
    learning_rate: 3e-4
    lr_schedule: adaptive
    kl_threshold: 0.008
    score_to_win: 20000
    max_epochs: 500
    save_best_after: 100
    save_frequency: 50
    print_stats: True
    grad_norm: 1.0
    entropy_coef: 0.0
    truncate_grads: True
    e_clip: 0.2
    horizon_length: 24
    minibatch_size: 16384
    mini_epochs: 5
    critic_coef: 2
    bounds_loss_coef: 0.0
```

### 训练脚本

```bash
# 训练
./isaaclab.sh -p scripts/reinforcement_learning/rl_games/train.py \
    --task Isaac-Lift-Cube-Franka-v0 \
    --num_envs 4096 \
    --headless

# 评估
./isaaclab.sh -p scripts/reinforcement_learning/rl_games/play.py \
    --task Isaac-Lift-Cube-Franka-v0 \
    --num_envs 32 \
    --checkpoint /path/to/nn/model.pth
```

## SKRL 训练

### 配置

```python
# agents/skrl_ppo_cfg.py
from skrl.agents.torch.ppo import PPO_DEFAULT_CONFIG

PPO_CFG = PPO_DEFAULT_CONFIG.copy()
PPO_CFG["rollouts"] = 24
PPO_CFG["learning_epochs"] = 5
PPO_CFG["mini_batches"] = 4
PPO_CFG["discount_factor"] = 0.99
PPO_CFG["lambda"] = 0.95
PPO_CFG["learning_rate"] = 1e-3
PPO_CFG["learning_rate_scheduler"] = "adaptive"
PPO_CFG["kl_threshold"] = 0.008
PPO_CFG["entropy_loss_scale"] = 0.0
PPO_CFG["value_loss_scale"] = 2.0
PPO_CFG["clip_predicted_values"] = True
PPO_CFG["grad_norm_clip"] = 1.0
```

### 训练脚本

```bash
./isaaclab.sh -p scripts/reinforcement_learning/skrl/train.py \
    --task Isaac-Reach-Franka-v0 \
    --num_envs 4096 \
    --headless
```

## Stable-Baselines3 训练

```bash
./isaaclab.sh -p scripts/reinforcement_learning/sb3/train.py \
    --task Isaac-Cartpole-v0 \
    --num_envs 1024 \
    --headless
```

## 自定义训练脚本

```python
import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--task", type=str, default="Isaac-Lift-Cube-Franka-v0")
parser.add_argument("--num_envs", type=int, default=4096)
parser.add_argument("--max_iterations", type=int, default=1000)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

import gymnasium as gym
import torch
from rsl_rl.runners import OnPolicyRunner

def main():
    # 创建环境
    env = gym.make(
        args.task,
        num_envs=args.num_envs,
        device=args.device
    )
    
    # 创建训练器
    runner = OnPolicyRunner(
        env=env,
        train_cfg=train_cfg,
        log_dir="./logs",
        device=args.device
    )
    
    # 训练
    runner.learn(num_learning_iterations=args.max_iterations)
    
    env.close()

if __name__ == "__main__":
    main()
    simulation_app.close()
```

## Hydra 配置

Isaac Lab 支持 Hydra 配置系统:

```bash
# 使用 Hydra 覆盖参数
./isaaclab.sh -p scripts/train.py \
    task=Isaac-Lift-Cube-Franka-v0 \
    num_envs=4096 \
    train.ppo.learning_rate=0.001 \
    train.ppo.entropy_coef=0.01
```

## 分布式训练

### 多 GPU

```bash
# 使用 torchrun
torchrun --nproc_per_node=4 scripts/train.py \
    --task Isaac-Lift-Cube-Franka-v0 \
    --num_envs 16384
```

### Ray 集群

```bash
# 提交到 Ray 集群
./isaaclab.sh -p scripts/reinforcement_learning/ray/submit_job.py \
    --task Isaac-Lift-Cube-Franka-v0 \
    --num_envs 32768 \
    --cluster configs/cluster.yaml
```

## 训练技巧

### 1. 超参数调优

```python
# 使用 Ray Tune
from ray import tune

config = {
    "learning_rate": tune.loguniform(1e-5, 1e-2),
    "entropy_coef": tune.uniform(0.0, 0.1),
    "num_mini_batches": tune.choice([4, 8, 16])
}

tune.run(train_fn, config=config, num_samples=50)
```

### 2. 课程学习

```python
@configclass
class CurriculumCfg:
    terrain_difficulty = CurriculumTermCfg(
        func=increase_terrain_difficulty,
        params={"start_level": 0, "max_level": 10}
    )
```

### 3. 奖励调试

```python
# 记录各项奖励
env.extras["log"] = {
    "reward/reaching": reaching_reward.mean(),
    "reward/lifting": lifting_reward.mean(),
    "reward/action_rate": action_rate.mean()
}
```

## TensorBoard 监控

```bash
# 启动 TensorBoard
tensorboard --logdir ./logs

# 常见指标
# - episode_reward: 平均回报
# - episode_length: 平均长度
# - policy_loss: 策略损失
# - value_loss: 价值函数损失
# - entropy: 策略熵
# - kl_divergence: KL 散度
```
