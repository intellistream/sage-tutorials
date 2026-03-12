import time

from sage.foundation import SinkFunction, SourceFunction
from sage.runtime import LocalEnvironment


# 简单的数字源
class NumberSource(SourceFunction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0

    def execute(self, data=None):
        self.counter += 1
        return self.counter


# 简单的统计汇总函数
class StatsSink(SinkFunction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self, data):
        print(f"[{self.name}] Received: {data}")
        return data


def main():
    # 创建环境
    env = LocalEnvironment("simple_connected_example")

    # 设置日志级别为WARNING以减少调试输出
    env.set_console_log_level("WARNING")

    print("🚀 Starting Simple Connected Streams Example")
    print("📊 Demonstrating multiple stream processing and connection")
    print("⏹️  Press Ctrl+C to stop\n")

    # 创建主数据源
    main_stream = env.from_source(NumberSource, delay=1.0)

    # 分支1：偶数流
    even_stream = (
        main_stream.filter(lambda x: x % 2 == 0).map(lambda x: ("EVEN", x))
        # .print("🔵 Even Stream")
    )

    # 分支2：奇数流
    odd_stream = (
        main_stream.filter(lambda x: x % 2 == 1).map(lambda x: ("ODD", x))
        # .print("🔴 Odd Stream")
    )

    # 分支3：倍数流（3的倍数）
    multiple_stream = (
        main_stream.filter(lambda x: x % 3 == 0).map(lambda x: ("MULTIPLE_3", x))
        # .print("🟡 Multiple-3 Stream")
    )

    # 分支4：大数流（大于5）
    large_stream = (
        main_stream.filter(lambda x: x > 5).map(lambda x: ("LARGE", x))
        # .print("🟢 Large Stream")
    )

    # 使用 ConnectedStreams 将所有分支连接起来
    print("\n🔗 Connecting all streams...")
    connected_streams = (
        even_stream.connect(odd_stream).connect(multiple_stream).connect(large_stream)
    )

    # 对连接的流进行统一处理
    (
        connected_streams.map(lambda data: f"Processed: {data[0]} -> {data[1]}")
        .print("🎯 Final Result")
        .sink(StatsSink, name="FinalSink")
    )

    print("📈 All streams connected and processing...\n")

    try:
        # 运行流处理
        env.submit()

        time.sleep(5)  # 运行5秒

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping Simple Connected Streams Example...")

    finally:
        print("\n📋 Example completed!")
        print("💡 This example demonstrated:")
        print("   - Multiple stream branches from single source")
        print("   - Independent filtering and processing")
        print("   - ConnectedStreams merging multiple flows")
        print("   - Unified final processing of merged streams")
        env.close()


if __name__ == "__main__":
    main()
