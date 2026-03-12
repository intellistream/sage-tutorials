from sage.foundation import CustomLogger


def main():
    print("此教程原本演示已退役的 sage_flow 微服务适配层。")
    print("现在请使用 sage.runtime.LocalEnvironment 构建核心数据流，")
    print("如确需外部向量流能力，请通过独立适配包接入，而不是依赖旧 middleware 路径。")


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
