"""
游戏状态管理 - 管理游戏的整体状态
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from entities.player import Player
from world.room import Room


class GameMode(Enum):
    """游戏模式"""
    MENU = "menu"               # 主菜单
    EXPLORATION = "exploration" # 探索模式
    COMBAT = "combat"           # 战斗模式
    BONFIRE = "bonfire"         # 篝火模式
    LEVEL_UP = "level_up"       # 升级模式
    GAME_OVER = "game_over"     # 游戏结束


@dataclass
class GameState:
    """游戏状态"""
    mode: GameMode = GameMode.MENU
    player: Optional[Player] = None
    current_room: Optional[Room] = None
    is_running: bool = True
    turns_elapsed: int = 0
    deaths: int = 0
    souls_collected: int = 0
    enemies_killed: int = 0

    def create_player(self, name: str = "无名的亡者") -> Player:
        """创建玩家"""
        self.player = Player(name=name)
        return self.player

    def set_current_room(self, room: Room) -> None:
        """设置当前房间"""
        self.current_room = room

    def set_mode(self, mode: GameMode) -> None:
        """设置游戏模式"""
        self.mode = mode

    def increment_turn(self) -> None:
        """增加回合数"""
        self.turns_elapsed += 1

    def record_death(self) -> None:
        """记录死亡"""
        self.deaths += 1

    def record_souls(self, amount: int) -> None:
        """记录获得的魂"""
        self.souls_collected += amount

    def record_kill(self) -> None:
        """记录击杀"""
        self.enemies_killed += 1

    def get_stats_summary(self) -> str:
        """获取游戏统计摘要"""
        return f"""
游戏统计:
  回合数: {self.turns_elapsed}
  死亡次数: {self.deaths}
  获得魂总数: {self.souls_collected}
  击杀敌人: {self.enemies_killed}
"""
