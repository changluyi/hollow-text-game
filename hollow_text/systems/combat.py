"""
战斗系统 - 魂风格回合制战斗
核心原则：精力管理、时机把握、风险与回报
"""
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum
from random import random

from entities.player import Player
from entities.enemy import Enemy, EnemyAction


class CombatAction(Enum):
    """玩家战斗行动"""
    ATTACK = "attack"       # 攻击 (消耗6精力)
    HEAVY_ATTACK = "heavy"  # 重击 (消耗10精力，伤害高但后摇长)
    DEFEND = "defend"       # 防御 (消耗3精力，减少伤害)
    DODGE = "dodge"         # 闪避 (消耗5精力，完全躲避攻击)
    ITEM = "item"           # 使用物品
    FLEE = "flee"           # 逃跑


class CombatResult(Enum):
    """战斗结果"""
    ONGOING = "ongoing"     # 战斗进行中
    PLAYER_WIN = "win"      # 玩家胜利
    PLAYER_DEATH = "death"  # 玩家死亡
    FLED = "fled"           # 逃跑成功


@dataclass
class CombatLog:
    """战斗日志"""
    turn: int
    player_action: CombatAction
    enemy_action: EnemyAction
    player_damage_dealt: int = 0
    player_damage_taken: int = 0
    message: str = ""


class CombatSystem:
    """战斗系统"""

    # 精力消耗
    STAMINA_COST = {
        CombatAction.ATTACK: 6,
        CombatAction.HEAVY_ATTACK: 10,
        CombatAction.DEFEND: 3,
        CombatAction.DODGE: 5,
        CombatAction.ITEM: 0,
        CombatAction.FLEE: 0,
    }

    # 伤害倍率
    DAMAGE_MULTIPLIER = {
        CombatAction.ATTACK: 1.0,
        CombatAction.HEAVY_ATTACK: 1.8,
    }

    def __init__(self, player: Player, enemy: Enemy):
        self.player = player
        self.enemy = enemy
        self.turn = 0
        self.result = CombatResult.ONGOING
        self.logs: list[CombatLog] = []
        self._is_player_stunned = False  # 玩家是否硬直

    def is_player_turn_valid(self, action: CombatAction) -> Tuple[bool, str]:
        """检查玩家行动是否有效"""
        if not self.player.is_alive:
            return False, "你已经死亡了..."

        stamina_cost = self.STAMINA_COST.get(action, 0)
        if self.player.stamina < stamina_cost:
            return False, f"精力不足！需要 {stamina_cost} 精力，当前只有 {self.player.stamina}"

        if self._is_player_stunned and action not in [CombatAction.DEFEND, CombatAction.ITEM]:
            return False, "你正处于硬直状态，只能防御或使用物品..."

        return True, ""

    def execute_turn(self, player_action: CombatAction) -> CombatLog:
        """执行一个回合"""
        self.turn += 1
        log = CombatLog(
            turn=self.turn,
            player_action=player_action,
            enemy_action=self.enemy.current_action
        )

        # 重置硬直状态
        self._is_player_stunned = False

        # 获取敌人下一步行动
        enemy_next_action = self.enemy.decide_action()

        # 处理玩家行动
        player_damage = 0
        player_message = ""

        if player_action == CombatAction.ATTACK:
            player_damage, player_message = self._player_attack()
        elif player_action == CombatAction.HEAVY_ATTACK:
            player_damage, player_message = self._player_heavy_attack()
        elif player_action == CombatAction.DEFEND:
            player_message = self._player_defend()
        elif player_action == CombatAction.DODGE:
            player_message = self._player_dodge()
        elif player_action == CombatAction.FLEE:
            if self._attempt_flee():
                self.result = CombatResult.FLED
                log.message = "你成功逃离了战斗！"
                return log
            player_message = "逃跑失败！敌人挡住了你的去路。"

        # 消耗精力
        stamina_cost = self.STAMINA_COST.get(player_action, 0)
        self.player.use_stamina(stamina_cost)

        # 处理敌人行动（如果敌人还活着）
        enemy_damage = 0
        enemy_message = ""

        if self.enemy.is_alive and enemy_next_action == EnemyAction.ATTACK:
            enemy_damage, enemy_message = self._enemy_attack(player_action)

        # 更新日志
        log.player_damage_dealt = player_damage
        log.player_damage_taken = enemy_damage
        log.message = f"{player_message}\n{enemy_message}".strip()

        # 检查战斗结果
        self._check_result()

        # 回合结束恢复少量精力
        self.player.recover_stamina(2)
        self.enemy.recover_stamina(2)

        self.logs.append(log)
        return log

    def _player_attack(self) -> Tuple[int, str]:
        """玩家普通攻击"""
        damage = int(self.player.calculate_attack_damage() * self.DAMAGE_MULTIPLIER[CombatAction.ATTACK])

        # 判断是否在敌人脆弱时攻击
        if self.enemy.is_vulnerable():
            damage = int(damage * 1.5)  # 额外50%伤害
            actual_damage = self.enemy.take_damage(damage)
            return actual_damage, f"趁机攻击！对 {self.enemy.name} 造成 {actual_damage} 点伤害！"

        # 正常攻击
        actual_damage = self.enemy.take_damage(damage)

        # 重击会让玩家进入短暂硬直
        if actual_damage > 15:
            self._is_player_stunned = True
            return actual_damage, f"对 {self.enemy.name} 造成 {actual_damage} 点伤害！但你用力过猛，动作僵直了..."

        return actual_damage, f"对 {self.enemy.name} 造成 {actual_damage} 点伤害！"

    def _player_heavy_attack(self) -> Tuple[int, str]:
        """玩家重击 - 高风险高回报"""
        damage = int(self.player.calculate_attack_damage() * self.DAMAGE_MULTIPLIER[CombatAction.HEAVY_ATTACK])

        # 重击必然导致硬直
        self._is_player_stunned = True

        if self.enemy.is_vulnerable():
            damage = int(damage * 2)  # 脆弱时双倍伤害
            actual_damage = self.enemy.take_damage(damage)
            return actual_damage, f"致命重击！对 {self.enemy.name} 造成 {actual_damage} 点巨额伤害！"

        actual_damage = self.enemy.take_damage(damage)
        return actual_damage, f"重击！对 {self.enemy.name} 造成 {actual_damage} 点伤害！但你暴露了破绽..."

    def _player_defend(self) -> str:
        """玩家防御"""
        self.player.defense += 10  # 临时增加防御
        return "你举起盾牌，准备承受攻击。"

    def _player_dodge(self) -> str:
        """玩家闪避"""
        dodge_chance = self.player.calculate_dodge_chance()
        if random() < dodge_chance:
            return "你灵活地闪开了！"
        return "闪避失败！你没能躲开敌人的视线。"

    def _enemy_attack(self, player_action: CombatAction) -> Tuple[int, str]:
        """敌人攻击"""
        damage = self.enemy.calculate_attack_damage()

        # 检查玩家是否闪避成功
        if player_action == CombatAction.DODGE:
            dodge_chance = self.player.calculate_dodge_chance()
            if random() < dodge_chance:
                return 0, f"{self.enemy.name} 的攻击被你闪开了！"

        # 检查玩家是否防御
        if player_action == CombatAction.DEFEND:
            damage = int(damage * 0.3)  # 防御减少70%伤害
            actual_damage = self.player.take_damage(damage)
            self.player.defense -= 10  # 移除临时防御加成
            return actual_damage, f"{self.enemy.name} 的攻击打在盾牌上，你受到 {actual_damage} 点伤害。"

        # 正常受击
        actual_damage = self.player.take_damage(damage)
        return actual_damage, f"{self.enemy.name} 的攻击命中了！你受到 {actual_damage} 点伤害！"

    def _attempt_flee(self) -> bool:
        """尝试逃跑"""
        # 基于敏捷计算逃跑成功率
        flee_chance = 0.3 + (self.player.stats.dexterity * 0.02)
        return random() < flee_chance

    def _check_result(self) -> None:
        """检查战斗结果"""
        if not self.enemy.is_alive:
            self.result = CombatResult.PLAYER_WIN
        elif not self.player.is_alive:
            self.result = CombatResult.PLAYER_DEATH

    def get_combat_status(self) -> str:
        """获取战斗状态描述"""
        enemy_action_desc = self.enemy.get_action_description()
        return f"""
【第 {self.turn} 回合】

敌人: {self.enemy.name}
HP: {self._hp_bar(self.enemy.hp, self.enemy.max_hp)} {self.enemy.hp}/{self.enemy.max_hp}
状态: {enemy_action_desc}

你的状态:
HP: {self._hp_bar(self.player.hp, self.player.max_hp)} {self.player.hp}/{self.player.max_hp}
精力: {self._hp_bar(self.player.stamina, self.player.max_stamina)} {self.player.stamina}/{self.player.max_stamina}
"""

    @staticmethod
    def _hp_bar(current: int, maximum: int, length: int = 10) -> str:
        """生成血条/精力条"""
        filled = int((current / maximum) * length)
        return "█" * filled + "░" * (length - filled)
