from sage.foundation import CustomLogger


def main():
    print("此教程原本演示已退役的 sage_db 微服务接口。")
    print("现在建议在核心 SAGE pipeline 中接入独立向量库适配器，")
    print("例如使用 isage-rag 或其他 OpenAI-compatible embedding/vector backend。")


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
