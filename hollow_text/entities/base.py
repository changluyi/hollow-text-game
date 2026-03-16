"""
基础实体类 - 所有游戏实体的基类
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class EntityType(Enum):
    """实体类型枚举"""
    PLAYER = "player"
    ENEMY = "enemy"
    NPC = "npc"


@dataclass
class Entity:
    """基础实体类"""
    name: str
    entity_type: EntityType
    hp: int = 100
    max_hp: int = 100
    stamina: int = 20
    max_stamina: int = 20
    attack_power: int = 10
    defense: int = 5
    is_alive: bool = True

    def take_damage(self, damage: int) -> int:
        """受到伤害，返回实际伤害值"""
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        if self.hp <= 0:
            self.is_alive = False
        return actual_damage

    def heal(self, amount: int) -> int:
        """恢复生命值，返回实际恢复量"""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def use_stamina(self, amount: int) -> bool:
        """消耗精力，返回是否成功"""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False

    def recover_stamina(self, amount: int) -> int:
        """恢复精力，返回实际恢复量"""
        old_stamina = self.stamina
        self.stamina = min(self.max_stamina, self.stamina + amount)
        return self.stamina - old_stamina

    def __post_init__(self):
        """初始化后验证"""
        self.max_hp = max(1, self.max_hp)
        self.max_stamina = max(1, self.max_stamina)
        if self.hp <= 0:
            self.hp = self.max_hp
        if self.stamina <= 0:
            self.stamina = self.max_stamina
