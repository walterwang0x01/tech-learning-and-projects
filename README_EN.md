# AI Engineering Knowledge Base

> [🇨🇳 中文](./README.md) | 🇬🇧 English

**571 original technical notes + 198 self-check questions + 6 runnable projects**, covering the full path from backpropagation derivation to production-grade Agent systems.

### 👉 [Read online (interactive) →](https://walterwang0x01.github.io/portfolio/notes/)

Not just a pile of markdown. The site offers three modes:

| | What it does |
| --- | --- |
| 🗺️ **Learning Path** | 5 stages ordered by dependency, each labeled with note count, estimated time, and **why you should learn it first**. Tracks reading progress |
| 📖 **Read** | Tree navigation + full-text rendering, mark as read |
| ✍️ **Self-check** | 198 questions. Answer first, then reveal the source. **Can't answer = signal to re-read** |

### 🔬 [Interactive Visualizations →](https://walterwang0x01.github.io/portfolio/demos/)

Turn formulas into things you can drag. Pure frontend, no API calls:

- **Attention heatmap** — type a sentence, see the `softmax(QKᵀ/√d)` matrix. Toggle causal mask to compare GPT vs BERT, adjust temperature to see attention concentrate/spread
- **Backpropagation** — step through the chain rule layer by layer. Set x negative to reproduce "dying ReLU" (gradient cut off)
- **KV Cache calculator** — 5 real model presets, live comparison of MHA / GQA / MQA, plus "how many concurrent requests fit on one GPU"
- **TIES model merging** — visualize sign election, see how naive averaging cancels +0.8 and -0.7 into +0.05

[![Interactive Site](https://img.shields.io/badge/Read-Interactive_Site-blue)](https://walterwang0x01.github.io/portfolio/notes/)
[![Visualizations](https://img.shields.io/badge/Visualizations-4_demos-red)](https://walterwang0x01.github.io/portfolio/demos/)
[![AI Notes](https://img.shields.io/badge/AI_Engineering-191_notes-orange)](./learning-notes/00-ai/)
[![All Notes](https://img.shields.io/badge/All_Notes-571-green)](./learning-notes/)
[![Quiz](https://img.shields.io/badge/Self--check-198_questions-purple)](https://walterwang0x01.github.io/portfolio/notes/#quiz)

---

## What makes this different

**1. Both fundamentals and applications — not just half**

Most AI learning resources either only cover "how to call APIs to build Agents" or only "Transformer math derivations". This covers both, clearly separated:

```
01-machine-learning  backprop / optimizers / regularization / CNN / RNN / RL      34 notes
02-llm               attention derivation / tokenization / MoE / RLHF / quant     23 notes
04-ai-agent          frameworks / protocols / RAG / tools / memory / security    128 notes
```

Understanding "why fine-tuning didn't work" requires the first two layers. Understanding "why the Agent went rogue" requires the third.

**2. Three questions at the top of every note**

Not a summary — a **verification standard**. Example from [Model Merging](./learning-notes/00-ai/02-llm/04-微调与对齐/05-模型合并.md):

> 1. Why can two independently fine-tuned models be added/subtracted in parameter space, and what does this operation assume?
> 2. What problems do TIES and DARE each solve in naive weight averaging, and how do their approaches differ?
> 3. Under what conditions does model merging fail, and how do you assess feasibility beforehand?

Can't answer? Go back and read that section. These 198 questions are [interactive on the site](https://walterwang0x01.github.io/portfolio/notes/#quiz).

**3. Runnable code with actually-measured output**

Not pseudocode. Every NumPy implementation was executed, and the pasted output is the real result. During writing, there were multiple cases of "expected output ≠ actual output" — e.g. the model-collapse note initially used an unbiased variance estimator and couldn't reproduce the decay at all; switching to MLE (biased) revealed sigma dropping from 0.95 to 0.35. **Those corrections are kept in the notes, because the debugging path itself carries information.**

**4. Explicit "when NOT to use this"**

Technology selection notes don't just list advantages. [Model Merging](./learning-notes/00-ai/02-llm/04-微调与对齐/05-模型合并.md) §9 lists six failure scenarios with detection methods; [From for-loops to autonomous systems](./learning-notes/00-ai/04-ai-agent/16-Harness%20Engineering/10-从for循环到自治系统.md) has a dedicated section on "when you should not go autonomous".

---

## Content Map

### 🧠 AI Engineering (191 notes) — [Full navigation](./learning-notes/00-ai/README.md)

Numbered by learning dependency, not alphabetically:

| Stage | Content | Notes |
| --- | --- | --- |
| [00-Getting Started](./learning-notes/00-ai/00-入门准备/) | AI landscape, dev environment & compute, learning path & pitfalls, how to read papers | 4 |
| [01-machine-learning](./learning-notes/00-ai/01-machine-learning/README.md) | Math essentials → classic algorithms → feature engineering → **backprop derivation** → training engineering → CNN/RNN → RL | 34 |
| [02-llm](./learning-notes/00-ai/02-llm/README.md) | **Attention derivation** → tokenization → BERT/GPT/MoE → SFT/LoRA/RLHF/DPO → KV Cache/quantization/speculative decoding → CLIP/diffusion/VLM | 23 |
| [03-Hands-on](./learning-notes/00-ai/03-实战项目/) | PyTorch training, end-to-end project | 2 |
| [04-ai-agent](./learning-notes/00-ai/04-ai-agent/README.md) | 25 subdirectories | 128 |

**Highlights in 04-ai-agent**: Claude Code architecture deep-dive (44KB), Agent identity & permissions (60KB), Agent testing engineering (76KB), MCP supply-chain attacks, Prompt injection & memory poisoning, Harness Engineering (10 notes incl. Context Offloading / Version Drifting / Company Brain).

### 💻 Other Stacks (380 notes)

| Domain | Content | Notes |
| --- | --- | --- |
| [01-languages](./learning-notes/01-languages/) | Python / Java / Go / Rust | 181 |
| [02-frontend](./learning-notes/02-frontend/frontend/README.md) | React / Vue3 / TypeScript / build tooling / performance | 66 |
| [03-mobile](./learning-notes/03-mobile/) | iOS (Swift/SwiftUI), Android (Kotlin/Compose) | 90 |
| [04-backend-infra](./learning-notes/04-backend-infra/) | Architecture / databases / data engineering / observability / platform engineering / security | 43 |

### 📰 Daily Tech Briefings (304 issues)

[AI Agent / China Tech / Global Tech](./learning-notes/_briefings/) — automated pipeline (RSS + HN API + web search, with dedup, scoring, circuit-breaker self-healing).

**[Read briefings online →](https://walterwang0x01.github.io/portfolio/briefing/)**

### 📖 Reading Collection

[reading/](./reading/) — third-party technical books + my reading notes (separate copyright declarations, see each subdirectory's COPYRIGHT.md).

**[Read online →](https://walterwang0x01.github.io/portfolio/reading/)**

---

## 🎯 Projects

### LangGraph + MCP Agent

Production-grade Agent skeleton: intent routing → RAG retrieval / tool calling / human approval → response generation.

```bash
cd projects/langgraph-mcp-agent-demo
cp env.example .env   # add your API keys
docker-compose up -d  # PostgreSQL + ChromaDB
uvicorn app.main:app --reload
```

Covers: LangGraph state graph with checkpointing, MCP Servers (file + database), ChromaDB RAG, Mem0 long-term memory, human-in-the-loop for sensitive operations.

→ [Docs](./projects/langgraph-mcp-agent-demo/)

### CrewAI Multi-Agent

Content pipeline: Researcher → Writer → Editor → SEO Optimizer, four Agents in sequence.

```bash
cd projects/crewai-multi-agent-demo
cp env.example .env
python -m app.main --topic "AI Agent trends"
```

→ [Docs](./projects/crewai-multi-agent-demo/)

### Others

- [rag-llm-agent-platform](./projects/rag-llm-agent-platform/) — RAG + tool calling platform (FastAPI + pgvector)
- [spring-boot-microservice-demo](./projects/spring-boot-microservice-demo/) — Spring Cloud microservices (user/order + Kafka)
- [x402-demo](./projects/x402-demo/) / [x402-python-demo](./projects/x402-python-demo/) — x402 HTTP-native micropayment experiments

---

## How to use this repo

**New to AI**: Start from the [learning path](https://walterwang0x01.github.io/portfolio/notes/), follow 00 → 01 → 02 → 03 → 04. Don't skip `01-machine-learning/04-神经网络原理` — that's where judgment comes from.

**Already building Agents**: Jump to the relevant subdirectory under `04-ai-agent/`. For selection, see `04-Agent框架补充/01-Agent框架选型指南`. For pitfalls, see `15-Agent安全与治理` and `14-可观测与评估`.

**Want to test yourself**: Go straight to the [self-check page](https://walterwang0x01.github.io/portfolio/notes/#quiz). Pick a module from the 198 questions, and only read the notes for what you can't answer. More efficient than reading front to back.

---

## Maintenance

This repo isn't write-once-and-forget. It has automated maintenance:

- **Docs quality CI**: broken link checks, file header conventions, version-staleness checks ([ci-docs.yml](./.github/workflows/ci-docs.yml))
- **Internal link validation**: 841 internal links, verified zero-broken after every change
- **Briefing pipeline**: 232 unit tests in `scripts/briefing_tools/` covering classification, scoring, dedup, source circuit-breaker
- **Version markers**: content tagged `<!-- version-check -->` gets periodically re-verified

Writing conventions: 8–15KB per note, three self-check questions at the top, runnable example required for principle notes, split anything over 20KB.

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=walterwang0x01/tech-learning-and-projects&type=Date)](https://star-history.com/#walterwang0x01/tech-learning-and-projects&Date)

---

## License

**Free to read and share non-commercially**, with attribution required. Any commercial use (publishing, training courses, paid content adaptation) requires prior written permission.

Content under `reading/` is third-party; copyright belongs to the original authors — see each subdirectory's `COPYRIGHT.md`.

See [LICENSE](./LICENSE) for details.

---

<div align="center">

**If this repo helps you, a ⭐ Star is appreciated**

Author: Walter Wang

</div>
