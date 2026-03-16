"""
界面渲染 - 使用 rich 库创建精美的终端 UI
依赖: pip install rich
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.layout import Layout
from typing import Optional, List

from entities.player import Player
from entities.enemy import Enemy, EnemyAction
from systems.combat import CombatSystem, CombatAction
from world.room import Room


class Renderer:
    """终端渲染器"""

    def __init__(self):
        self.console = Console()

    def clear(self) -> None:
        """清屏"""
        self.console.clear()

    def print(self, text: str = "", style: str = "") -> None:
        """打印文本"""
        if style:
            self.console.print(text, style=style)
        else:
            self.console.print(text)

    def print_title(self) -> None:
        """打印游戏标题"""
        title = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄     ║
║     █░███░███░███░███░███░███░███░███░███░███░█         ║
║     █░█░█░█░█░█░█░█░█░█░█░█░█░█░█░█░█░█░█░█░█░█         ║
║     █░███░███░███░███░███░███░███░███░███░███░█         ║
║     █░█░░░█░░░█░░░█░░░█░░░█░░░█░░░█░░░█░░░█░░░█         ║
║     █░█░███░███░███░███░███░███░███░███░███░█░█         ║
║     ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀     ║
║                                                           ║
║               《 虚 渊 文 字 》                           ║
║                 Hollow Text                               ║
║                                                           ║
║          "在黑暗中前行，以魂为灯"                          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
        self.console.print(title, style="bold red")

    def print_main_menu(self) -> None:
        """打印主菜单"""
        self.print()
        menu = Panel(
            "[1] 开始新游戏\n"
            "[2] 查看操作说明\n"
            "[3] 关于游戏\n"
            "[Q] 退出游戏",
            title="[bold]主菜单[/bold]",
            border_style="yellow"
        )
        self.console.print(menu)

    def print_controls(self) -> None:
        """打印操作说明"""
        self.clear()
        self.print_title()

        controls_text = """
[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]
                    [bold]操作说明[/bold]
[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]

[bold yellow]探索模式[/bold yellow]
  [N] 北  [S] 南  [E] 东  [W] 西    - 移动
  [R] 休息（仅篝火房间）             - 恢复HP/存档
  [I] 查看状态                       - 查看角色信息
  [L] 查看日志                       - 查看战斗记录

[bold yellow]战斗模式[/bold yellow]
  [A] 攻击    (消耗 6 精力)          - 普通攻击
  [H] 重击    (消耗10精力)           - 高伤害但会硬直
  [D] 防御    (消耗 3 精力)          - 减少受到的伤害
  [O] 闪避    (消耗 5 精力)          - 有几率完全躲避攻击
  [F] 逃跑                          - 尝试逃离战斗

[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]

[bold red]战斗提示[/bold red]
  • 敌人蓄力时是攻击的最佳时机
  • 管理好精力，不要贪刀
  • 重击后会有硬直，慎用
  • 观察敌人模式，把握攻击时机

[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]
"""
        self.print(controls_text)
        self.print("\n按任意键返回主菜单...")

    def print_about(self) -> None:
        """打印关于信息"""
        self.clear()
        self.print_title()

        about_text = """
[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]

[bold]《虚渊文字》Hollow Text[/bold]

一款受《黑暗之魂》系列启发的文字 Roguelike 游戏。

[bold yellow]特色[/bold yellow]
  • 魂风格回合制战斗
  • 精力管理系统
  • 死亡惩罚机制
  • 随机生成地牢（即将推出）
  • 碎片化叙事（即将推出）

[bold yellow]开发信息[/bold yellow]
  引擎: Python + Rich
  版本: 0.1.0 (MVP)

[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]

" darkness "
"""
        self.print(about_text)
        self.print("\n按任意键返回主菜单...")

    def print_player_status(self, player: Player) -> None:
        """打印玩家状态"""
        hp_bar = self._create_bar(player.hp, player.max_hp, "red")
        stamina_bar = self._create_bar(player.stamina, player.max_stamina, "green")

        status_text = f"""
[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]
                    [bold]角色状态[/bold]
[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]

[bold]{player.name}[/bold]  Lv.{player.level}

生命值: {hp_bar} {player.hp}/{player.max_hp}
精力:   {stamina_bar} {player.stamina}/{player.max_stamina}

魂: {player.souls}  (升级需要: {player.get_level_up_cost()})

[bold yellow]属性[/bold yellow]
  力量: {player.stats.strength}  敏捷: {player.stats.dexterity}
  智力: {player.stats.intelligence}  信仰: {player.stats.faith}

[bold yellow]战斗[/bold yellow]
  攻击力: {player.attack_power}  防御: {player.defense}
  闪避率: {player.calculate_dodge_chance()*100:.1f}%

"""
        self.print(status_text)

    def print_exploration(self, room: Room, exits: List[str]) -> None:
        """打印探索界面"""
        self.print(f"\n[bold cyan]{'─'*50}[/bold cyan]")

        # 显示出口
        exit_text = " ".join([f"[{self._direction_symbol(d)}]" for d in exits])
        self.print(f"\n可用出口: {exit_text}")

        self.print("\n[bold]行动:[/bold] [N]北 [S]南 [E]东 [W]西 [I]状态 [L]日志", style="dim")

    def _direction_symbol(self, direction: str) -> str:
        """获取方向符号"""
        symbols = {"北": "↑北", "南": "↓南", "东": "→东", "西": "←西"}
        return symbols.get(direction, direction)

    def print_combat_status(self, combat: CombatSystem) -> None:
        """打印战斗状态"""
        self.print(combat.get_combat_status())

    def print_combat_actions(self, player: Player) -> None:
        """打印战斗行动选项"""
        actions_text = f"""
[bold yellow]═══════════════════════════════════════════════════════[/bold yellow]
                    [bold]选择行动[/bold]
[bold yellow]═══════════════════════════════════════════════════════[/bold yellow]

[A] 攻击  (消耗 6 精力)     [H] 重击  (消耗10精力)
[D] 防御  (消耗 3 精力)     [O] 闪避  (消耗 5 精力)
[F] 逃跑  (有风险)

当前精力: {player.stamina}/{player.max_stamina}
"""
        self.print(actions_text)

    def print_combat_log(self, message: str, is_player_turn: bool = True) -> None:
        """打印战斗日志"""
        if is_player_turn:
            self.print(f"\n[bold green]你的行动:[/bold green] {message}")
        else:
            self.print(f"[bold red]敌人:[/bold red] {message}")

    def print_victory(self, souls_gained: int) -> None:
        """打印胜利信息"""
        victory_text = f"""
[bold green]═══════════════════════════════════════════════════════[/bold green]
                    [bold]敌 人 击 败[/bold]
[bold green]═══════════════════════════════════════════════════════[/bold green]

你获得了 {souls_gained} 个魂！

"""
        self.print(victory_text)

    def print_death(self, player: Player, location: tuple) -> None:
        """打印死亡信息"""
        death_text = f"""
[bold red]═══════════════════════════════════════════════════════[/bold red]
                    [bold]你 死 了[/bold]
[bold red]═══════════════════════════════════════════════════════[/bold red]

你失去了 {player.lost_souls_amount} 个魂...

但你并没有真正死去。
你从篝火旁醒来，准备再次挑战黑暗...

"""
        self.print(death_text)

    def print_bonfire_menu(self, player: Player) -> None:
        """打印篝火菜单"""
        bonfire_text = f"""
[bold yellow]═══════════════════════════════════════════════════════[/bold yellow]
                    [bold]🔥 篝 火 🔥[/bold]
[bold yellow]═══════════════════════════════════════════════════════[/bold yellow]

[R] 休息 - 恢复全部生命和精力（敌人会复活）
[U] 升级 - 消耗魂提升属性
[L] 离开

当前魂: {player.souls}  升级需要: {player.get_level_up_cost()}

"""
        self.print(bonfire_text)

    def print_level_up_menu(self, player: Player) -> None:
        """打印升级菜单"""
        menu_text = f"""
[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]
                    [bold]升级属性[/bold]
[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]

当前等级: {player.level}  所需魂: {player.get_level_up_cost()}
当前魂: {player.souls}

[1] 力量 ({player.stats.strength}) - 增加物理伤害
[2] 敏捷 ({player.stats.dexterity}) - 增加闪避和暴击
[3] 智力 ({player.stats.intelligence}) - 增加法术伤害
[4] 信仰 ({player.stats.faith}) - 增加奇迹效果

[Q] 取消

"""
        self.print(menu_text)

    def _create_bar(self, current: int, maximum: int, color: str, length: int = 10) -> str:
        """创建进度条"""
        filled = int((current / maximum) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{color}]{bar}[/{color}]"

    def print_message(self, message: str, style: str = "") -> None:
        """打印消息"""
        if style:
            self.console.print(Panel(message, style=style))
        else:
            self.console.print(Panel(message))

    def print_input_prompt(self) -> None:
        """打印输入提示"""
        self.print("\n> ", end="")

    def print_separator(self) -> None:
        """打印分隔线"""
        self.print("[dim]──────────────────────────────────────────────────[/dim]")
