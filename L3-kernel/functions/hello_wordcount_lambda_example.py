#!/usr/bin/env python3
"""
SAGE WordCount Lambda 示例
@test:timeout=120
@test:category=streaming
"""

import os
import time
from collections import Counter

from sage.foundation import SourceFunction
from sage.runtime import LocalEnvironment

# 设置日志级别为ERROR减少输出
os.environ.setdefault("SAGE_LOG_LEVEL", "ERROR")


# 简单的句子源，重复输出同一句话
class SentenceSource(SourceFunction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sentences = [
            "hello world sage framework",
            "this is a streaming data processing example",
            "lambda functions make the code much cleaner",
            "word count is a classic big data example",
            "sage provides powerful stream processing capabilities",
        ]
        self.counter = 0

    def execute(self, data=None):
        # 随机选择一个句子，或者循环输出
        sentence = self.sentences[self.counter % len(self.sentences)]
        self.counter += 1
        return sentence


def main():
    # 创建环境
    env = LocalEnvironment("wordcount_example")

    # 全局词汇计数器
    word_counts = Counter()
    total_processed = 0

    def update_word_count(words_with_count):
        """更新全局词汇计数"""
        nonlocal total_processed
        word, count = words_with_count
        word_counts[word] += count
        total_processed += count

        # 每处理10个词就打印一次统计结果
        if total_processed % 10 == 0:
            print(f"\n=== Word Count Statistics (Total: {total_processed}) ===")
            for word, count in word_counts.most_common(10):
                print(f"{word:20}: {count:3d}")
            print("=" * 50)

    # 构建流处理管道
    (
        env.from_source(SentenceSource, delay=1.0)  # 每秒产生一个句子
        # 数据清洗和预处理
        .map(lambda sentence: sentence.lower())  # 转小写
        .map(lambda sentence: sentence.strip())  # 去除首尾空白
        .filter(lambda sentence: len(sentence) > 0)  # 过滤空字符串
        # 分词处理
        .flatmap(lambda sentence: sentence.split())  # 按空格分词
        .filter(lambda word: len(word) > 2)  # 过滤长度小于3的词
        .map(lambda word: word.replace(",", "").replace(".", ""))  # 去除标点
        # 词汇统计
        .map(lambda word: (word, 1))  # 转换为 (word, count) 格式
        .print()  # 更新计数器
    )

    print("🚀 Starting WordCount Example with Lambda Functions")
    print("📝 Processing sentences and counting words...")
    print("⏹️  Press Ctrl+C to stop")

    try:
        # 运行流处理
        env.submit()

        # 在测试模式下运行更短时间
        test_mode = os.environ.get("SAGE_EXAMPLES_MODE") == "test"
        runtime = 10 if test_mode else 60

        print(f"⏰ Running for {runtime} seconds...")
        time.sleep(runtime)  # 测试模式运行10秒，正常模式60秒
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping WordCount Example...")
        print("\n📊 Final Word Count Results:")
        print("=" * 60)
        for word, count in word_counts.most_common():
            print(f"{word:20}: {count:3d}")
        print("=" * 60)
        print(f"Total words processed: {total_processed}")
    finally:
        env.close()


if __name__ == "__main__":
    main()
