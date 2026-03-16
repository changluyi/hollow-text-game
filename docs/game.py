"""
虚渊文字 - PyScript 网页版游戏逻辑
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from enum import Enum
from random import random


# ==================== 枚举定义 ====================

class EntityType(Enum):
    PLAYER = "player"
    ENEMY = "enemy"


class EnemyAction(Enum):
    IDLE = "idle"
    CHARGE = "charge"
    ATTACK = "attack"
    DEFEND = "defend"
    REST = "rest"


class CombatAction(Enum):
    ATTACK = "attack"
    HEAVY_ATTACK = "heavy"
    DEFEND = "defend"
    DODGE = "dodge"
    FLEE = "flee"


class RoomType(Enum):
    NORMAL = "normal"
    BONFIRE = "bonfire"
    BOSS = "boss"


class GameMode(Enum):
    MENU = "menu"
    NAME_INPUT = "name_input"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    BONFIRE = "bonfire"
    LEVEL_UP = "level_up"


# ==================== 实体类 ====================

@dataclass
class Entity:
    name: str
    hp: int = 100
    max_hp: int = 100
    stamina: int = 20
    max_stamina: int = 20
    attack_power: int = 10
    defense: int = 5
    is_alive: bool = True

    def take_damage(self, damage: int) -> int:
        actual = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual)
        if self.hp <= 0:
            self.is_alive = False
        return actual

    def use_stamina(self, amount: int) -> bool:
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False

    def recover_stamina(self, amount: int) -> None:
        self.stamina = min(self.max_stamina, self.stamina + amount)


@dataclass
class PlayerStats:
    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    faith: int = 10


@dataclass
class Player(Entity):
    souls: int = 0
    level: int = 1
    stats: PlayerStats = field(default_factory=PlayerStats)
    lost_souls_location: Optional[str] = None
    lost_souls_amount: int = 0

    def gain_souls(self, amount: int) -> None:
        self.souls += amount

    def spend_souls(self, amount: int) -> bool:
        if self.souls >= amount:
            self.souls -= amount
            return True
        return False

    def drop_souls(self, location: str) -> None:
        self.lost_souls_location = location
        self.lost_souls_amount = self.souls
        self.souls = 0

    def recover_souls(self) -> int:
        amount = self.lost_souls_amount
        self.lost_souls_location = None
        self.lost_souls_amount = 0
        self.souls += amount
        return amount

    def get_level_up_cost(self) -> int:
        return self.level * 100

    def level_up(self, stat: str) -> bool:
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

    def calculate_attack_damage(self) -> int:
        return self.attack_power + int(self.stats.strength * 0.5)

    def calculate_dodge_chance(self) -> float:
        return min(0.5, 0.1 + self.stats.dexterity * 0.02)

    def respawn(self) -> None:
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.is_alive = True


@dataclass
class EnemyPattern:
    sequence: List[EnemyAction]
    current_index: int = 0

    def get_next(self) -> EnemyAction:
        action = self.sequence[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.sequence)
        return action


@dataclass
class Enemy(Entity):
    description: str = ""
    souls_reward: int = 50
    pattern: Optional[EnemyPattern] = None
    current_action: EnemyAction = EnemyAction.IDLE

    def __post_init__(self):
        if self.pattern is None:
            self.pattern = EnemyPattern([
                EnemyAction.IDLE, EnemyAction.CHARGE,
                EnemyAction.ATTACK, EnemyAction.REST
            ])

    def decide_action(self) -> EnemyAction:
        self.current_action = self.pattern.get_next()
        return self.current_action

    def get_action_text(self) -> str:
        texts = {
            EnemyAction.IDLE: "敌人正在观察你的动作...",
            EnemyAction.CHARGE: "【警告】敌人正在蓄力！",
            EnemyAction.ATTACK: "敌人发起攻击！",
            EnemyAction.DEFEND: "敌人举起盾牌防御。",
            EnemyAction.REST: "敌人动作迟缓，似乎在喘息...",
        }
        return texts.get(self.current_action, "")

    def is_vulnerable(self) -> bool:
        return self.current_action in [EnemyAction.CHARGE, EnemyAction.REST]

    def calculate_attack_damage(self) -> int:
        base = self.attack_power
        if self.current_action == EnemyAction.CHARGE:
            return int(base * 1.5)
        return base

    def respawn(self) -> None:
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.is_alive = True
        self.pattern.current_index = 0


def create_hollow_soldier() -> Enemy:
    return Enemy(
        name="空洞士兵",
        description="一个失去了心智的士兵，仅剩下战斗的本能。",
        hp=40, max_hp=40, attack_power=10, defense=3, souls_reward=30,
        pattern=EnemyPattern([EnemyAction.IDLE, EnemyAction.ATTACK, EnemyAction.REST])
    )


def create_rotted_knight() -> Enemy:
    return Enemy(
        name="腐朽骑士",
        description="曾经是英勇的骑士，现在只剩下腐朽的铠甲和无尽的仇恨。",
        hp=80, max_hp=80, attack_power=18, defense=8,
        stamina=25, max_stamina=25, souls_reward=80,
        pattern=EnemyPattern([
            EnemyAction.IDLE, EnemyAction.CHARGE,
            EnemyAction.ATTACK, EnemyAction.ATTACK, EnemyAction.REST
        ])
    )


def create_dark_wraith() -> Enemy:
    return Enemy(
        name="深渊幽灵",
        description="从深渊中爬出的黑暗存在，它渴望吞噬一切光明。",
        hp=120, max_hp=120, attack_power=25, defense=5,
        stamina=30, max_stamina=30, souls_reward=200,
        pattern=EnemyPattern([
            EnemyAction.CHARGE, EnemyAction.ATTACK, EnemyAction.ATTACK,
            EnemyAction.ATTACK, EnemyAction.REST, EnemyAction.IDLE
        ])
    )


# ==================== 房间和地图 ====================

@dataclass
class Room:
    id: str
    name: str
    description: str
    room_type: RoomType = RoomType.NORMAL
    connections: Dict[str, str] = field(default_factory=dict)
    enemies: List[Enemy] = field(default_factory=list)
    has_bloodstain: bool = False

    def get_alive_enemies(self) -> List[Enemy]:
        return [e for e in self.enemies if e.is_alive]

    def has_alive_enemies(self) -> bool:
        return len(self.get_alive_enemies()) > 0

    def respawn_enemies(self) -> None:
        for enemy in self.enemies:
            enemy.respawn()


def create_map() -> Dict[str, Room]:
    rooms = {}

    # 入口篝火
    rooms["entrance"] = Room(
        id="entrance", name="被遗忘的入口",
        description="你站在一个古老建筑的入口处。破败的石柱上刻满了看不懂的符文，一堆篝火在角落里静静地燃烧着。",
        room_type=RoomType.BONFIRE,
        connections={"北": "corridor_1"}
    )

    # 走廊1
    rooms["corridor_1"] = Room(
        id="corridor_1", name="昏暗走廊",
        description="一条狭长的走廊，墙壁上的火把早已熄灭。地上散落着生锈的武器和破碎的盾牌。",
        connections={"南": "entrance", "北": "hall_1"},
        enemies=[create_hollow_soldier()]
    )

    # 大厅
    rooms["hall_1"] = Room(
        id="hall_1", name="战士大厅",
        description="一个宽敞的大厅，墙壁上挂满了褪色的旗帜和锈蚀的盔甲。大厅中央有一座断裂的雕像。",
        connections={"南": "corridor_1", "北": "bonfire_2", "西": "side_chamber"},
        enemies=[create_hollow_soldier(), create_hollow_soldier()]
    )

    # 侧室
    rooms["side_chamber"] = Room(
        id="side_chamber", name="封印的宝库",
        description="一个小型的石室，门上刻着古老的封印。房间中央有一个石台，上面空无一物。",
        room_type=RoomType.NORMAL,
        connections={"东": "hall_1"}
    )

    # 篝火2
    rooms["bonfire_2"] = Room(
        id="bonfire_2", name="深渊前厅",
        description="这里比其他地方更加温暖。一堆篝火在中央燃烧着。墙上刻着：\"不要贪婪，耐心是生存的关键。\"",
        room_type=RoomType.BONFIRE,
        connections={"南": "hall_1", "北": "corridor_2"}
    )

    # 骑士走廊
    rooms["corridor_2"] = Room(
        id="corridor_2", name="骑士长廊",
        description="两侧站立着沉默的盔甲，它们仿佛在注视着你。这里的敌人更加强大...",
        connections={"南": "bonfire_2", "北": "boss_room"},
        enemies=[create_rotted_knight()]
    )

    # Boss房间
    rooms["boss_room"] = Room(
        id="boss_room", name="深渊守卫之间",
        description="一个巨大的圆形大厅。中央矗立着一个高大的身影，它的眼睛在黑暗中闪烁着红光！",
        room_type=RoomType.BOSS,
        connections={"南": "corridor_2"},
        enemies=[create_dark_wraith()]
    )

    return rooms


# ==================== 游戏引擎 ====================

class Game:
    STAMINA_COST = {
        CombatAction.ATTACK: 6,
        CombatAction.HEAVY_ATTACK: 10,
        CombatAction.DEFEND: 3,
        CombatAction.DODGE: 5,
    }

    def __init__(self):
        self.mode = GameMode.MENU
        self.player: Optional[Player] = None
        self.rooms = create_map()
        self.current_room: Optional[Room] = None
        self.current_enemy: Optional[Enemy] = None
        self.combat_turn = 0
        self._is_stunned = False

    def start(self):
        self.show_menu()

    def show_menu(self):
        self.mode = GameMode.MENU
        self.update_ui()

    def start_new_game(self):
        self.mode = GameMode.NAME_INPUT
        self.update_ui()

    def set_player_name(self, name: str):
        if not name.strip():
            name = "无名的亡者"
        self.player = Player(name=name.strip())
        self.current_room = self.rooms["entrance"]
        self.mode = GameMode.EXPLORATION
        self.enter_room()

    def enter_room(self):
        room = self.current_room
        if not room or not self.player:
            return

        # 检查是否有掉落的魂
        if self.player.lost_souls_location == room.id:
            recovered = self.player.recover_souls()
            self.append_output(f"✨ 你取回了 {recovered} 个魂！", "souls")

        # 检查是否有敌人
        if room.has_alive_enemies():
            self.start_combat(room.get_alive_enemies()[0])
            return

        self.mode = GameMode.EXPLORATION
        self.update_ui()

    def start_combat(self, enemy: Enemy):
        self.current_enemy = enemy
        self.combat_turn = 0
        self._is_stunned = False
        self.mode = GameMode.COMBAT
        self.append_output(f"\n【战斗开始】{enemy.name}", "warning")
        self.append_output(enemy.description, "description")
        self.update_ui()

    def move(self, direction: str):
        if not self.current_room:
            return

        if direction in self.current_room.connections:
            new_room_id = self.current_room.connections[direction]
            self.current_room = self.rooms[new_room_id]
            self.enter_room()
        else:
            self.append_output("那个方向没有路。", "warning")

    def combat_action(self, action: CombatAction):
        if not self.player or not self.current_enemy:
            return

        self.combat_turn += 1
        messages = []

        # 检查精力
        cost = self.STAMINA_COST.get(action, 0)
        if self.player.stamina < cost:
            self.append_output("精力不足！", "warning")
            return

        # 获取敌人下一步行动
        enemy_next = self.current_enemy.decide_action()

        # 处理玩家行动
        if action == CombatAction.ATTACK:
            self._player_attack()
        elif action == CombatAction.HEAVY_ATTACK:
            self._player_heavy_attack()
        elif action == CombatAction.DEFEND:
            self._player_defend()
        elif action == CombatAction.DODGE:
            self._player_dodge()
        elif action == CombatAction.FLEE:
            if random() < 0.3 + self.player.stats.dexterity * 0.02:
                self.append_output("你成功逃离了战斗！", "success")
                self.mode = GameMode.EXPLORATION
                self.current_enemy = None
                self.update_ui()
                return
            self.append_output("逃跑失败！", "damage")

        # 消耗精力
        self.player.use_stamina(cost)

        # 敌人攻击
        if self.current_enemy.is_alive and enemy_next == EnemyAction.ATTACK:
            self._enemy_attack(action)

        # 回合结束恢复精力
        self.player.recover_stamina(2)
        if self.current_enemy:
            self.current_enemy.recover_stamina(2)

        # 检查结果
        self._check_combat_result()

    def _player_attack(self):
        if not self.player or not self.current_enemy:
            return

        damage = self.player.calculate_attack_damage()
        if self.current_enemy.is_vulnerable():
            damage = int(damage * 1.5)
            actual = self.current_enemy.take_damage(damage)
            self.append_output(f"趁机攻击！造成 {actual} 点伤害！", "success")
        else:
            actual = self.current_enemy.take_damage(damage)
            self.append_output(f"攻击造成 {actual} 点伤害。")

        if actual > 15:
            self._is_stunned = True
            self.append_output("用力过猛，动作僵直了...", "warning")

    def _player_heavy_attack(self):
        if not self.player or not self.current_enemy:
            return

        self._is_stunned = True
        damage = int(self.player.calculate_attack_damage() * 1.8)

        if self.current_enemy.is_vulnerable():
            damage = int(damage * 2)
            actual = self.current_enemy.take_damage(damage)
            self.append_output(f"致命重击！造成 {actual} 点巨额伤害！", "success")
        else:
            actual = self.current_enemy.take_damage(damage)
            self.append_output(f"重击造成 {actual} 点伤害！但你暴露了破绽...", "warning")

    def _player_defend(self):
        self.player.defense += 10
        self.append_output("你举起盾牌防御。")

    def _player_dodge(self):
        if random() < self.player.calculate_dodge_chance():
            self.append_output("你准备闪避！", "success")
        else:
            self.append_output("闪避准备失败。", "warning")

    def _enemy_attack(self, player_action: CombatAction):
        if not self.player or not self.current_enemy:
            return

        damage = self.current_enemy.calculate_attack_damage()

        # 闪避检查
        if player_action == CombatAction.DODGE:
            if random() < self.player.calculate_dodge_chance():
                self.append_output(f"{self.current_enemy.name} 的攻击被闪开了！", "success")
                return

        # 防御检查
        if player_action == CombatAction.DEFEND:
            damage = int(damage * 0.3)
            self.player.defense -= 10

        actual = self.player.take_damage(damage)
        self.append_output(f"{self.current_enemy.name} 攻击命中！你受到 {actual} 点伤害！", "damage")

    def _check_combat_result(self):
        if not self.player or not self.current_enemy:
            return

        if not self.current_enemy.is_alive:
            # 胜利
            souls = self.current_enemy.souls_reward
            self.player.gain_souls(souls)
            self.append_output(f"\n【胜利】获得 {souls} 魂！", "souls")
            self.mode = GameMode.EXPLORATION
            self.current_enemy = None
            self.update_ui()

        elif not self.player.is_alive:
            # 死亡
            self.player.drop_souls(self.current_room.id)
            if self.current_room:
                self.current_room.has_bloodstain = True
            self.append_output("\n【你死了】", "damage")
            self.append_output(f"失去了 {self.player.lost_souls_amount} 魂...", "warning")
            self._respawn()

    def _respawn(self):
        if not self.player:
            return

        self.player.respawn()
        self.current_room = self.rooms["entrance"]

        # 重生所有敌人
        for room in self.rooms.values():
            room.respawn_enemies()

        self.current_enemy = None
        self.mode = GameMode.EXPLORATION
        self.append_output("\n你从篝火旁醒来...")
        self.enter_room()

    def bonfire_rest(self):
        if not self.player:
            return

        self.player.hp = self.player.max_hp
        self.player.stamina = self.player.max_stamina

        for room in self.rooms.values():
            room.respawn_enemies()

        self.append_output("🔥 你在篝火旁休息，生命和精力完全恢复。", "success")
        self.append_output("敌人也复活了...", "warning")
        self.mode = GameMode.EXPLORATION
        self.update_ui()

    def open_bonfire_menu(self):
        self.mode = GameMode.BONFIRE
        self.update_ui()

    def open_level_up(self):
        self.mode = GameMode.LEVEL_UP
        self.update_ui()

    def level_up(self, stat: str):
        if not self.player:
            return

        if self.player.level_up(stat):
            self.append_output(f"升级成功！{stat} 提升了！", "success")
        else:
            self.append_output(f"魂不足！需要 {self.player.get_level_up_cost()} 魂。", "warning")
        self.mode = GameMode.BONFIRE
        self.update_ui()

    # ==================== UI 更新 ====================

    def update_ui(self):
        self._update_output()
        self._update_status()
        self._update_enemy()
        self._update_actions()

    def _update_output(self):
        from pyscript import document
        output = document.getElementById("output")

        if self.mode == GameMode.MENU:
            output.innerHTML = """
                <p class="room-name">虚渊文字</p>
                <p class="description">在黑暗中前行，以魂为灯</p>
                <p class="divider">──────────────────────────</p>
                <p>一款受《黑暗之魂》启发的文字 Roguelike 游戏。</p>
                <p>在这个黑暗的世界中，你将面对可怕的敌人，管理宝贵的精力，并在死亡中不断成长。</p>
            """
        elif self.mode == GameMode.NAME_INPUT:
            output.innerHTML = """
                <p class="room-name">新的旅程</p>
                <p class="description">你醒来了...但你不记得自己是谁。</p>
                <p>你叫什么名字？</p>
            """
        elif self.mode == GameMode.EXPLORATION and self.current_room:
            room = self.current_room
            exits = " ".join([f"[{d}]" for d in room.connections.keys()])

            html = f"""
                <p class="room-name">【{room.name}】</p>
                <p class="description">{room.description}</p>
            """

            if room.has_bloodstain:
                html += '<p class="warning">💀 地上有一滩血迹...</p>'

            if room.room_type == RoomType.BONFIRE:
                html += '<p class="success">🔥 一堆篝火静静地燃烧着。</p>'

            html += f'<p class="divider">──────────────────────────</p>'
            html += f'<p>可用出口: {exits}</p>'

            output.innerHTML = html

        elif self.mode == GameMode.COMBAT:
            if self.current_enemy:
                html = f"""
                    <p class="room-name">【战斗中】第 {self.combat_turn} 回合</p>
                    <p class="warning">{self.current_enemy.get_action_text()}</p>
                """
                output.innerHTML = html

        elif self.mode == GameMode.BONFIRE:
            output.innerHTML = """
                <p class="room-name">🔥 篝火 🔥</p>
                <p class="description">火焰温暖了你的身体...</p>
                <p class="divider">──────────────────────────</p>
                <p>选择你的行动：</p>
            """

        elif self.mode == GameMode.LEVEL_UP and self.player:
            p = self.player
            output.innerHTML = f"""
                <p class="room-name">升级属性</p>
                <p>当前等级: {p.level} | 所需魂: {p.get_level_up_cost()} | 拥有魂: {p.souls}</p>
                <p class="divider">──────────────────────────</p>
            """

    def _update_status(self):
        from pyscript import document
        status_bar = document.getElementById("status-bar")

        if not self.player or self.mode == GameMode.MENU or self.mode == GameMode.NAME_INPUT:
            status_bar.classList.add("hidden")
            return

        status_bar.classList.remove("hidden")

        p = self.player
        hp_pct = (p.hp / p.max_hp) * 100
        stamina_pct = (p.stamina / p.max_stamina) * 100

        document.getElementById("hp-fill").style.width = f"{hp_pct}%"
        document.getElementById("hp-value").textContent = f"{p.hp}/{p.max_hp}"
        document.getElementById("stamina-fill").style.width = f"{stamina_pct}%"
        document.getElementById("stamina-value").textContent = f"{p.stamina}/{p.max_stamina}"
        document.getElementById("souls-value").textContent = str(p.souls)

    def _update_enemy(self):
        from pyscript import document
        enemy_status = document.getElementById("enemy-status")

        if self.mode != GameMode.COMBAT or not self.current_enemy:
            enemy_status.classList.add("hidden")
            return

        enemy_status.classList.remove("hidden")
        e = self.current_enemy
        hp_pct = (e.hp / e.max_hp) * 100

        document.getElementById("enemy-name").textContent = e.name
        document.getElementById("enemy-hp-fill").style.width = f"{hp_pct}%"
        document.getElementById("enemy-action").textContent = e.get_action_text()

    def _update_actions(self):
        from pyscript import document
        actions = document.getElementById("actions")
        input_area = document.getElementById("input-area")

        actions.innerHTML = ""
        input_area.classList.add("hidden")

        if self.mode == GameMode.MENU:
            self._add_button("开始新游戏", "start_game")
            self._add_button("操作说明", "show_help")

        elif self.mode == GameMode.NAME_INPUT:
            input_area.classList.remove("hidden")

        elif self.mode == GameMode.EXPLORATION and self.current_room:
            for direction in self.current_room.connections.keys():
                self._add_button(direction, f"move_{direction}")

            if self.current_room.room_type == RoomType.BONFIRE:
                self._add_button("休息", "bonfire_rest", "primary")

            self._add_button("状态", "show_status")

        elif self.mode == GameMode.COMBAT:
            self._add_button(f"攻击(6)", "combat_attack", "primary")
            self._add_button(f"重击(10)", "combat_heavy")
            self._add_button(f"防御(3)", "combat_defend")
            self._add_button(f"闪避(5)", "combat_dodge")
            self._add_button("逃跑", "combat_flee")

        elif self.mode == GameMode.BONFIRE:
            self._add_button("休息恢复", "bonfire_rest", "primary")
            self._add_button("升级属性", "level_up")
            self._add_button("离开", "bonfire_leave")

        elif self.mode == GameMode.LEVEL_UP:
            self._add_button(f"力量({self.player.stats.strength})", "up_strength")
            self._add_button(f"敏捷({self.player.stats.dexterity})", "up_dexterity")
            self._add_button(f"智力({self.player.stats.intelligence})", "up_intelligence")
            self._add_button(f"信仰({self.player.stats.faith})", "up_faith")
            self._add_button("返回", "level_up_back")

    def _add_button(self, text: str, action: str, style: str = ""):
        from pyscript import document
        actions = document.getElementById("actions")

        btn = document.createElement("button")
        btn.textContent = text
        btn.setAttribute("data-action", action)
        if style:
            btn.classList.add(style)
        btn.onclick = lambda e, a=action: handle_action(a)
        actions.appendChild(btn)

    def append_output(self, text: str, style: str = ""):
        from pyscript import document
        output = document.getElementById("output")

        p = document.createElement("p")
        p.textContent = text
        if style:
            p.classList.add(style)
        output.appendChild(p)
        output.scrollTop = output.scrollHeight


# ==================== 全局游戏实例和事件处理 ====================

game = Game()


def handle_action(action: str):
    if action == "start_game":
        game.start_new_game()
    elif action == "show_help":
        game.append_output("""
──────────────────────────
【操作说明】
探索模式: 点击方向按钮移动
战斗模式: 选择攻击/防御/闪避
篝火模式: 休息恢复或升级属性

【战斗提示】
• 敌人蓄力时是攻击最佳时机
• 管理好精力，不要贪刀
• 重击后会有硬直，慎用
──────────────────────────
""", "description")
    elif action.startswith("move_"):
        direction = action.replace("move_", "")
        game.move(direction)
    elif action == "bonfire_rest":
        game.bonfire_rest()
    elif action == "show_status":
        if game.player:
            p = game.player
            game.append_output(f"""
──────────────────────────
【{p.name}】 Lv.{p.level}
HP: {p.hp}/{p.max_hp} | 精力: {p.stamina}/{p.max_stamina}
魂: {p.souls}

力量:{p.stats.strength} 敏捷:{p.stats.dexterity}
智力:{p.stats.intelligence} 信仰:{p.stats.faith}
──────────────────────────
""", "description")
    elif action == "combat_attack":
        game.combat_action(CombatAction.ATTACK)
    elif action == "combat_heavy":
        game.combat_action(CombatAction.HEAVY_ATTACK)
    elif action == "combat_defend":
        game.combat_action(CombatAction.DEFEND)
    elif action == "combat_dodge":
        game.combat_action(CombatAction.DODGE)
    elif action == "combat_flee":
        game.combat_action(CombatAction.FLEE)
    elif action == "level_up":
        game.open_level_up()
    elif action == "bonfire_leave":
        game.mode = GameMode.EXPLORATION
        game.update_ui()
    elif action.startswith("up_"):
        stat = action.replace("up_", "")
        stat_map = {"strength": "strength", "dexterity": "dexterity",
                   "intelligence": "intelligence", "faith": "faith"}
        if stat in stat_map:
            game.level_up(stat_map[stat])
    elif action == "level_up_back":
        game.mode = GameMode.BONFIRE
        game.update_ui()


def handle_input(event):
    from pyscript import document
    input_el = document.getElementById("player-input")
    value = input_el.value
    input_el.value = ""

    if game.mode == GameMode.NAME_INPUT:
        game.set_player_name(value)


def setup():
    from pyscript import document

    # 设置输入事件
    input_el = document.getElementById("player-input")
    input_el.addEventListener("keypress", lambda e: handle_input(e) if e.key == "Enter" else None)

    btn = document.getElementById("submit-btn")
    btn.onclick = lambda e: handle_input(None)

    # 启动游戏
    game.start()


# 页面加载后初始化
setup()
