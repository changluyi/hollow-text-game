#!/usr/bin/env python3
"""
《虚渊文字》Hollow Text
一款受《黑暗之魂》系列启发的文字 Roguelike 游戏

依赖安装: pip install rich
运行游戏: python main.py

作者: Claude Code
版本: 0.1.0 (MVP)
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.engine import GameEngine


def main():
    """游戏入口"""
    try:
        engine = GameEngine()
        engine.run()
    except KeyboardInterrupt:
        print("\n\n游戏已退出。")
        sys.exit(0)
    except Exception as e:
        print(f"\n游戏发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
