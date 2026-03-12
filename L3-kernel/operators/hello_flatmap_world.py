# 此例意在说明FlatMap的使用
from sage.foundation import (
    BatchFunction,
    CustomLogger,
    FlatMapFunction,
    MapFunction,
    SinkFunction,
)
from sage.runtime import LocalEnvironment


class HelloBatch(BatchFunction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        self.max_count = 10

    def execute(self):
        if self.counter >= self.max_count:
            return None
        self.counter += 1
        return f"Hello, World! #{self.counter}"


class UpperCaseMap(MapFunction):
    def execute(self, data):
        return data.upper()


class PrintSink(SinkFunction):
    def execute(self, data):
        print(data)


# 利用FlatMapFunction实现单词拆分
class SplitWords(FlatMapFunction):
    def execute(self, data):
        words = data.split()
        return words


def main():
    env = LocalEnvironment("Hello_Flatmap_World")

    env.from_batch(HelloBatch).map(UpperCaseMap).flatmap(SplitWords).sink(PrintSink)

    env.submit(autostop=True)
    print("Hello Flatmap World 示例结束")


if __name__ == "__main__":
    # 关闭日志输出
    CustomLogger.disable_global_console_debug()
    main()
