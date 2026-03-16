"""
工具函数 - 通用辅助函数
"""
import os
import time
from typing import Any


def clear_screen() -> None:
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def delay(seconds: float = 0.5) -> None:
    """延迟"""
    time.sleep(seconds)


def clamp(value: int, min_val: int, max_val: int) -> int:
    """限制值在范围内"""
    return max(min_val, min(max_val, value))


def format_number(number: int) -> str:
    """格式化数字（添加千位分隔符）"""
    return f"{number:,}"


def pluralize(word: str, count: int) -> str:
    """单复数处理"""
    if count == 1:
        return word
    return f"{word}s"
