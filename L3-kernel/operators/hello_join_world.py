# 此例用到了keyby和join操作符，展示如何将两个数据流按key进行关联。
from sage.foundation import (
    BaseJoinFunction,
    BatchFunction,
    CustomLogger,
    KeyByFunction,
    SinkFunction,
)
from sage.runtime import LocalEnvironment


class SourceOne(BatchFunction):
    def __init__(self):
        super().__init__()
        self.counter = 0

    def execute(self):
        self.counter += 1
        if self.counter > 5:
            return None
        return {"id": self.counter, "msg": f"Hello-{self.counter}", "type": "hello"}


class SourceTwo(BatchFunction):
    def __init__(self):
        super().__init__()
        self.counter = 0

    def execute(self):
        self.counter += 1
        if self.counter > 5:
            return None
        return {"id": self.counter, "msg": f"World-{self.counter}", "type": "world"}


class IdKeyBy(KeyByFunction):
    def execute(self, data):
        return data.get("id")


class PrintSink(SinkFunction):
    def execute(self, data):
        print(f"🔗 Joined Streaming: {data}")


class HelloWorldJoin(BaseJoinFunction):
    """
    Join 算子示例：
    execute(payload, key, tag) 参数说明：
      - payload: 流里传过来的原始数据 (dict)
      - key: 由 keyby 算子提取出来的分区键 (比如这里的 id)
      - tag: 数据来源标识 (0=左流 / 第一个流, 1=右流 / 第二个流)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hello_cache = {}  # {key: [payloads]}
        self.world_cache = {}  # {key: [payloads]}

    def execute(self, payload, key, tag):
        results = []
        data_type = payload.get("type", "")

        if tag == 0:  # 第一个流 (Hello)
            if data_type == "hello":
                # 缓存 Hello 数据
                self.hello_cache.setdefault(key, []).append(payload)

                # 检查是否有匹配的 World 数据
                if key in self.world_cache:
                    for world_data in self.world_cache[key]:
                        results.append(self._merge(payload, world_data, key))

        elif tag == 1:  # 第二个流 (World)
            if data_type == "world":
                # 缓存 World 数据
                self.world_cache.setdefault(key, []).append(payload)

                # 检查是否有匹配的 Hello 数据
                if key in self.hello_cache:
                    for hello_data in self.hello_cache[key]:
                        results.append(self._merge(hello_data, payload, key))

        return results

    def _merge(self, hello_data, world_data, key):
        return {"id": key, "msg": f"{hello_data['msg']} + {world_data['msg']}"}


def main():
    env = LocalEnvironment("hello_join_world")

    source1 = env.from_batch(SourceOne)
    source2 = env.from_batch(SourceTwo)

    source1.keyby(IdKeyBy).connect(source2.keyby(IdKeyBy)).join(HelloWorldJoin).sink(
        PrintSink
    )

    # 使用 autostop=True 让框架自动检测处理完成
    env.submit(autostop=True)

    print("Hello Join World 示例结束")


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()
