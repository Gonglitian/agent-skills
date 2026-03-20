# 创建新环境步骤指南

## Manager-Based 环境创建流程

### 步骤 1: 创建场景配置

```python
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.assets import ArticulationCfg, RigidObjectCfg, AssetBaseCfg
import isaaclab.sim as sim_utils
from isaaclab.utils import configclass

@configclass
class MySceneCfg(InteractiveSceneCfg):
    """场景配置"""
    
    # 1. 机器人
    robot: ArticulationCfg = ArticulationCfg(
        prim_path="{ENV_REGEX_NS}/Robot",
        spawn=sim_utils.UsdFileCfg(
            usd_path="path/to/robot.usd",
            rigid_props=sim_utils.RigidBodyPropertiesCfg(),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg()
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.0),
            joint_pos={"joint.*": 0.0}
        ),
        actuators={"arm": ImplicitActuatorCfg(...)}
    )
    
    # 2. 可交互物体
    object: RigidObjectCfg = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Object",
        spawn=sim_utils.CuboidCfg(size=(0.05, 0.05, 0.05)),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(0.5, 0.0, 0.1))
    )
    
    # 3. 静态物体
    table = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Table",
        spawn=sim_utils.UsdFileCfg(usd_path="path/to/table.usd"),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.5, 0.0, 0.0))
    )
    
    # 4. 地面 (全局)
    ground = AssetBaseCfg(
        prim_path="/World/Ground",
        spawn=sim_utils.GroundPlaneCfg(),
        collision_group=-1  # 全局碰撞组
    )
    
    # 5. 灯光
    light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=3000.0)
    )
```

### 步骤 2: 定义动作

```python
import isaaclab.envs.mdp as mdp

@configclass
class ActionsCfg:
    """动作配置"""
    
    # 手臂关节控制
    arm_action: mdp.JointPositionActionCfg = mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=["joint1", "joint2", "joint3", "joint4", "joint5", "joint6", "joint7"],
        scale=1.0,
        use_default_offset=True
    )
    
    # 夹爪控制
    gripper_action: mdp.BinaryJointPositionActionCfg = mdp.BinaryJointPositionActionCfg(
        asset_name="robot",
        joint_names=["finger_joint.*"],
        open_command_expr={"finger_joint.*": 0.04},
        close_command_expr={"finger_joint.*": 0.0}
    )
```

### 步骤 3: 定义观测

```python
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import SceneEntityCfg

@configclass
class ObservationsCfg:
    """观测配置"""
    
    @configclass
    class PolicyCfg(ObsGroup):
        """策略观测组"""
        
        # 关节状态
        joint_pos = ObsTerm(func=mdp.joint_pos_rel)
        joint_vel = ObsTerm(func=mdp.joint_vel_rel)
        
        # 物体状态
        object_pos = ObsTerm(
            func=mdp.root_pos_w,
            params={"asset_cfg": SceneEntityCfg("object")}
        )
        object_quat = ObsTerm(
            func=mdp.root_quat_w,
            params={"asset_cfg": SceneEntityCfg("object")}
        )
        
        # 上一步动作
        actions = ObsTerm(func=mdp.last_action)
        
        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True
    
    policy: PolicyCfg = PolicyCfg()
```

### 步骤 4: 定义奖励 (RL 环境)

```python
from isaaclab.managers import RewardTermCfg as RewTerm

@configclass
class RewardsCfg:
    """奖励配置"""
    
    # 任务相关奖励
    reaching = RewTerm(
        func=my_reaching_reward,
        weight=1.0,
        params={"object_cfg": SceneEntityCfg("object")}
    )
    
    # 正则化惩罚
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-0.01)
    joint_vel = RewTerm(func=mdp.joint_vel_l2, weight=-0.0001)
```

### 步骤 5: 定义终止条件 (RL 环境)

```python
from isaaclab.managers import TerminationTermCfg as DoneTerm

@configclass
class TerminationsCfg:
    """终止条件"""
    
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    
    object_dropped = DoneTerm(
        func=mdp.root_height_below_minimum,
        params={"asset_cfg": SceneEntityCfg("object"), "minimum_height": -0.1}
    )
```

### 步骤 6: 定义事件

```python
from isaaclab.managers import EventTermCfg as EventTerm

@configclass
class EventsCfg:
    """事件配置"""
    
    reset_robot = EventTerm(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot"),
            "position_range": (-0.1, 0.1),
            "velocity_range": (0.0, 0.0)
        }
    )
    
    reset_object = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("object"),
            "pose_range": {"x": (-0.1, 0.1), "y": (-0.1, 0.1)},
            "velocity_range": {}
        }
    )
```

### 步骤 7: 组合环境配置

```python
from isaaclab.envs import ManagerBasedRLEnvCfg

@configclass
class MyEnvCfg(ManagerBasedRLEnvCfg):
    """完整环境配置"""
    
    scene: MySceneCfg = MySceneCfg(num_envs=1024, env_spacing=2.5)
    actions: ActionsCfg = ActionsCfg()
    observations: ObservationsCfg = ObservationsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventsCfg = EventsCfg()
    
    # 可选
    commands = None
    curriculum = None
    
    def __post_init__(self):
        self.decimation = 4
        self.episode_length_s = 10.0
        self.sim.dt = 0.01
        self.sim.render_interval = 2
        
        self.viewer.eye = (3.0, 3.0, 3.0)
        self.viewer.lookat = (0.0, 0.0, 0.5)
```

### 步骤 8: 注册环境

```python
import gymnasium as gym
from isaaclab.envs import ManagerBasedRLEnv

# 注册
gym.register(
    id="MyEnv-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    kwargs={"cfg": MyEnvCfg()}
)

# 使用
env = gym.make("MyEnv-v0")
```

### 步骤 9: 运行脚本

```python
import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--num_envs", type=int, default=16)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

# 导入
import torch
from my_envs import MyEnvCfg
from isaaclab.envs import ManagerBasedRLEnv

def main():
    env_cfg = MyEnvCfg()
    env_cfg.scene.num_envs = args.num_envs
    env = ManagerBasedRLEnv(cfg=env_cfg)
    
    obs, _ = env.reset()
    
    while simulation_app.is_running():
        with torch.inference_mode():
            actions = torch.randn(env.num_envs, env.action_manager.total_action_dim, device=env.device)
            obs, reward, terminated, truncated, info = env.step(actions)
    
    env.close()

if __name__ == "__main__":
    main()
    simulation_app.close()
```

## Direct 环境创建流程

### 步骤 1-2: 定义配置和环境类

```python
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg

@configclass
class MyDirectEnvCfg(DirectRLEnvCfg):
    decimation = 2
    episode_length_s = 10.0
    action_space = 7
    observation_space = 20
    
    robot_cfg: ArticulationCfg = ...
    object_cfg: RigidObjectCfg = ...

class MyDirectEnv(DirectRLEnv):
    cfg: MyDirectEnvCfg
    
    def __init__(self, cfg, render_mode=None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)
        # 初始化
    
    def _setup_scene(self):
        # 创建资产
        self.robot = Articulation(self.cfg.robot_cfg)
        self.object = RigidObject(self.cfg.object_cfg)
        
        # 克隆环境
        self.scene.clone_environments()
        
        # 注册
        self.scene.articulations["robot"] = self.robot
        self.scene.rigid_objects["object"] = self.object
    
    def _pre_physics_step(self, actions):
        self.actions = actions.clone()
    
    def _apply_action(self):
        self.robot.set_joint_position_target(self.actions)
    
    def _get_observations(self):
        return {"policy": self._compute_obs()}
    
    def _get_rewards(self):
        return self._compute_rewards()
    
    def _get_dones(self):
        terminated = ...
        truncated = self.episode_length_buf >= self.max_episode_length - 1
        return terminated, truncated
    
    def _reset_idx(self, env_ids):
        super()._reset_idx(env_ids)
        # 重置逻辑
```

## 检查清单

创建新环境时确保:

- [ ] 场景配置完整 (机器人、物体、地面、灯光)
- [ ] 动作空间正确定义
- [ ] 观测包含任务所需信息
- [ ] 奖励函数鼓励期望行为
- [ ] 终止条件合理 (超时 + 异常情况)
- [ ] 重置逻辑正确随机化
- [ ] 仿真参数合适 (dt, decimation)
- [ ] 测试单环境运行正常
- [ ] 测试多环境并行正常
