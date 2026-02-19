# SAGE Tutorials Copilot Instructions

## 🚨 Runtime Direction (Cross-Repo)

- `sageFlownet` is the runtime component that replaces `Ray` in the SAGE ecosystem.
- Tutorials that mention runtime, scheduling, or distributed execution should use Flownet-oriented guidance.
- Do NOT add new `ray` imports/dependency instructions in tutorials.

## 🚨 Installation Consistency (Cross-Repo)

- 在 conda 环境中，**必须**使用 `python -m pip`，不要直接使用 `pip`。
- 涉及 SAGE 主仓库能力时，先在 `SAGE/` 执行 `./quickstart.sh --dev --yes`。
- SAGE quickstart 已显式安装核心独立 PyPI 依赖（如 `isagellm`、`isage-flownet`、`isage-vdb` 等），不要再建议通过 extras 手动补装核心依赖。

## Overview

**sage-tutorials** is the official tutorial repository for the SAGE framework, containing hands-on examples organized by architecture layers (L1-L5).

## 🚨 CRITICAL Principles

### Repository Scope

This repository contains **ONLY tutorials and learning materials**. It does NOT contain:
- ❌ SAGE core framework code (in `intellistream/SAGE`)
- ❌ Production applications (in `intellistream/sage-examples`)
- ❌ Benchmark framework (in `intellistream/sage-benchmark`)
- ❌ Documentation website (in `intellistream/SAGE-Pub`)

### SAGE Dependency

**All tutorials depend on SAGE being installed.**

```bash
# SAGE must be installed first
git clone https://github.com/intellistream/SAGE.git
cd SAGE
./quickstart.sh --dev --yes

# Then tutorials can be run
cd ../sage-tutorials
python L1-common/hello_world.py
```

### ❌ NO FALLBACK LOGIC - PROJECT-WIDE RULE

Follow SAGE's fail-fast principle:

```python
# ❌ BAD - Silent fallback
try:
    from sage.llm import UnifiedInferenceClient
except ImportError:
    print("SAGE not installed, using mock")
    UnifiedInferenceClient = MockClient

# ✅ GOOD - Fail fast with clear error
from sage.llm import UnifiedInferenceClient  # ImportError if SAGE not installed
```

### ❌ NEVER MANUAL PIP INSTALL

Dependencies must be documented in README, not installed via commands in tutorials:

```python
# ❌ BAD
# !pip install transformers

# ✅ GOOD - Document in tutorial header
"""
Requirements:
    - isage-common>=0.2.0
    - isagellm>=0.2.0
    - transformers>=4.52.0

Install: python -m pip install isage-common isagellm transformers
"""
```

## SAGE Architecture Reference

SAGE has 5 layers (L1-L5):

```
L5: sage-cli, sage-tools                    # CLI & Dev Tools
L4: sage-middleware                         # Operators (C++ extensions)
L3: sage-kernel, sage-libs                  # Dataflow Engine + Algorithms
L2: sage-platform                           # Platform Services
L1: sage-common                             # Foundation
```

**PyPI Packages**: All use `isage-*` prefix (e.g., `isage-common`, `isage-libs`)

## Tutorial Structure

```
sage-tutorials/
├── L1-common/              # Foundation layer
│   ├── hello_world.py
│   ├── unified_inference_client_example.py
│   └── embedding_server_example.py
├── L2-platform/            # Platform services
│   └── environment/
├── L3-kernel/              # Dataflow engine
│   ├── stream/
│   ├── batch/
│   ├── operators/
│   ├── functions/
│   └── advanced/
├── L3-libs/                # Algorithm libraries
│   ├── llm/
│   ├── rag/
│   ├── agents/
│   ├── embeddings/
│   └── unlearning/
├── L4-middleware/          # Middleware components
│   ├── sage_db/
│   ├── sage_flow/
│   └── rag/
├── L5-apps/                # Applications
└── config/                 # Configuration examples
```

## Writing Good Tutorials

### Tutorial Template

```python
"""
Brief description of what this tutorial demonstrates.

Layer: L{1-5}
Concepts: [list key concepts]

Requirements:
    - isage-common>=0.2.0
    - (other dependencies)

Usage:
    python path/to/tutorial.py
"""

# Clear comments explaining each step
# Minimal, runnable code
# Print intermediate results
# Handle errors gracefully (not silently!)
```

### Naming Conventions

- `hello_*.py` - Introductory examples
- `*_demo.py` - Feature demonstrations
- `*_example.py` - Practical use cases
- `*_tutorial.py` - Step-by-step guides

### Documentation Requirements

Each directory should have:
- `README.md` - Overview and learning path
- Clear comments in code
- Prerequisites listed
- Expected output documented

## Common Issues

### Import Errors

```python
# If SAGE not installed, tutorials will fail with ImportError
# This is INTENTIONAL - fail fast, don't hide the problem
from sage.llm import UnifiedInferenceClient  # Requires isagellm
```

### Service Dependencies

Some tutorials require services (LLM Gateway, embeddings):

```python
# Document service requirements in docstring
"""
Requirements:
    - SAGE Gateway running (sage gateway start)
    - LLM engine started (sage llm engine start <model>)
"""
```

### API Keys

```python
# Never hardcode API keys
# Document environment variables needed
"""
Environment Variables:
    OPENAI_API_KEY - Required for OpenAI models
    HF_TOKEN - Required for HuggingFace models
"""
```

## How Copilot Should Learn SAGE Tutorials

### Documentation-First Approach

Before answering questions or modifying code:

1. **Read layer README** - Each L{1-5} directory has a README
2. **Check QUICK_START.md** - 5-minute introduction
3. **Review example code** - Look at existing tutorials for patterns
4. **Consult SAGE docs** - Main framework documentation when needed

**Common Documentation Locations**:
- Root: `README.md`, `QUICK_START.md`
- Layer guides: `L{1-5}-*/README.md`
- Config examples: `config/`
- SAGE main docs: https://sage.intellistream.com

### 🔍 When Encountering Difficulties

1. **First**, check if relevant tutorial already exists
2. **Use tools** (`grep_search`, `semantic_search`) to find similar examples
3. **Read before acting** - understand existing patterns
4. **Consult SAGE instructions** - Reference main SAGE copilot instructions

**Rule**: Don't guess. Read the docs and examples. They exist for this reason.

## Relationship with SAGE Main Repository

```
┌──────────────────────────────────────────────┐
│ SAGE Main Repository                         │
│ (intellistream/SAGE)                         │
├──────────────────────────────────────────────┤
│ • Core framework packages                    │
│ • Development tools                          │
│ • Documentation site                         │
│ • CI/CD                                      │
└──────────────────────────────────────────────┘
                     ↓
              PyPI 发布
         (isage-* packages)
                     ↓
┌──────────────────────────────────────────────┐
│ sage-tutorials Repository                    │
│ (intellistream/sage-tutorials)               │
├──────────────────────────────────────────────┤
│ • Tutorials organized by layer               │
│ • Depends on isage-* packages from PyPI      │
│ • Learning materials only                    │
└──────────────────────────────────────────────┘
```

## Contributing

### Adding New Tutorials

1. **Choose correct layer** - Match tutorial to architecture layer
2. **Follow naming conventions** - `hello_*.py`, `*_demo.py`, `*_example.py`
3. **Add documentation** - Docstrings + comments + README updates
4. **Test thoroughly** - Ensure tutorial runs with clean SAGE install
5. **No dependencies on internal code** - Only use public SAGE APIs

### Code Style

Follow SAGE project standards:
- Ruff formatting (line length 100)
- Type hints where helpful
- Clear variable names
- Docstrings for functions/classes

## Resources

- **SAGE Main Repo**: https://github.com/intellistream/SAGE
- **SAGE Documentation**: https://sage.intellistream.com
- **PyPI Packages**: https://pypi.org/search/?q=isage
- **sage-examples**: https://github.com/intellistream/sage-examples
- **Issue Tracker**: https://github.com/intellistream/sage-tutorials/issues

## Final Reminder for Copilot

**Trust these instructions** - search only if incomplete or deep SAGE knowledge needed.

**Remember**:
1. Tutorials depend on SAGE being installed
2. Follow fail-fast principle (no silent fallbacks)
3. Document requirements clearly
4. Keep code simple and runnable
5. Reference existing tutorials for patterns

**When uncertain**: Read layer READMEs and existing examples first.
