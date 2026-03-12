#!/usr/bin/env python3
"""Migration note for the retired SageDB workflow demo.

@test:allow-demo
"""

from sage.foundation import CustomLogger


def main() -> None:
    print("此教程原本演示旧版 SageDB workflow DAG。")
    print("现在建议使用 sage.runtime.LocalEnvironment 编排主流程，")
    print("并通过独立适配包或外部向量库客户端接入检索能力。")
    print("可参考已收敛的 benchmark/examples 中的 vector_db service 模式。")


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
