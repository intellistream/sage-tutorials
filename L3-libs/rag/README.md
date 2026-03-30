# RAG Tutorials

Simple RAG (Retrieval-Augmented Generation) examples to get started.

## Examples

### 1. Simple RAG (`simple_rag.py`)

Basic RAG pipeline example.

```bash
python examples/tutorials/rag/simple_rag.py
```

**Requirements**: API key (set in `.env`)

### 2. QA Without Retrieval (`qa_no_retrieval.py`)

Direct QA using LLM without retrieval.

```bash
python examples/tutorials/rag/qa_no_retrieval.py
```

### 3. QA with Local LLM (`qa_local_llm.py`)

QA using a local language model.

```bash
python examples/tutorials/rag/qa_local_llm.py
```

## Next Steps

- **Advanced RAG examples**: See `packages/sage-benchmark/src/sage/benchmark/benchmark_rag/` for
  production-ready RAG pipelines and benchmarks
- **Advanced RAG examples**: See `sage-benchmark/experiments/pipelines/` for production-ready
  RAG pipelines and benchmarks
- **Current core surface**: use `isage>=0.3.0` with `sage.foundation` / `sage.runtime`; add
  `isagellm` or `isage-rag` only when a specific retriever or gateway backend is needed
