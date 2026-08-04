# CLIP 与对比学习

> Author: Walter Wang

> **读完你能回答的 3 个问题**
>
> 1. InfoNCE 损失里的温度系数在做什么，调大调小分别有什么后果？
> 2. 为什么对比学习的效果高度依赖 batch size？
> 3. 模态鸿沟（modality gap）是什么现象，SigLIP 相比 CLIP 改进了什么？

## 1. 对比学习的核心思想

对比学习（contrastive learning）解决的是"没有显式标签，如何学到有意义的表示"这个问题。核心思路很朴素：**构造正样本对（positive pair）和负样本对（negative pair），训练模型把正样本对的表示拉近，把负样本对的表示推远**。

```
表示空间中：
  正样本对 (anchor, positive)  → 距离应该小
  负样本对 (anchor, negative)  → 距离应该大

优化目标：anchor 与 positive 的相似度 >> anchor 与所有 negative 的相似度
```

在图文多模态场景里，正样本对是"同一张图和它配的文本描述"，负样本是"图和其他不相关的文本"。模型不需要人工标注类别，只需要大量图文对（互联网上天然存在），就能学到图像和文本在语义上是否匹配——这是自监督学习的一种形式。

对比学习的关键不在于正样本怎么拉近，而在于**负样本怎么选、选多少、怎么参与损失计算**，这直接决定了表示学到的区分度。

## 2. InfoNCE 损失推导

InfoNCE（Noise Contrastive Estimation 的信息论版本）是对比学习最常用的损失形式。给定 anchor 表示 `q`、正样本表示 `k+`，以及 `N-1` 个负样本表示 `{k1, ..., k(N-1)}`，损失定义为：

```
L = -log( exp(q·k+ / τ) / Σ_i exp(q·k_i / τ) )
```

求和 `Σ_i` 遍历正样本和全部负样本，`τ` 是温度系数（temperature），`q·k` 通常是归一化向量的余弦相似度。

**本质是 softmax 分类问题**：把"从 N 个候选里挑出正样本"看作 N 类分类，`q·k_i / τ` 是每个候选的 logit，交叉熵损失要求正样本对应的 logit 在 softmax 后概率最大。

**温度系数 τ 的作用**：`τ` 缩放 logit 尺度，直接影响 softmax 分布的锐利程度。

```
τ 越小 → 差异被放大 → softmax 更尖锐 → 被迫更强烈区分正负样本
        → 梯度更集中在难负样本（hard negative）上，但过小会训练不稳定
τ 越大 → 差异被压平 → softmax 更平滑 → 所有负样本贡献的梯度更均匀
        → 训练更稳定，但区分信号变弱
```

直觉上，`τ` 控制模型对困难负样本的关注度：温度低时，相似度偏高的负样本也必须被明确压低，否则损失很大；温度高时压力被摊平，学习信号变弱。CLIP 实际训练把 `τ` 设为可学习参数（`log(1/τ)` 参数化），让模型自己找到合适的锐利程度。

## 3. CLIP 的双塔结构与图文对齐

CLIP（Contrastive Language-Image Pre-training）用两个独立编码器分别处理图像和文本，称为双塔结构（dual-tower / dual-encoder）：

```
图像编码器（Vision Encoder，如 ViT 或 CNN）：图像 → 图像特征向量 v ∈ R^d
文本编码器（Text Encoder，如 Transformer）：文本 → 文本特征向量 t ∈ R^d

投影层：两个编码器输出维度可能不同，各接一个线性投影层映射到同一维度 d
归一化：v、t 都做 L2 归一化，之后点积就是余弦相似度
```

两个编码器**没有中间交互**，各自独立编码成向量，只在最后计算相似度时才发生联系。这与融合式结构（图文特征在同一 Transformer 里做 cross-attention）的本质区别是：双塔结构推理时可把图像库/文本库提前编码好存起来，检索时只需算点积，成本远低于每次都跑一遍融合模型。

**训练时的对比目标**：一个 batch 里有 `N` 个图文对，构造 `N×N` 相似度矩阵，对角线是正样本对，非对角线全是负样本。损失是**双向 InfoNCE**——图到文本、文本到图像方向各算一次交叉熵再平均：

```
相似度矩阵 S[i][j] = v_i · t_j / τ   (i, j = 1..N)

图→文本损失：对每行 i，正确答案是 j=i，做 N 类分类交叉熵
文本→图损失：对每列 j，正确答案是 i=j，做 N 类分类交叉熵

L = (L_image→text + L_text→image) / 2
```

双向损失保证图像编码器和文本编码器被同等力度地推向对齐，而非只优化单一方向。

## 4. Batch 内负样本：为何 batch size 至关重要

上面的相似度矩阵里，**同一 batch 内除对角线外的所有元素天然就是负样本**，不需要额外采样或标注——负样本"免费"来自同一批数据。

但这也决定了 **batch size 直接等于负样本数量**：batch size 为 `N`，每个正样本对就有 `N-1` 个负样本参与损失计算。负样本不足会带来明显问题：

```
batch 太小（N=32）：每个 anchor 只面对 31 个负样本，任务过于简单，
  区分"图和文本不匹配"容易，学不到"图和相似但错误文本"间的细粒度差异
batch 足够大（数千至数万）：负样本池够大，出现语义相近但不匹配的
  "难负样本"概率更高，模型被迫学习更精细的语义区分
```

这也解释了 CLIP 类模型原始训练严重依赖大 batch size（往往需跨多机分布式训练，把不同设备上的负样本汇聚参与损失计算），是对比学习相对其他自监督方法在工程成本上的显著代价。

## 5. 零样本分类为何能工作

CLIP 训练完成后不需要针对下游任务微调即可做零样本分类（zero-shot classification），做法是把类别名转换成文本 prompt：

```
候选类别："cat", "dog", "car" ...
构造文本："a photo of a cat" / "a photo of a dog" / "a photo of a car" ...
对每个类别文本跑文本编码器得 t_1, t_2, t_3, ...；对图像跑图像编码器得 v
计算 v 与每个 t_i 的相似度，取最大值对应的类别作为预测结果
```

**能work的根本原因**：预训练阶段模型已在海量图文对上学会图像语义和文本语义共享同一表示空间，相似度高低直接对应语义匹配程度。分类任务被重新表述成图文匹配任务，正是预训练时优化的目标——没有引入新学习目标，只是把闭集分类转化成模型本来就会做的事。这与语言模型用 next-token 预测做续写、翻译，思路相通（参考 [../03-预训练范式/02-GPT与自回归路线.md](../03-预训练范式/02-GPT与自回归路线.md)）。

## 6. 模态鸿沟（modality gap）现象

直观预期是：训练好的 CLIP 表示空间里匹配的图文对应几乎重合。但实际观察到反直觉现象——**图像向量和文本向量在表示空间中占据两个可分离、几乎不重叠的区域**，即便匹配的图文对，向量距离也明显大于同模态内部样本间的距离。

这被称为模态鸿沟（modality gap）。较能解释这一现象的因素包括：不同模态编码器的架构差异、初始化差异，以及**对比损失本身不要求匹配对向量重合，只要求正样本相似度相对负样本足够高**——鸿沟不违反训练目标，模型只需保持排序正确。

> ⚠️ 待确认：modality gap 具体成因（架构、初始化、损失函数各自贡献比例）学界仍有讨论，这里只呈现现象和主流解释方向。

这提示：CLIP 类模型相似度分数是相对的，跨模态绝对距离不能直接当作语义接近程度的可靠度量。

## 7. SigLIP：Sigmoid 损失的改进思路

SigLIP 对 CLIP 训练目标做了改进，核心变化是**把 softmax 形式的 InfoNCE 换成逐对独立的 sigmoid 二分类损失**：

```
CLIP（softmax，需要归一化整行/整列）：
  L = -log( exp(sim(i,i)/τ) / Σ_j exp(sim(i,j)/τ) )

SigLIP（sigmoid，每个 pair 独立判断"是否匹配"）：
  L = Σ_{i,j} [ y_ij·log σ(sim(i,j)) + (1-y_ij)·log(1-σ(sim(i,j))) ]
  其中 y_ij = 1 若 i=j（正样本对），否则 0
```

**关键区别**：softmax 版本要求整行/整列归一化，损失计算天然全局，对 batch size、跨设备负样本同步更敏感；sigmoid 版本把每对当作独立二分类，不需跨样本归一化，更容易并行化，对超大 batch size 依赖更低。代价是失去 softmax 天然的排序约束，需额外机制平衡类别不均衡（每行仅 1 个正样本，`N-1` 个负样本）。

## 8. 单模态对比学习：SimCLR 与 MoCo

对比学习框架并非多模态专属，最早大规模验证效果的是图像自监督表示学习。

**SimCLR** 对同一张图做两次随机数据增强（裁剪、颜色扰动），两个视图互为正样本，batch 内其他图像的视图互为负样本，直接套用 InfoNCE 训练图像编码器，不需要标签。

**MoCo**（Momentum Contrast）解决 SimCLR 依赖超大 batch size 的显存瓶颈：维护一个动量更新的编码器和一个队列（queue）作为负样本库——负样本从跨多个 batch 累积的队列取出，数量可远大于单次 batch size 而不显著增加显存压力；动量编码器（滑动平均更新）保证队列里旧的负样本不会与当前编码器脱节太严重。

CLIP 可看作把这套单模态框架搬到跨模态场景，核心机制一脉相承。

## 9. 代码：InfoNCE 损失中温度与负样本数量的效应

用 numpy 实现 InfoNCE 损失，验证温度系数和负样本数量分别如何影响损失值和分类置信度。

```python
import numpy as np

rng = np.random.default_rng(0)


def make_embeddings(n, dim, align_strength=3.0):
    """构造 n 对模拟图文嵌入：文本向量=图像向量+噪声（模拟真实对齐），
    各自 L2 归一化，模拟 CLIP 中点积即余弦相似度的设定"""
    img = rng.normal(0, 1.0, (n, dim))
    txt = img * align_strength + rng.normal(0, 1.0, (n, dim))
    img = img / np.linalg.norm(img, axis=1, keepdims=True)
    txt = txt / np.linalg.norm(txt, axis=1, keepdims=True)
    return img, txt


def info_nce_loss(img, txt, tau):
    """双向 InfoNCE：图→文本、文本→图各算一次交叉熵后取平均"""
    sim = (img @ txt.T) / tau  # N x N 相似度矩阵，对角线是正样本

    # 图→文本方向：对每行做 softmax 交叉熵，正确类别是对角线
    row_max = np.max(sim, axis=1, keepdims=True)
    log_softmax_row = sim - row_max - np.log(np.sum(np.exp(sim - row_max), axis=1, keepdims=True))
    loss_i2t = -np.mean(np.diag(log_softmax_row))

    # 文本→图方向：对每列做 softmax 交叉熵
    col_max = np.max(sim, axis=0, keepdims=True)
    log_softmax_col = sim - col_max - np.log(np.sum(np.exp(sim - col_max), axis=0, keepdims=True))
    loss_t2i = -np.mean(np.diag(log_softmax_col))

    # 正样本（对角线）在 softmax 后的平均概率，衡量模型把正样本排第一的把握
    prob_pos = np.mean(np.diag(np.exp(log_softmax_row)))
    return (loss_i2t + loss_t2i) / 2, prob_pos


dim = 32
img, txt = make_embeddings(n=64, dim=dim)

print("实验1：固定负样本数(batch=64)，观察温度系数 τ 的影响")
for tau in [0.5, 0.1, 0.05, 0.01]:
    loss, prob_pos = info_nce_loss(img, txt, tau)
    print(f"  τ={tau:<5} loss={loss:.4f}  正样本平均置信度={prob_pos:.4f}")

print("\n实验2：固定温度 τ=0.07，观察 batch size（负样本数量）的影响")
for n in [4, 16, 64, 256]:
    img_n, txt_n = make_embeddings(n=n, dim=dim)
    loss, prob_pos = info_nce_loss(img_n, txt_n, tau=0.07)
    print(f"  batch={n:<4} 负样本数={n-1:<4} loss={loss:.4f}  正样本平均置信度={prob_pos:.4f}")
```

实测输出（numpy 2.4.4）：

```
实验1：固定负样本数(batch=64)，观察温度系数 τ 的影响
  τ=0.5   loss=2.3992  正样本平均置信度=0.0909
  τ=0.1   loss=0.0200  正样本平均置信度=0.9802
  τ=0.05  loss=0.0001  正样本平均置信度=0.9999
  τ=0.01  loss=-0.0000  正样本平均置信度=1.0000

实验2：固定温度 τ=0.07，观察 batch size（负样本数量）的影响
  batch=4    负样本数=3    loss=0.0001  正样本平均置信度=0.9999
  batch=16   负样本数=15   loss=0.0004  正样本平均置信度=0.9996
  batch=64   负样本数=63   loss=0.0012  正样本平均置信度=0.9988
  batch=256  负样本数=255  loss=0.0067  正样本平均置信度=0.9934
```

实验1显示 τ 越大，相似度差异被压平越严重，模型几乎分不清正负样本（τ=0.5 时置信度仅 0.09，接近随机猜的 1/64）；τ 越小差异被放大，置信度迅速逼近 1。实验2里对齐强度固定，模型区分能力不受 batch size 影响（数据是人为构造的强对齐信号），但 loss 随负样本数增多缓慢上升——候选池变大，选出正确答案本身更难，真实训练中负样本增多会提供更多难负样本，逼迫编码器学到更精细的区分能力。

## 10. 小结

| 主题 | 核心结论 |
| --- | --- |
| 对比学习核心 | 拉近正样本对、推远负样本对，不需人工标签 |
| InfoNCE | 挑出正样本当 softmax 分类，温度系数控制区分锐利程度 |
| CLIP 结构 | 双塔独立编码图文，仅在相似度计算层交互，支持离线编码检索 |
| Batch size | 决定负样本数量，过小学不到精细区分，是工程瓶颈 |
| 零样本分类 | 分类被重述为图文匹配，复用预训练目标本身 |
| 模态鸿沟 | 图文向量占据可分离区域，损失只要求排序正确，不强制重合 |
| SigLIP | sigmoid 逐对损失替代 softmax，降低对超大 batch 依赖 |
| 单模态先驱 | SimCLR 用数据增强构造正样本，MoCo 用队列扩大负样本规模 |

## 11. 延伸阅读

- 注意力机制与 Transformer 基础 → [../01-Transformer原理/01-注意力机制推导.md](../01-Transformer原理/01-注意力机制推导.md)
- 自编码式预训练与表示学习 → [../03-预训练范式/01-BERT与自编码路线.md](../03-预训练范式/01-BERT与自编码路线.md)
- GPT 自回归范式与零样本泛化 → [../03-预训练范式/02-GPT与自回归路线.md](../03-预训练范式/02-GPT与自回归路线.md)
- 损失函数设计的通用原理 → [../../machine-learning/04-神经网络原理/05-损失函数.md](../../machine-learning/04-神经网络原理/05-损失函数.md)
