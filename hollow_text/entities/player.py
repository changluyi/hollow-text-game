"""
玩家实体类 - 包含玩家特有的属性和行为
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple
from .base import Entity, EntityType


@dataclass
class PlayerStats:
    """玩家属性"""
    strength: int = 10      # 力量 - 影响物理伤害
    dexterity: int = 10     # 敏捷 - 影响闪避和暴击
    intelligence: int = 10  # 智力 - 影响法术伤害
    faith: int = 10         # 信仰 - 影响奇迹和恢复


@dataclass
class Player(Entity):
    """玩家实体"""
    entity_type: EntityType = field(default=EntityType.PLAYER, init=False)
    souls: int = 0                      # 魂（经验+货币）
    level: int = 1                      # 等级
    stats: PlayerStats = field(default_factory=PlayerStats)
    lost_souls_location: Optional[Tuple[int, int]] = None  # 死亡掉落魂的位置
    lost_souls_amount: int = 0          # 掉落的魂数量

    # 覆盖基类默认值
    hp: int = field(default=100)
    max_hp: int = field(default=100)
    stamina: int = field(default=20)
    max_stamina: int = field(default=20)
    attack_power: int = field(default=15)
    defense: int = field(default=5)

    def gain_souls(self, amount: int) -> None:
        """获得魂"""
        self.souls += amount

    def spend_souls(self, amount: int) -> bool:
        """花费魂，返回是否成功"""
        if self.souls >= amount:
            self.souls -= amount
            return True
        return False

    def drop_souls(self, location: Tuple[int, int]) -> None:
        """死亡时掉落魂"""
        self.lost_souls_location = location
        self.lost_souls_amount = self.souls
        self.souls = 0

    def recover_souls(self) -> int:
        """取回掉落的魂，返回取回数量"""
        amount = self.lost_souls_amount
        self.lost_souls_location = None
        self.lost_souls_amount = 0
        self.souls += amount
        return amount

    def level_up(self, stat: str) -> bool:
        """升级属性
        stat: 'strength', 'dexterity', 'intelligence', 'faith'
        """
        cost = self.get_level_up_cost()
        if self.spend_souls(cost):
            self.level += 1
            if stat == 'strength':
                self.stats.strength += 1
                self.attack_power += 2
            elif stat == 'dexterity':
                self.stats.dexterity += 1
            elif stat == 'intelligence':
                self.stats.intelligence += 1
            elif stat == 'faith':
                self.stats.faith += 1
            return True
        return False

    def get_level_up_cost(self) -> int:
        """获取升级所需魂数"""
        return self.level * 100

    def calculate_attack_damage(self) -> int:
        """计算攻击伤害"""
        base_damage = self.attack_power
        strength_bonus = int(self.stats.strength * 0.5)
        return base_damage + strength_bonus

    def calculate_dodge_chance(self) -> float:
        """计算闪避概率"""
        base_chance = 0.1
        dex_bonus = self.stats.dexterity * 0.02
        return min(0.5, base_chance + dex_bonus)  # 最高 50%

    def respawn(self) -> None:
        """从篝火重生"""
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.is_alive = True
