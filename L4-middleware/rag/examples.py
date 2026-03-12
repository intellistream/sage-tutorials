"""
SAGE RAG - Usage Examples

This file demonstrates how to use the SAGE RAG (Retrieval-Augmented Generation) toolkit.

These legacy middleware demos are retained as migration notes.
Current guidance is to use core `sage` runtime/dataflow APIs plus optional adapter
packages such as `isage-rag` when advanced retrieval components are needed.
"""


def example_document_loading():
    """
    Example 1: Loading documents

    Demonstrates how to load documents from various sources using
    the document loaders.
    """
    print("=" * 60)
    print("Example 1: Loading Documents")
    print("=" * 60)

    try:
        from sage.libs.rag.document_loaders import (
            DocxLoader,  # noqa: F401
            LoaderFactory,  # noqa: F401
            MarkdownLoader,  # noqa: F401
            PDFLoader,  # noqa: F401
            TextLoader,  # noqa: F401
        )

        print("\n✓ Available document loaders:")
        print("  - TextLoader: Load plain text files")
        print("  - PDFLoader: Load PDF documents")
        print("  - DocxLoader: Load Word documents")
        print("  - MarkdownLoader: Load Markdown files")
        print("  - LoaderFactory: Auto-detect and load files")

        # Example: Loading text files
        print("\nExample: Loading a text file")
        print(
            """
        loader = TextLoader("documents/article.txt")
        documents = loader.load()
        for doc in documents:
            print(f"Content: {doc.content[:100]}...")
        """
        )

    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Some document loaders may require additional dependencies")


def example_rag_pipeline():
    """
    Example 2: Building a RAG pipeline

    Demonstrates how to build a complete RAG pipeline with
    document loading, embedding, retrieval, and generation.
    """
    print("\n" + "=" * 60)
    print("Example 2: Building a RAG Pipeline")
    print("=" * 60)

    print("\n✓ Recommended RAG building blocks:")
    print("  1. Load documents with your preferred loader")
    print("  2. Build prompts as normal Python/SAGE operators")
    print("  3. Use an OpenAI-compatible embedding endpoint or isagellm")
    print("  4. Store vectors in an optional adapter backend such as isage-rag")
    print("  5. Execute retrieval + generation in a core `sage.runtime` pipeline")

    print("\nExample migration sketch:")
    print(
        """
    from sage.runtime import LocalEnvironment
    from sage.foundation import MapFunction

    env = LocalEnvironment("rag-demo")

    # 1. Load and split documents in plain Python
    # 2. Generate embeddings with isagellm or another OpenAI-compatible endpoint
    # 3. Persist/search vectors with an optional adapter such as isage-rag
    # 4. Feed retrieved context into a normal SAGE map pipeline

    env.submit(autostop=True)
    """
    )


def example_vector_stores():
    """
    Example 3: Using vector stores

    Demonstrates how to use different vector store backends
    for storing and retrieving embeddings.
    """
    print("\n" + "=" * 60)
    print("Example 3: Vector Store Integration")
    print("=" * 60)

    print("\n✓ Supported vector stores:")
    print("  - Milvus: Distributed vector database")
    print("  - Chroma: Lightweight in-memory store")
    print("  - FAISS: Facebook AI Similarity Search")

    print("\nExample: Using an optional Milvus adapter")
    print(
        """
    # Use an optional adapter package, for example isage-rag, to connect Milvus.
    # Keep orchestration and prompting in your normal SAGE pipeline.
    """
    )

    print("\nExample: Using an optional Chroma adapter")
    print(
        """
    # Use an optional adapter package to manage Chroma persistence/search.
    # The core SAGE runtime remains responsible for pipeline orchestration.
    """
    )


def example_profiling():
    """
    Example 4: RAG performance profiling

    Demonstrates how to profile and optimize RAG pipelines
    using the built-in profiler.
    """
    print("\n" + "=" * 60)
    print("Example 4: RAG Pipeline Profiling")
    print("=" * 60)

    print("\n✓ Profiling ideas for modern RAG pipelines:")
    print("  - Measure retrieval latency")
    print("  - Track context length and token budget")
    print("  - Log query complexity and routing decisions")
    print("  - Compare answer quality across retriever/generator settings")

    print("\nExample profiling sketch:")
    print(
        """
    metrics = {
        "retrieval_ms": 18.4,
        "generation_ms": 241.7,
        "context_chars": 1532,
        "strategy": "single-retrieval",
    }
    print(metrics)
    """
    )


def example_advanced_retrieval():
    """
    Example 5: Advanced retrieval strategies

    Demonstrates advanced retrieval techniques like hybrid search,
    reranking, and query expansion.
    """
    print("\n" + "=" * 60)
    print("Example 5: Advanced Retrieval Strategies")
    print("=" * 60)

    print("\n✓ Advanced retrieval techniques:")
    print("  - Hybrid search: Combine dense + sparse retrieval")
    print("  - Reranking: Post-process retrieval results")
    print("  - Query expansion: Enhance queries with synonyms")
    print("  - Multi-hop retrieval: Iterative retrieval")

    print("\nExample: Hybrid search")
    print(
        """
    # Combine dense (embedding) and sparse (BM25) retrieval
    dense_results = vector_store.search(query_embedding, top_k=20)
    sparse_results = bm25_index.search(query_text, top_k=20)

    # Merge and rerank
    combined = merge_results(dense_results, sparse_results)
    reranked = reranker.rerank(query, combined, top_k=5)
    """
    )

    print("\nExample: Query expansion")
    print(
        """
    # Expand query with synonyms and related terms
    original_query = "machine learning algorithms"
    expanded_query = query_expander.expand(original_query)
    # Result: "machine learning algorithms ML AI models neural networks"

    # Use expanded query for retrieval
    results = vector_store.search(expanded_query, top_k=10)
    """
    )


def run_all_examples():
    """Run all examples in sequence."""
    print("\n" + "=" * 60)
    print("SAGE RAG - Complete Examples")
    print("=" * 60)

    example_document_loading()
    example_rag_pipeline()
    example_vector_stores()
    example_profiling()
    example_advanced_retrieval()

    print("\n" + "=" * 60)
    print("✓ All examples completed")
    print("=" * 60)
    print("\nFor more information:")
    print("- See rag/README.md for detailed documentation")
    print("- Check examples/ for complete working examples")
    print("- Visit docs/ for RAG best practices")


if __name__ == "__main__":
    run_all_examples()
