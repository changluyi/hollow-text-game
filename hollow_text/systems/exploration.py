"""
探索系统 - 处理玩家在世界中的移动和探索
"""
from typing import Optional, List
from entities.player import Player
from world.room import Room, RoomType


class ExplorationSystem:
    """探索系统"""

    def __init__(self):
        self.current_room: Optional[Room] = None
        self.visited_rooms: set[str] = set()

    def enter_room(self, room: Room, player: Player) -> tuple[bool, str]:
        """进入房间"""
        self.current_room = room
        is_first_visit = room.id not in self.visited_rooms

        if is_first_visit:
            self.visited_rooms.add(room.id)
            return True, self._describe_first_entry(room)

        return True, self._describe_room(room)

    def _describe_first_entry(self, room: Room) -> str:
        """首次进入房间的描述"""
        desc = f"\n{'='*50}\n"
        desc += f"【{room.name}】\n"
        desc += f"{'='*50}\n\n"
        desc += room.description
        desc += "\n"

        if room.enemies:
            desc += f"\n⚠️ 你感受到了危险的气息... {len(room.enemies)} 个敌人潜伏在阴影中。"

        if room.room_type == RoomType.BONFIRE:
            desc += "\n🔥 一堆篝火静静地燃烧着，散发着温暖的光芒。"

        if room.has_bloodstain:
            desc += "\n💀 地上有一滩血迹，你曾经在这里倒下..."

        return desc

    def _describe_room(self, room: Room) -> str:
        """再次进入房间的描述"""
        desc = f"\n【{room.name}】\n"
        desc += room.short_description

        if room.enemies:
            remaining = [e for e in room.enemies if e.is_alive]
            if remaining:
                desc += f"\n⚠️ 还有 {len(remaining)} 个敌人在这里。"

        return desc

    def get_available_exits(self, room: Room) -> List[str]:
        """获取可用的出口"""
        return list(room.connections.keys())

    def check_for_souls(self, room: Room, player: Player) -> Optional[str]:
        """检查是否有掉落的魂可以取回"""
        if (player.lost_souls_location and
            player.lost_souls_location[0] == room.id):
            recovered = player.recover_souls()
            return f"✨ 你取回了 {recovered} 个魂！"
        return None

    def check_for_bonfire(self, room: Room) -> bool:
        """检查房间是否有篝火"""
        return room.room_type == RoomType.BONFIRE

    def rest_at_bonfire(self, player: Player) -> str:
        """在篝火休息"""
        player.respawn()
        return """
🔥 你在篝火旁坐下，火焰温暖了你的身体...
你的生命和精力已完全恢复。
但你知道，篝火的温暖也意味着敌人的复活...
"""
