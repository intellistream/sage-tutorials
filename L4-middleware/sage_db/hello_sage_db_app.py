from sage.foundation import CustomLogger


def main():
    print("此教程原本演示旧版 sage_db 应用接口。")
    print("当前推荐做法是：保留核心编排在 SAGE 内，")
    print("将向量存储能力交给独立适配包或外部数据库客户端。")


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
