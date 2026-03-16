"""
地图管理 - 管理游戏世界中的所有房间
"""
from typing import Dict, Optional
from .room import Room, RoomType
from entities.enemy import create_hollow_soldier, create_rotted_knight, create_dark_wraith


class GameMap:
    """游戏地图"""

    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.start_room_id: Optional[str] = None

    def add_room(self, room: Room, is_start: bool = False) -> None:
        """添加房间"""
        self.rooms[room.id] = room
        if is_start:
            self.start_room_id = room.id

    def get_room(self, room_id: str) -> Optional[Room]:
        """获取房间"""
        return self.rooms.get(room_id)

    def get_start_room(self) -> Optional[Room]:
        """获取起始房间"""
        if self.start_room_id:
            return self.rooms.get(self.start_room_id)
        return None

    def connect_rooms(self, room1_id: str, room2_id: str,
                      direction1: str, direction2: str) -> bool:
        """连接两个房间"""
        if room1_id not in self.rooms or room2_id not in self.rooms:
            return False

        self.rooms[room1_id].add_connection(direction1, room2_id)
        self.rooms[room2_id].add_connection(direction2, room1_id)
        return True

    def respawn_all_enemies(self) -> None:
        """重生所有房间的敌人（篝火休息时调用）"""
        for room in self.rooms.values():
            room.respawn_enemies()


def create_starter_dungeon() -> GameMap:
    """创建初始地牢 - 新手教程关卡"""
    game_map = GameMap()

    # 入口 - 篝火房间
    entrance = Room(
        id="entrance",
        name="被遗忘的入口",
        description="""
你发现自己站在一个古老建筑的入口处。
破败的石柱上刻满了看不懂的符文，空气中弥漫着腐朽的气息。
一堆篝火在角落里静静地燃烧着，这是这个黑暗世界中唯一的光源。

你不记得自己是如何来到这里的，但你知道必须继续前进...
""",
        room_type=RoomType.BONFIRE
    )
    game_map.add_room(entrance, is_start=True)

    # 第一个走廊
    corridor1 = Room(
        id="corridor_1",
        name="昏暗走廊",
        description="""
一条狭长的走廊，墙壁上的火把早已熄灭。
你的脚步声在空旷的走廊中回响，仿佛有什么东西在暗处注视着你。
地上散落着生锈的武器和破碎的盾牌，这里曾经发生过激烈的战斗。
""",
        room_type=RoomType.NORMAL
    )
    corridor1.add_enemy(create_hollow_soldier())
    game_map.add_room(corridor1)

    # 第一个大厅
    hall1 = Room(
        id="hall_1",
        name="战士大厅",
        description="""
一个宽敞的大厅，墙壁上挂满了褪色的旗帜和锈蚀的盔甲。
大厅中央有一座断裂的雕像，曾经可能是一位伟大的战士。
阴影中似乎有什么东西在移动...
""",
        room_type=RoomType.NORMAL
    )
    hall1.add_enemy(create_hollow_soldier())
    hall1.add_enemy(create_hollow_soldier())
    game_map.add_room(hall1)

    # 侧室 - 宝藏房间（暂时空）
    side_chamber = Room(
        id="side_chamber",
        name="封印的宝库",
        description="""
一个小型的石室，门上刻着古老的封印。
房间中央有一个石台，上面空无一物。
也许曾经这里放着什么珍贵的东西...
""",
        room_type=RoomType.TREASURE
    )
    game_map.add_room(side_chamber)

    # 篝火房间2
    bonfire2 = Room(
        id="bonfire_2",
        name="深渊前厅",
        description="""
这里比其他地方更加温暖。一堆篝火在中央燃烧着，
周围有一些古老的家具残骸。看起来曾经有人在这里休息过。
墙上刻着一行字："不要贪婪，耐心是生存的关键。"
""",
        room_type=RoomType.BONFIRE
    )
    game_map.add_room(bonfire2)

    # 骑士走廊
    corridor2 = Room(
        id="corridor_2",
        name="骑士长廊",
        description="""
两侧站立着沉默的盔甲，它们仿佛在注视着你。
地板上有一道裂缝，从中散发着一丝寒意。
这里的敌人比你之前遇到的更加强大...
""",
        room_type=RoomType.NORMAL
    )
    corridor2.add_enemy(create_rotted_knight())
    game_map.add_room(corridor2)

    # Boss房间
    boss_room = Room(
        id="boss_room",
        name="深渊守卫之间",
        description="""
一个巨大的圆形大厅，天花板高得看不见顶。
中央矗立着一个高大的身影，它的眼睛在黑暗中闪烁着红光。
这是深渊的守护者，你必须战胜它才能继续前进...
""",
        room_type=RoomType.BOSS
    )
    boss_room.add_enemy(create_dark_wraith())
    game_map.add_room(boss_room)

    # 连接房间
    game_map.connect_rooms("entrance", "corridor_1", "北", "南")
    game_map.connect_rooms("corridor_1", "hall_1", "北", "南")
    game_map.connect_rooms("hall_1", "side_chamber", "西", "东")
    game_map.connect_rooms("hall_1", "bonfire_2", "北", "南")
    game_map.connect_rooms("bonfire_2", "corridor_2", "北", "南")
    game_map.connect_rooms("corridor_2", "boss_room", "北", "南")

    return game_map
