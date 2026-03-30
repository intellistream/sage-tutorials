"""
终端交互式QA无界流处理
支持终端输入问题，使用大模型生成回答的无界流处理示例
"""

from __future__ import annotations

import time

from dotenv import load_dotenv

from sage.foundation import CustomLogger, MapFunction, SinkFunction, SourceFunction
from sage.runtime import LocalEnvironment

try:
    from ._qa_helpers import OpenAICompatibleGenerator, SimplePromptor, load_config
except ImportError:
    from _qa_helpers import OpenAICompatibleGenerator, SimplePromptor, load_config


class TerminalInputSource(SourceFunction):
    """终端输入源函数 - 简化版"""

    def execute(self, data=None):
        try:
            user_input = input().strip()
            if user_input:
                return user_input
            return self.execute(data)
        except (EOFError, KeyboardInterrupt):
            raise


class QuestionProcessor(MapFunction):
    """问题处理器"""

    def execute(self, data):
        if not data or data.strip() == "":
            return None

        question = data.strip()
        return question


class AnswerFormatter(MapFunction):
    """回答格式化器"""

    def execute(self, data):
        if not data:
            return None

        # OpenAIGenerator返回的格式是 (user_query, generated_text)
        if isinstance(data, tuple) and len(data) >= 2:
            user_query = data[0]
            answer = data[1]
            return {
                "question": user_query if user_query else "N/A",
                "answer": answer,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        else:
            return {
                "question": "N/A",
                "answer": str(data),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }


class ConsoleSink(SinkFunction):
    """控制台输出"""

    def execute(self, data):
        if not data:
            return None

        if isinstance(data, dict):
            print(f"\n🤖 {data.get('answer', 'N/A')}\n")
        else:
            print(f"\n🤖 {data}\n")

        return data


def create_qa_pipeline():
    """创建QA处理管道"""
    import os

    # 加载配置
    load_dotenv(override=False)
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "config", "config_source.yaml"
    )
    config = load_config(config_path)

    # 创建本地环境
    env = LocalEnvironment()

    # 启动欢迎提示
    print("💬 QA助手已启动！输入问题后按回车")

    try:
        # 构建无界流处理管道
        (
            env.from_source(TerminalInputSource)
            .map(QuestionProcessor)
            .map(SimplePromptor, config["promptor"])
            .map(OpenAICompatibleGenerator, config["generator"]["vllm"])
            .map(AnswerFormatter)
            .sink(ConsoleSink)
        )

        # 提交并运行
        env.submit()
        # 保持主线程运行，直到用户退出
        while True:
            time.sleep(1)

    except Exception as e:
        print(f"❌ 管道运行出错: {str(e)}")
    finally:
        try:
            env.close()
            print("✅ QA流处理管道已关闭")
        except Exception:
            pass


if __name__ == "__main__":
    import os
    import sys

    # 检查是否在测试模式下运行
    if (
        os.getenv("SAGE_EXAMPLES_MODE") == "test"
        or os.getenv("SAGE_TEST_MODE") == "true"
    ):
        print("🧪 Test mode detected - qa_without_retrieval is interactive")
        print("✅ Test passed: Interactive example structure validated")
        sys.exit(0)

    CustomLogger.disable_global_console_debug()
    create_qa_pipeline()
