#!/usr/bin/env python3
"""
Hello Three Input CoMap World

这个例子演示了如何使用CoMap操作处理三个输入流，每个流的数据
会被路由到对应的mapN方法进行独立处理。

CoMap（Co-processing Map）是一种多流处理操作，允许对连接的多个
数据流进行协同处理，每个输入流通过专用的mapN方法独立处理。
"""

from sage.foundation import BaseCoMapFunction, BatchFunction, CustomLogger, SinkFunction
from sage.runtime import LocalEnvironment


class SimpleDataSource(BatchFunction):
    """简单的批量数据源"""

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.index = 0

    def execute(self):
        if self.index >= len(self.data):
            return None
        result = self.data[self.index]
        self.index += 1
        return result


class ThreeStreamCoMapFunction(BaseCoMapFunction):
    """
    三输入流CoMap函数

    演示如何处理三个不同的输入流：
    - map0: 处理第一个流的数据
    - map1: 处理第二个流的数据
    - map2: 处理第三个流的数据
    """

    def map0(self, data):
        """处理第一个输入流的数据"""
        return f"🔴 Stream-0: {data}"

    def map1(self, data):
        """处理第二个输入流的数据"""
        return f"🟡 Stream-1: {data}"

    def map2(self, data):
        """处理第三个输入流的数据"""
        return f"🔵 Stream-2: {data}"


class ConsoleSink(SinkFunction):
    """控制台输出Sink"""

    def execute(self, data):
        print(data)


def main():
    """主函数：演示三输入流CoMap操作"""

    # 创建本地环境
    env = LocalEnvironment("ThreeInputCoMapExample")

    print("🚀 Starting Three Input CoMap Example...")
    print("=" * 50)

    # 创建三个数据源
    stream1 = env.from_batch(SimpleDataSource, ["Apple", "Banana"])
    stream2 = env.from_batch(SimpleDataSource, ["Cat", "Dog"])
    stream3 = env.from_batch(SimpleDataSource, ["Red", "Blue"])

    print("📊 Data sources created:")
    print("  Stream 1 (Fruits): [Apple, Banana]")
    print("  Stream 2 (Animals): [Cat, Dog]")
    print("  Stream 3 (Colors): [Red, Blue]")
    print()

    # 连接三个流并应用CoMap
    print("🔗 Connecting streams and applying CoMap...")
    (
        stream1.connect(stream2)
        .connect(stream3)
        .comap(ThreeStreamCoMapFunction)
        .sink(ConsoleSink)
    )

    print("⚙️ Processing data...")
    print()

    # 执行流处理
    env.submit(autostop=True)

    print()
    print("✅ Three Input CoMap Example completed!")
    print("=" * 50)
    print("📝 Each input stream was processed by its corresponding mapN method:")
    print("  - Stream 1 data → map0() → 🔴 Stream-0: ...")
    print("  - Stream 2 data → map1() → 🟡 Stream-1: ...")
    print("  - Stream 3 data → map2() → 🔵 Stream-2: ...")


if __name__ == "__main__":
    # 禁用全局调试日志以获得更清晰的输出
    CustomLogger.disable_global_console_debug()
    main()
