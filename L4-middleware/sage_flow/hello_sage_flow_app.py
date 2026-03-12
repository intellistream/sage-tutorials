from sage.foundation import CustomLogger


def main():
    print("此教程原本演示旧版 sage_flow 绑定式应用接口。")
    print(
        "现在建议直接使用 sage.runtime.LocalEnvironment 与标准 Source/Map/Sink 算子。"
    )


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
