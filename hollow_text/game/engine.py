"""
游戏引擎 - 主游戏循环和核心逻辑
"""
from typing import Optional

from .state import GameState, GameMode
from entities.player import Player
from entities.enemy import Enemy
from systems.combat import CombatSystem, CombatAction, CombatResult
from systems.exploration import ExplorationSystem
from world.map import GameMap, create_starter_dungeon
from world.room import Room, RoomType
from ui.renderer import Renderer
from ui.input import InputHandler, GameInput


class GameEngine:
    """游戏引擎"""

    def __init__(self):
        self.state = GameState()
        self.renderer = Renderer()
        self.input_handler = InputHandler()
        self.game_map: Optional[GameMap] = None
        self.exploration = ExplorationSystem()
        self.combat: Optional[CombatSystem] = None

    def run(self) -> None:
        """运行游戏主循环"""
        while self.state.is_running:
            self._update()
        self._cleanup()

    def _update(self) -> None:
        """更新游戏状态"""
        mode = self.state.mode

        if mode == GameMode.MENU:
            self._handle_menu()
        elif mode == GameMode.EXPLORATION:
            self._handle_exploration()
        elif mode == GameMode.COMBAT:
            self._handle_combat()
        elif mode == GameMode.BONFIRE:
            self._handle_bonfire()
        elif mode == GameMode.LEVEL_UP:
            self._handle_level_up()
        elif mode == GameMode.GAME_OVER:
            self._handle_game_over()

    def _handle_menu(self) -> None:
        """处理主菜单"""
        self.renderer.clear()
        self.renderer.print_title()
        self.renderer.print_main_menu()

        raw_input = self.input_handler.get_input()
        action = self.input_handler.parse_menu_input(raw_input)

        if action == GameInput.NEW_GAME:
            self._start_new_game()
        elif action == GameInput.CONTROLS:
            self._show_controls()
        elif action == GameInput.ABOUT:
            self._show_about()
        elif action == GameInput.QUIT:
            self.state.is_running = False

    def _start_new_game(self) -> None:
        """开始新游戏"""
        self.renderer.clear()
        self.renderer.print_title()

        # 获取玩家名字
        self.renderer.print("\n[bold]你醒来了...[/bold]")
        self.renderer.print("你叫什么名字？", style="dim")
        name = input("> ").strip()
        if not name:
            name = "无名的亡者"

        # 创建玩家和地图
        self.state.create_player(name)
        self.game_map = create_starter_dungeon()

        # 进入起始房间
        start_room = self.game_map.get_start_room()
        if start_room:
            self.state.set_current_room(start_room)
            self.state.set_mode(GameMode.EXPLORATION)

            # 显示开场白
            self.renderer.print(f"\n[bold cyan]{name}[/bold cyan]...")
            self.renderer.print("你不知道自己为何在这里，也不知道要去向何方。")
            self.renderer.print("但你知道，只有不断前进，才能找到答案...")
            self.input_handler.wait_for_input()

    def _show_controls(self) -> None:
        """显示操作说明"""
        self.renderer.print_controls()
        self.input_handler.wait_for_input()

    def _show_about(self) -> None:
        """显示关于信息"""
        self.renderer.print_about()
        self.input_handler.wait_for_input()

    def _handle_exploration(self) -> None:
        """处理探索模式"""
        room = self.state.current_room
        player = self.state.player

        if not room or not player:
            return

        self.renderer.clear()
        self.renderer.print_title()

        # 检查是否有掉落的魂
        souls_msg = self.exploration.check_for_souls(room, player)
        if souls_msg:
            self.renderer.print(souls_msg, style="bold yellow")

        # 进入房间
        _, room_desc = self.exploration.enter_room(room, player)
        self.renderer.print(room_desc)

        # 检查是否有敌人
        if room.has_alive_enemies():
            # 进入战斗
            enemy = room.get_alive_enemies()[0]
            self._start_combat(enemy)
            return

        # 显示出口和行动
        exits = self.exploration.get_available_exits(room)
        self.renderer.print_exploration(room, exits)

        # 处理输入
        raw_input = self.input_handler.get_input()
        action = self.input_handler.parse_exploration_input(raw_input)

        self._process_exploration_action(action, room, exits)

    def _process_exploration_action(self, action: GameInput, room: Room, exits: list) -> None:
        """处理探索行动"""
        player = self.state.player

        if action == GameInput.NORTH and "北" in exits:
            self._move_to_room(room.connections["北"])
        elif action == GameInput.SOUTH and "南" in exits:
            self._move_to_room(room.connections["南"])
        elif action == GameInput.EAST and "东" in exits:
            self._move_to_room(room.connections["东"])
        elif action == GameInput.WEST and "西" in exits:
            self._move_to_room(room.connections["西"])
        elif action == GameInput.STATUS:
            self.renderer.print_player_status(player)
            self.input_handler.wait_for_input()
        elif action == GameInput.REST:
            if room.room_type == RoomType.BONFIRE:
                self.state.set_mode(GameMode.BONFIRE)
            else:
                self.renderer.print("\n这里没有篝火可以休息...", style="yellow")
                self.input_handler.wait_for_input()
        elif action == GameInput.QUIT:
            self.state.set_mode(GameMode.MENU)
        else:
            self.renderer.print("\n无效的输入。", style="red")
            self.input_handler.wait_for_input()

    def _move_to_room(self, room_id: str) -> None:
        """移动到指定房间"""
        if not self.game_map:
            return

        new_room = self.game_map.get_room(room_id)
        if new_room:
            self.state.set_current_room(new_room)
            self.state.increment_turn()

    def _start_combat(self, enemy: Enemy) -> None:
        """开始战斗"""
        self.combat = CombatSystem(self.state.player, enemy)
        self.state.set_mode(GameMode.COMBAT)

        self.renderer.print(f"\n[bold red]══════ 战斗开始 ══════[/bold red]")
        self.renderer.print(f"[bold]敌人: {enemy.name}[/bold]")
        self.renderer.print(f"[dim]{enemy.description}[/dim]")
        self.input_handler.wait_for_input()

    def _handle_combat(self) -> None:
        """处理战斗模式"""
        if not self.combat or not self.state.player:
            return

        self.renderer.clear()
        self.renderer.print_title()

        # 显示战斗状态
        self.renderer.print_combat_status(self.combat)

        # 检查战斗结果
        if self.combat.result != CombatResult.ONGOING:
            self._handle_combat_result()
            return

        # 显示行动选项
        self.renderer.print_combat_actions(self.state.player)

        # 处理输入
        raw_input = self.input_handler.get_input()
        action = self.input_handler.parse_combat_input(raw_input)

        self._process_combat_action(action)

    def _process_combat_action(self, action: GameInput) -> None:
        """处理战斗行动"""
        if not self.combat:
            return

        combat_action = None

        if action == GameInput.ATTACK:
            combat_action = CombatAction.ATTACK
        elif action == GameInput.HEAVY_ATTACK:
            combat_action = CombatAction.HEAVY_ATTACK
        elif action == GameInput.DEFEND:
            combat_action = CombatAction.DEFEND
        elif action == GameInput.DODGE:
            combat_action = CombatAction.DODGE
        elif action == GameInput.FLEE:
            combat_action = CombatAction.FLEE
        else:
            self.renderer.print("\n无效的输入。", style="red")
            self.input_handler.wait_for_input()
            return

        # 验证行动
        valid, message = self.combat.is_player_turn_valid(combat_action)
        if not valid:
            self.renderer.print(f"\n{message}", style="red")
            self.input_handler.wait_for_input()
            return

        # 执行回合
        log = self.combat.execute_turn(combat_action)
        self.renderer.print(f"\n{log.message}", style="bold")
        self.input_handler.wait_for_input()

    def _handle_combat_result(self) -> None:
        """处理战斗结果"""
        if not self.combat or not self.state.player:
            return

        result = self.combat.result
        player = self.state.player

        if result == CombatResult.PLAYER_WIN:
            souls = self.combat.enemy.souls_reward
            player.gain_souls(souls)
            self.state.record_souls(souls)
            self.state.record_kill()

            self.renderer.print_victory(souls)
            self.input_handler.wait_for_input()

            # 返回探索模式
            self.state.set_mode(GameMode.EXPLORATION)
            self.combat = None

        elif result == CombatResult.PLAYER_DEATH:
            self.state.record_death()

            # 掉落魂
            if self.state.current_room:
                player.drop_souls((self.state.current_room.id, 0))
                self.state.current_room.has_bloodstain = True

            self.renderer.print_death(player, (self.state.current_room.id, 0))
            self.input_handler.wait_for_input()

            # 重生到最近的篝火
            self._respawn_at_bonfire()

        elif result == CombatResult.FLED:
            self.renderer.print("\n你成功逃离了战斗！", style="green")
            self.input_handler.wait_for_input()
            self.state.set_mode(GameMode.EXPLORATION)
            self.combat = None

    def _respawn_at_bonfire(self) -> None:
        """在篝火重生"""
        if not self.state.player or not self.game_map:
            return

        # 重生到起始篝火
        start_room = self.game_map.get_start_room()
        if start_room:
            self.state.player.respawn()
            self.state.set_current_room(start_room)
            self.state.set_mode(GameMode.EXPLORATION)

            # 重生所有敌人
            self.game_map.respawn_all_enemies()

    def _handle_bonfire(self) -> None:
        """处理篝火模式"""
        player = self.state.player

        self.renderer.clear()
        self.renderer.print_title()
        self.renderer.print_bonfire_menu(player)

        raw_input = self.input_handler.get_input()
        action = self.input_handler.parse_bonfire_input(raw_input)

        if action == GameInput.REST:
            # 休息
            if self.game_map:
                self.game_map.respawn_all_enemies()
            self.renderer.print(self.exploration.rest_at_bonfire(player))
            self.input_handler.wait_for_input()
        elif action == GameInput.LOG:  # 升级
            self.state.set_mode(GameMode.LEVEL_UP)
        elif action == GameInput.LEAVE:
            self.state.set_mode(GameMode.EXPLORATION)

    def _handle_level_up(self) -> None:
        """处理升级模式"""
        player = self.state.player

        self.renderer.clear()
        self.renderer.print_title()
        self.renderer.print_level_up_menu(player)

        raw_input = self.input_handler.get_input()
        action, stat = self.input_handler.parse_level_up_input(raw_input)

        if action == GameInput.BACK:
            self.state.set_mode(GameMode.BONFIRE)
        elif stat:
            if player.souls >= player.get_level_up_cost():
                player.level_up(stat)
                self.renderer.print(f"\n[bold green]升级成功！[/bold green]")
                self.renderer.print(f"[bold]{stat}[/bold] 提升了！")
            else:
                self.renderer.print("\n魂不足！", style="red")
            self.input_handler.wait_for_input()

    def _handle_game_over(self) -> None:
        """处理游戏结束"""
        self.renderer.clear()
        self.renderer.print_title()

        stats = self.state.get_stats_summary()
        self.renderer.print(stats)

        self.renderer.print("\n感谢游玩《虚渊文字》！")
        self.renderer.print("\n[Q] 返回主菜单")

        raw_input = self.input_handler.get_input()
        if raw_input.lower() == "q":
            self.state.set_mode(GameMode.MENU)

    def _cleanup(self) -> None:
        """清理资源"""
        self.renderer.clear()
        self.renderer.print("\n[bold]再见，亡者...[/bold]")
        self.renderer.print("[dim]愿火焰永远指引你的道路...[/dim]\n")
