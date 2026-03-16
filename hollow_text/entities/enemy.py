"""
敌人实体类 - 包含敌人的AI行为和战斗模式
"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from .base import Entity, EntityType


class EnemyAction(Enum):
    """敌人行动类型"""
    IDLE = "idle"           # 待机
    CHARGE = "charge"       # 蓄力（预示攻击）
    ATTACK = "attack"       # 攻击
    DEFEND = "defend"       # 防御
    REST = "rest"           # 后摇/休息
    STUNNED = "stunned"     # 硬直


@dataclass
class EnemyPattern:
    """敌人行为模式"""
    name: str
    sequence: List[EnemyAction]
    current_index: int = 0

    def get_next_action(self) -> EnemyAction:
        """获取下一个行动"""
        action = self.sequence[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.sequence)
        return action

    def reset(self) -> None:
        """重置模式"""
        self.current_index = 0


@dataclass
class Enemy(Entity):
    """敌人实体"""
    entity_type: EntityType = field(default=EntityType.ENEMY, init=False)
    description: str = "一个堕落的生物"
    souls_reward: int = 50             # 击杀奖励魂
    action_pattern: Optional[EnemyPattern] = None
    current_action: EnemyAction = field(default=EnemyAction.IDLE, init=False)
    charge_turns: int = field(default=0, init=False)  # 蓄力回合数

    # 覆盖基类默认值
    hp: int = field(default=50)
    max_hp: int = field(default=50)
    stamina: int = field(default=15)
    max_stamina: int = field(default=15)
    attack_power: int = field(default=12)
    defense: int = field(default=3)

    def __post_init__(self):
        super().__post_init__()
        if self.action_pattern is None:
            # 默认行为模式：待机 -> 蓄力 -> 攻击 -> 后摇
            self.action_pattern = EnemyPattern(
                name="default",
                sequence=[
                    EnemyAction.IDLE,
                    EnemyAction.CHARGE,
                    EnemyAction.ATTACK,
                    EnemyAction.REST
                ]
            )

    def decide_action(self) -> EnemyAction:
        """决定下一个行动"""
        if self.action_pattern:
            self.current_action = self.action_pattern.get_next_action()
            if self.current_action == EnemyAction.CHARGE:
                self.charge_turns = 1  # 蓄力1回合后攻击
        return self.current_action

    def get_action_description(self) -> str:
        """获取当前行动的描述"""
        descriptions = {
            EnemyAction.IDLE: "敌人正在观察你的动作...",
            EnemyAction.CHARGE: "【警告】敌人正在蓄力！准备攻击！",
            EnemyAction.ATTACK: "敌人发起攻击！",
            EnemyAction.DEFEND: "敌人举起盾牌防御。",
            EnemyAction.REST: "敌人动作迟缓，似乎在喘息...",
            EnemyAction.STUNNED: "敌人陷入了硬直！"
        }
        return descriptions.get(self.current_action, "敌人行动不明")

    def is_vulnerable(self) -> bool:
        """判断敌人是否处于脆弱状态"""
        return self.current_action in [EnemyAction.CHARGE, EnemyAction.REST, EnemyAction.STUNNED]

    def calculate_attack_damage(self) -> int:
        """计算攻击伤害"""
        base_damage = self.attack_power
        # 蓄力攻击造成额外伤害
        if self.current_action == EnemyAction.CHARGE:
            return int(base_damage * 1.5)
        return base_damage


# 预定义的敌人类型
def create_hollow_soldier() -> Enemy:
    """创建空洞士兵 - 基础敌人"""
    return Enemy(
        name="空洞士兵",
        description="一个失去了心智的士兵，仅剩下战斗的本能。",
        hp=40,
        max_hp=40,
        attack_power=10,
        defense=3,
        souls_reward=30,
        action_pattern=EnemyPattern(
            name="soldier",
            sequence=[
                EnemyAction.IDLE,
                EnemyAction.ATTACK,
                EnemyAction.REST
            ]
        )
    )


def create_rotted_knight() -> Enemy:
    """创建腐朽骑士 - 中等敌人"""
    return Enemy(
        name="腐朽骑士",
        description="曾经是英勇的骑士，现在只剩下腐朽的铠甲和无尽的仇恨。",
        hp=80,
        max_hp=80,
        attack_power=18,
        defense=8,
        stamina=25,
        max_stamina=25,
        souls_reward=80,
        action_pattern=EnemyPattern(
            name="knight",
            sequence=[
                EnemyAction.IDLE,
                EnemyAction.CHARGE,
                EnemyAction.ATTACK,
                EnemyAction.ATTACK,
                EnemyAction.REST
            ]
        )
    )


def create_dark_wraith() -> Enemy:
    """创建深渊幽灵 - 精英敌人"""
    return Enemy(
        name="深渊幽灵",
        description="从深渊中爬出的黑暗存在，它渴望吞噬一切光明。",
        hp=120,
        max_hp=120,
        attack_power=25,
        defense=5,
        stamina=30,
        max_stamina=30,
        souls_reward=150,
        action_pattern=EnemyPattern(
            name="wraith",
            sequence=[
                EnemyAction.CHARGE,
                EnemyAction.ATTACK,
                EnemyAction.ATTACK,
                EnemyAction.ATTACK,
                EnemyAction.REST,
                EnemyAction.IDLE
            ]
        )
    )
