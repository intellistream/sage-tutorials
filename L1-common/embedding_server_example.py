"""
Embedding Server 使用示例

这个示例展示如何使用本地 embedding 服务器，
无需修改任何原有代码，直接通过 get_embedding_model 调用。

Requirements:
    pip install isage>=0.3.0

Test Configuration:
    @test_category: tutorials
    @test_speed: quick
    @test_skip_ci: true
    @test:skip - Requires embedding server to be running
"""

import os

from sagellm.embedding import get_embedding_model
from sage.foundation import SagePorts

# Check test mode
_IS_TEST_MODE = (
    os.getenv("SAGE_TEST_MODE") == "true"
    or os.getenv("SAGE_EXAMPLES_MODE") == "test"
    or os.getenv("CI") == "true"
)

# Use SagePorts for embedding port configuration
EMBEDDING_PORT = SagePorts.EMBEDDING_SECONDARY  # 8091


def _create_openai_embedder(base_url: str, model: str):
    normalized_base_url = base_url[:-3] if base_url.endswith("/v1") else base_url
    return get_embedding_model(
        "openai",
        model=model,
        base_url=normalized_base_url,
        api_key="dummy",
    )


def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("示例 1: 基本使用")
    print("=" * 60)

    # In test mode, just show configuration
    if _IS_TEST_MODE:
        print("\n[Test mode] Would connect to embedding server:")
        print(f"  URL: http://localhost:{EMBEDDING_PORT}/v1")
        print("  Model: BAAI/bge-m3")
        print("  Skipping actual server connection")
        return

    # 创建 embedding 模型实例（连接到本地服务器）
    embedding_model = _create_openai_embedder(
        base_url=f"http://localhost:{EMBEDDING_PORT}",
        model="BAAI/bge-m3",
    )

    # 测试 embedding
    text = "Hello, this is a test sentence."
    print(f"\nInput text: {text}")

    embedding = embedding_model.embed(text)
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")


def example_batch_processing():
    """批量处理示例"""
    print("\n" + "=" * 60)
    print("示例 2: 批量处理")
    print("=" * 60)

    # 多个文本
    texts = [
        "What is machine learning?",
        "Deep learning is a subset of machine learning.",
        "Natural language processing uses neural networks.",
    ]

    # In test mode, just show configuration
    if _IS_TEST_MODE:
        print(f"\n[Test mode] Would process {len(texts)} texts:")
        for text in texts:
            print(f"  - {text}")
        print("  Skipping actual server connection")
        return

    embedding_model = _create_openai_embedder(
        base_url=f"http://localhost:{EMBEDDING_PORT}",
        model="BAAI/bge-m3",
    )

    print(f"\nProcessing {len(texts)} texts...")
    for i, text in enumerate(texts, 1):
        embedding = embedding_model.embed(text)
        print(f"{i}. Text: '{text[:50]}...' -> Embedding dim: {len(embedding)}")


def example_with_different_server():
    """使用不同服务器端口的示例"""
    print("\n" + "=" * 60)
    print("示例 3: 使用不同服务器")
    print("=" * 60)

    # In test mode, just show configuration
    if _IS_TEST_MODE:
        print("\n[Test mode] Would connect to custom server:")
        print("  URL: http://localhost:8081/v1")
        print("  Model: custom-model")
        print("  Skipping actual server connection")
        return

    # 假设你在端口 8081 运行另一个模型
    embedding_model = _create_openai_embedder(
        base_url="http://localhost:8081",
        model="custom-model",
    )

    text = "Testing with different server port"
    try:
        embedding = embedding_model.embed(text)
        print(f"Success. Embedding dimension: {len(embedding)}")
    except Exception as e:
        print(f"Error (expected if server not running): {e}")


def example_error_handling():
    """错误处理示例"""
    print("\n" + "=" * 60)
    print("示例 4: 错误处理")
    print("=" * 60)

    # In test mode, just show configuration
    if _IS_TEST_MODE:
        print("\n[Test mode] Would test error handling:")
        print("  - Empty text handling")
        print("  - Long text (truncation) handling")
        print("  Skipping actual server connection")
        return

    embedding_model = _create_openai_embedder(
        base_url=f"http://localhost:{EMBEDDING_PORT}",
        model="BAAI/bge-m3",
    )

    # 测试空文本
    try:
        embedding = embedding_model.embed("")
        print(f"Empty text embedding dimension: {len(embedding)}")
    except Exception as e:
        print(f"Error with empty text: {e}")

    # 测试很长的文本（会被截断）
    long_text = "This is a very long sentence. " * 100
    try:
        embedding = embedding_model.embed(long_text)
        print(f"Long text (truncated) embedding dimension: {len(embedding)}")
    except Exception as e:
        print(f"Error with long text: {e}")


def main():
    """主函数"""

    # In test mode, skip early
    if _IS_TEST_MODE:
        print("\n" + "=" * 60)
        print("Embedding Server 使用示例 [Test Mode]")
        print("=" * 60)
        print("\n[Test mode] Running examples without server connection")

        example_basic_usage()
        example_batch_processing()
        example_with_different_server()
        example_error_handling()

        print("\n" + "=" * 60)
        print("所有示例完成. (Test mode - no actual server calls)")
        print("=" * 60)
        return

    print("\n")
    print("=" * 60)
    print("Embedding Server 使用示例")
    print("=" * 60)
    print("\n请确保 embedding 服务器已启动:")
    print(
        f"  python -m sagellm_core.embedding_server --model BAAI/bge-m3 --port {EMBEDDING_PORT}"
    )
    print("\n或手动启动:")
    print(
        f"  python -m sagellm_core.embedding_server --model BAAI/bge-m3 --port {EMBEDDING_PORT}"
    )
    print("\n" + "=" * 60 + "\n")

    try:
        # 运行示例
        example_basic_usage()
        example_batch_processing()
        example_with_different_server()
        example_error_handling()

        print("\n" + "=" * 60)
        print("所有示例完成.")
        print("=" * 60)

    except Exception as e:
        print(f"\n错误: {e}")
        print("\n请确保 embedding 服务器正在运行:")
        print(
            f"  python -m sagellm_core.embedding_server --model BAAI/bge-m3 --port {EMBEDDING_PORT}"
        )


if __name__ == "__main__":
    main()
