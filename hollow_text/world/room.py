"""
房间定义 - 游戏世界的基本单位
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

from entities.enemy import Enemy


class RoomType(Enum):
    """房间类型"""
    NORMAL = "normal"         # 普通房间
    BONFIRE = "bonfire"       # 篝火（存档点）
    BOSS = "boss"             # Boss房间
    TREASURE = "treasure"     # 宝藏房间
    ENTRANCE = "entrance"     # 入口


@dataclass
class Room:
    """房间类"""
    id: str
    name: str
    description: str
    short_description: str = ""
    room_type: RoomType = RoomType.NORMAL
    connections: Dict[str, str] = field(default_factory=dict)  # 方向 -> 房间ID
    enemies: List[Enemy] = field(default_factory=list)
    has_bloodstain: bool = False  # 是否有玩家血迹（掉落的魂）

    def __post_init__(self):
        if not self.short_description:
            self.short_description = self.description[:50] + "..."

    def add_connection(self, direction: str, room_id: str) -> None:
        """添加连接"""
        self.connections[direction] = room_id

    def add_enemy(self, enemy: Enemy) -> None:
        """添加敌人"""
        self.enemies.append(enemy)

    def get_alive_enemies(self) -> List[Enemy]:
        """获取存活的敌人"""
        return [e for e in self.enemies if e.is_alive]

    def has_alive_enemies(self) -> bool:
        """检查是否有存活的敌人"""
        return len(self.get_alive_enemies()) > 0

    def respawn_enemies(self) -> None:
        """重生所有敌人"""
        for enemy in self.enemies:
            enemy.hp = enemy.max_hp
            enemy.stamina = enemy.max_stamina
            enemy.is_alive = True
            if enemy.action_pattern:
                enemy.action_pattern.reset()

    def clear_bloodstain(self) -> None:
        """清除血迹"""
        self.has_bloodstain = False
