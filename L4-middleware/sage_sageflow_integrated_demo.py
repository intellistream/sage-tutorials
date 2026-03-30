#!/usr/bin/env python3
"""Migration note for the retired SageFlow integration demo."""

from sage.foundation import CustomLogger


def main() -> None:
    print("此教程原本演示旧版 SageFlow 与 SAGE 的 middleware 集成。")
    print("当前收敛方向是：核心编排统一使用 sage.runtime 与 sage.stream。")
    print(
        "如需外部向量流/聚合能力，请通过独立适配包集成，而不是依赖旧 middleware 路径。"
    )


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
