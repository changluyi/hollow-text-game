"""
输入处理 - 处理用户输入
"""
from enum import Enum
from typing import Optional, Tuple


class GameInput(Enum):
    """游戏输入枚举"""
    # 移动
    NORTH = "n"
    SOUTH = "s"
    EAST = "e"
    WEST = "w"

    # 战斗
    ATTACK = "a"
    HEAVY_ATTACK = "h"
    DEFEND = "d"
    DODGE = "o"
    FLEE = "f"

    # 系统
    STATUS = "i"
    LOG = "l"
    REST = "r"
    LEAVE = "l"
    BACK = "q"
    QUIT = "q"

    # 升级
    UPGRADE_STR = "1"
    UPGRADE_DEX = "2"
    UPGRADE_INT = "3"
    UPGRADE_FAI = "4"

    # 菜单
    NEW_GAME = "1"
    CONTROLS = "2"
    ABOUT = "3"

    UNKNOWN = ""


class InputHandler:
    """输入处理器"""

    @staticmethod
    def get_input() -> str:
        """获取用户输入"""
        try:
            return input("> ").strip().lower()
        except EOFError:
            return "q"
        except KeyboardInterrupt:
            return "q"

    @staticmethod
    def parse_exploration_input(raw_input: str) -> GameInput:
        """解析探索模式输入"""
        input_map = {
            "n": GameInput.NORTH,
            "北": GameInput.NORTH,
            "s": GameInput.SOUTH,
            "南": GameInput.SOUTH,
            "e": GameInput.EAST,
            "东": GameInput.EAST,
            "w": GameInput.WEST,
            "西": GameInput.WEST,
            "i": GameInput.STATUS,
            "l": GameInput.LOG,
            "r": GameInput.REST,
            "q": GameInput.QUIT,
        }
        return input_map.get(raw_input.lower(), GameInput.UNKNOWN)

    @staticmethod
    def parse_combat_input(raw_input: str) -> GameInput:
        """解析战斗模式输入"""
        input_map = {
            "a": GameInput.ATTACK,
            "攻击": GameInput.ATTACK,
            "h": GameInput.HEAVY_ATTACK,
            "重击": GameInput.HEAVY_ATTACK,
            "d": GameInput.DEFEND,
            "防御": GameInput.DEFEND,
            "o": GameInput.DODGE,
            "闪避": GameInput.DODGE,
            "f": GameInput.FLEE,
            "逃跑": GameInput.FLEE,
        }
        return input_map.get(raw_input.lower(), GameInput.UNKNOWN)

    @staticmethod
    def parse_bonfire_input(raw_input: str) -> GameInput:
        """解析篝火模式输入"""
        input_map = {
            "r": GameInput.REST,
            "休息": GameInput.REST,
            "u": GameInput.LOG,  # 用 LOG 代表升级（临时）
            "升级": GameInput.LOG,
            "l": GameInput.LEAVE,
            "离开": GameInput.LEAVE,
            "q": GameInput.LEAVE,
        }
        return input_map.get(raw_input.lower(), GameInput.UNKNOWN)

    @staticmethod
    def parse_level_up_input(raw_input: str) -> Tuple[GameInput, Optional[str]]:
        """解析升级输入，返回 (输入类型, 属性名)"""
        input_map = {
            "1": (GameInput.UPGRADE_STR, "strength"),
            "2": (GameInput.UPGRADE_DEX, "dexterity"),
            "3": (GameInput.UPGRADE_INT, "intelligence"),
            "4": (GameInput.UPGRADE_FAI, "faith"),
            "q": (GameInput.BACK, None),
        }
        return input_map.get(raw_input.lower(), (GameInput.UNKNOWN, None))

    @staticmethod
    def parse_menu_input(raw_input: str) -> GameInput:
        """解析菜单输入"""
        input_map = {
            "1": GameInput.NEW_GAME,
            "2": GameInput.CONTROLS,
            "3": GameInput.ABOUT,
            "q": GameInput.QUIT,
        }
        return input_map.get(raw_input.lower(), GameInput.UNKNOWN)

    @staticmethod
    def wait_for_input() -> None:
        """等待用户输入（任意键继续）"""
        try:
            input("\n按回车键继续...")
        except (EOFError, KeyboardInterrupt):
            pass
