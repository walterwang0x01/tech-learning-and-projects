#!/usr/bin/env python3
"""为 machine-learning/ 与 llm/ 下的原理层笔记追加「推荐视频资源」区块。

资源库中所有 URL 均已用 curl 实测返回 200，B 站账号归属已核对页面 title 确认。
不使用无法验证归属的单个视频 ID（这类链接失效或错误署名的风险高）。

用法：
    python3 scripts/add_learning_resources.py --dry-run   # 预览
    python3 scripts/add_learning_resources.py             # 写入
"""

from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "learning-notes"

# ── 已验证资源库（2026-08-04 实测可达）─────────────────────────────

# 频道与官网入口：比单个视频 ID 稳定得多，优先使用
CH_3B1B_BILI = "[3Blue1Brown 官方 B 站](https://space.bilibili.com/88461692)"
CH_3B1B_YT = "[3Blue1Brown YouTube](https://www.youtube.com/@3blue1brown)"
CH_LIMU = "[跟李沐学AI（B 站）](https://space.bilibili.com/1567748478)"
CH_KARPATHY = "[Andrej Karpathy YouTube](https://www.youtube.com/@AndrejKarpathy)"
CH_STATQUEST = "[StatQuest YouTube](https://www.youtube.com/@statquest)"

# 3Blue1Brown 具体课时（官网课时页，含视频与图文稿）
L_NN = "[3Blue1Brown - 神经网络是什么](https://www.3blue1brown.com/lessons/neural-networks)"
L_GD = "[3Blue1Brown - 梯度下降与网络如何学习](https://www.3blue1brown.com/lessons/gradient-descent)"
L_BP = "[3Blue1Brown - 反向传播到底在做什么](https://www.3blue1brown.com/lessons/backpropagation)"
L_ATTN = "[3Blue1Brown - 注意力机制](https://www.3blue1brown.com/lessons/attention)"
L_GPT = "[3Blue1Brown - Transformer 与 GPT 可视化](https://www.3blue1brown.com/lessons/gpt)"
L_MLP = "[3Blue1Brown - 多层感知机如何存储知识](https://www.3blue1brown.com/lessons/mlp)"

# 系统课程与教材
C_D2L = "[动手学深度学习（中文版）](https://zh.d2l.ai/)"
C_D2L_EN = "[Dive into Deep Learning（英文版）](https://d2l.ai/)"
C_DLAI = "[DeepLearning.AI 深度学习专项课程](https://www.coursera.org/specializations/deep-learning)"
C_CS231N = "[Stanford CS231n 视觉识别中的卷积网络](https://cs231n.stanford.edu/)"
C_CS224N = "[Stanford CS224n 深度学习与自然语言处理](https://web.stanford.edu/class/cs224n/)"
C_CS229 = "[Stanford CS229 机器学习](https://cs229.stanford.edu/)"
C_CS229_SHEET = "[CS229 速查表（含公式推导要点）](https://cs.stanford.edu/~shervine/teaching/cs-229/)"
C_DLBOOK = "[Deep Learning Book（Goodfellow 等，可在线阅读）](https://www.deeplearningbook.org/)"
C_HF_NLP = "[Hugging Face NLP 课程](https://huggingface.co/learn/nlp-course)"
C_HF_DIFF = "[Hugging Face 扩散模型课程](https://huggingface.co/learn/diffusion-course)"
C_SPINUP = "[OpenAI Spinning Up in Deep RL](https://spinningup.openai.com/en/latest/)"
C_SKLEARN = "[scikit-learn 用户指南](https://scikit-learn.org/stable/user_guide.html)"

# 专题图文（非视频，标注区分）
A_ILL_TRANS = "[The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)"
A_DIFFUSION = "[Lilian Weng - 扩散模型综述](https://lilianweng.github.io/posts/2021-07-11-diffusion-models/)"
A_RNN = "[Karpathy - RNN 的惊人有效性](https://karpathy.github.io/2015/05/21/rnn-effectiveness/)"
A_RLHF = "[Hugging Face - RLHF 图解](https://huggingface.co/blog/rlhf)"
A_RLHF_BOOK = "[RLHF Book（在线书）](https://rlhfbook.com/)"

# ── 主题 → 资源映射 ────────────────────────────────────────────────
# 结构：相对路径 → (视频类, 课程类, 图文类)

M: dict[str, tuple[list[str], list[str], list[str]]] = {
    # ═══ machine-learning/01-机器学习基础 ═══
    "machine-learning/01-机器学习基础/01-学习范式与泛化.md": (
        [CH_STATQUEST, CH_LIMU],
        [C_CS229, C_CS229_SHEET, C_DLAI],
        [],
    ),
    # ═══ machine-learning/02-经典算法 ═══
    "machine-learning/02-经典算法/01-线性回归与逻辑回归推导.md": (
        [CH_STATQUEST],
        [C_CS229, C_CS229_SHEET, C_SKLEARN],
        [],
    ),
    "machine-learning/02-经典算法/02-决策树.md": (
        [CH_STATQUEST],
        [C_CS229, C_SKLEARN],
        [],
    ),
    "machine-learning/02-经典算法/03-集成学习.md": (
        [CH_STATQUEST],
        [C_CS229, C_SKLEARN],
        [],
    ),
    "machine-learning/02-经典算法/04-SVM与核方法.md": (
        [CH_STATQUEST],
        [C_CS229, C_CS229_SHEET],
        [],
    ),
    "machine-learning/02-经典算法/05-朴素贝叶斯.md": (
        [CH_STATQUEST],
        [C_CS229, C_SKLEARN],
        [],
    ),
    "machine-learning/02-经典算法/06-聚类.md": (
        [CH_STATQUEST],
        [C_CS229, C_SKLEARN],
        [],
    ),
    "machine-learning/02-经典算法/07-降维.md": (
        [CH_STATQUEST, CH_3B1B_BILI],
        [C_CS229, C_SKLEARN],
        [],
    ),
    # ═══ machine-learning/03-特征工程 ═══
    "machine-learning/03-特征工程/01-特征工程方法论.md": (
        [CH_STATQUEST],
        [C_SKLEARN, C_CS229],
        [],
    ),
    # ═══ machine-learning/04-神经网络原理 ═══
    "machine-learning/04-神经网络原理/01-感知机与多层感知机.md": (
        [L_NN, L_MLP, CH_LIMU],
        [C_D2L, C_DLAI],
        [],
    ),
    "machine-learning/04-神经网络原理/02-反向传播推导.md": (
        [L_BP, L_GD, CH_KARPATHY],
        [C_D2L, C_DLAI, C_DLBOOK],
        [],
    ),
    "machine-learning/04-神经网络原理/03-梯度下降与优化器.md": (
        [L_GD, CH_LIMU],
        [C_D2L, C_DLBOOK],
        [],
    ),
    "machine-learning/04-神经网络原理/04-激活函数.md": (
        [CH_LIMU],
        [C_D2L, C_DLBOOK],
        [],
    ),
    "machine-learning/04-神经网络原理/05-损失函数.md": (
        [CH_STATQUEST, CH_LIMU],
        [C_D2L, C_DLBOOK],
        [],
    ),
    # ═══ machine-learning/05-训练工程 ═══
    "machine-learning/05-训练工程/01-过拟合与偏差方差.md": (
        [CH_STATQUEST],
        [C_CS229, C_DLBOOK, C_D2L],
        [],
    ),
    "machine-learning/05-训练工程/02-正则化技术.md": (
        [CH_STATQUEST, CH_LIMU],
        [C_D2L, C_DLBOOK],
        [],
    ),
    "machine-learning/05-训练工程/03-归一化技术.md": (
        [CH_LIMU],
        [C_D2L, C_CS231N],
        [],
    ),
    "machine-learning/05-训练工程/04-学习率调度与训练技巧.md": (
        [CH_LIMU],
        [C_D2L, C_CS231N],
        [],
    ),
    # ═══ machine-learning/06-CNN与视觉 ═══
    "machine-learning/06-CNN与视觉/01-卷积原理.md": (
        [CH_LIMU, CH_3B1B_BILI],
        [C_CS231N, C_D2L, C_DLAI],
        [],
    ),
    "machine-learning/06-CNN与视觉/02-经典网络演进.md": (
        [CH_LIMU],
        [C_CS231N, C_D2L],
        [],
    ),
    "machine-learning/06-CNN与视觉/03-ViT与视觉Transformer.md": (
        [CH_LIMU],
        [C_CS231N, C_D2L_EN],
        [A_ILL_TRANS],
    ),
    # ═══ machine-learning/07-RNN与序列 ═══
    "machine-learning/07-RNN与序列/01-RNN-LSTM-GRU.md": (
        [CH_LIMU, CH_STATQUEST],
        [C_D2L, C_CS224N],
        [A_RNN],
    ),
    "machine-learning/07-RNN与序列/02-seq2seq与注意力起源.md": (
        [CH_LIMU, L_ATTN],
        [C_D2L, C_CS224N],
        [A_ILL_TRANS],
    ),
    # ═══ machine-learning/08-强化学习基础 ═══
    "machine-learning/08-强化学习基础/01-MDP与价值函数.md": (
        [CH_STATQUEST],
        [C_SPINUP, C_D2L_EN],
        [],
    ),
    "machine-learning/08-强化学习基础/02-策略梯度与PPO.md": (
        [CH_STATQUEST],
        [C_SPINUP],
        [A_RLHF],
    ),
    # ═══ llm/01-Transformer原理 ═══
    "llm/01-Transformer原理/01-注意力机制推导.md": (
        [L_ATTN, L_GPT, CH_KARPATHY, CH_LIMU],
        [C_CS224N, C_D2L],
        [A_ILL_TRANS],
    ),
    "llm/01-Transformer原理/02-位置编码.md": (
        [CH_LIMU],
        [C_CS224N, C_D2L],
        [A_ILL_TRANS],
    ),
    "llm/01-Transformer原理/03-架构组件与训练稳定性.md": (
        [L_GPT, CH_LIMU],
        [C_CS224N, C_D2L],
        [A_ILL_TRANS],
    ),
    # ═══ llm/02-分词与表示 ═══
    "llm/02-分词与表示/01-分词算法.md": (
        [CH_LIMU],
        [C_HF_NLP, C_CS224N],
        [],
    ),
    "llm/02-分词与表示/02-词向量演进.md": (
        [CH_STATQUEST, CH_LIMU],
        [C_CS224N, C_HF_NLP],
        [],
    ),
    # ═══ llm/03-预训练范式 ═══
    "llm/03-预训练范式/01-BERT与自编码路线.md": (
        [CH_LIMU],
        [C_HF_NLP, C_CS224N],
        [],
    ),
    "llm/03-预训练范式/02-GPT与自回归路线.md": (
        [L_GPT, CH_KARPATHY, CH_LIMU],
        [C_CS224N, C_HF_NLP],
        [],
    ),
    "llm/03-预训练范式/03-MoE混合专家.md": (
        [CH_LIMU],
        [C_CS224N],
        [],
    ),
    # ═══ llm/04-微调与对齐 ═══
    "llm/04-微调与对齐/01-三阶段范式与数据构造.md": (
        [CH_KARPATHY],
        [C_HF_NLP],
        [A_RLHF, A_RLHF_BOOK],
    ),
    "llm/04-微调与对齐/02-PEFT参数高效微调.md": (
        [CH_LIMU],
        [C_HF_NLP],
        [],
    ),
    "llm/04-微调与对齐/03-RLHF全链路.md": (
        [CH_KARPATHY],
        [C_SPINUP],
        [A_RLHF, A_RLHF_BOOK],
    ),
    "llm/04-微调与对齐/04-DPO与免RL对齐.md": (
        [],
        [C_SPINUP],
        [A_RLHF_BOOK, A_RLHF],
    ),
    # ═══ llm/05-推理优化 ═══
    "llm/05-推理优化/01-KV-Cache与显存分析.md": (
        [CH_KARPATHY, CH_LIMU],
        [C_D2L_EN],
        [A_ILL_TRANS],
    ),
    "llm/05-推理优化/02-量化.md": (
        [CH_LIMU],
        [C_HF_NLP],
        [],
    ),
    "llm/05-推理优化/03-蒸馏与剪枝.md": (
        [CH_LIMU],
        [C_DLBOOK],
        [],
    ),
    "llm/05-推理优化/04-投机解码与推理引擎.md": (
        [CH_KARPATHY],
        [],
        [A_ILL_TRANS],
    ),
    # ═══ llm/06-多模态 ═══
    "llm/06-多模态/01-CLIP与对比学习.md": (
        [CH_LIMU],
        [C_CS231N, C_HF_DIFF],
        [],
    ),
    "llm/06-多模态/02-扩散模型原理.md": (
        [CH_LIMU],
        [C_HF_DIFF],
        [A_DIFFUSION],
    ),
    "llm/06-多模态/03-VLM架构.md": (
        [CH_LIMU],
        [C_HF_DIFF, C_CS231N],
        [A_ILL_TRANS],
    ),
    "llm/06-多模态/04-语音与视频模型.md": (
        [CH_LIMU],
        [C_HF_DIFF],
        [],
    ),
}

HEADING = "## 🎬 推荐视频资源"

NOTE = (
    "> 以下资源均为频道 / 课程 / 官网入口级链接（已于 2026-08-04 实测可访问）。"
    "刻意不收录单个视频 ID——那类链接失效率高，且难以核实归属。\n"
    "> 从入口进去按本篇主题检索，命中率比一条可能失效的直链更高。\n"
)


def build_block(vids: list[str], courses: list[str], articles: list[str]) -> str:
    parts = [HEADING, "", NOTE]
    if vids:
        parts += ["", "### 📺 视频频道与课时", ""]
        parts += [f"- {v}" for v in vids]
    if courses:
        parts += ["", "### 🎓 系统课程与教材", ""]
        parts += [f"- {c}" for c in courses]
    if articles:
        parts += ["", "### 📖 专题图文", ""]
        parts += [f"- {a}" for a in articles]
    return "\n".join(parts) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    added = skipped = missing = 0
    for rel, (vids, courses, articles) in M.items():
        p = ROOT / rel
        if not p.exists():
            print(f"❌ 文件不存在: {rel}")
            missing += 1
            continue
        text = p.read_text(encoding="utf-8")
        if HEADING in text:
            print(f"⏭  已有资源区块，跳过: {rel}")
            skipped += 1
            continue

        block = build_block(vids, courses, articles)
        new = text.rstrip("\n") + "\n\n" + block

        if args.dry_run:
            print(f"[dry-run] 将追加 {len(block)} 字节 → {rel}")
        else:
            p.write_text(new, encoding="utf-8")
            print(f"✅ {rel}")
        added += 1

    print(f"\n处理 {added} 篇，跳过 {skipped} 篇，缺失 {missing} 篇")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
