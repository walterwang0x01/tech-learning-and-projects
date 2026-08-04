# ViT 与视觉 Transformer：把图像当作一串 token

> Author: Walter Wang

> **读完你能回答的 3 个问题**
>
> 1. ViT 怎么把一张图像转换成 Transformer 能处理的 token 序列？为什么需要额外加位置编码？
> 2. ViT 为什么比 CNN 更依赖大规模数据？这和"归纳偏置"有什么关系？
> 3. Swin Transformer 的窗口注意力解决了 ViT 的什么问题？MAE 的掩码重建又是为了解决什么问题？

## 1. 图像分块与线性投影：把图像变成 token 序列

Transformer 原本处理的是词序列（[注意力机制推导](../../llm/01-Transformer原理/01-注意力机制推导.md)），每个词是一个离散 token。ViT 要解决的第一个问题是：**图像是连续的像素网格，怎么变成一串 token？**

做法是把图像切成固定大小、不重叠的方块（patch），比如一张 `224×224` 的图切成 `16×16` 的 patch，会得到 `14×14=196` 个 patch。每个 patch 展平成一维向量（`16×16×3=768` 维），再通过一个线性投影层映射到 Transformer 的 embedding 维度：

```
patch_embed = Flatten(patch) @ W_embed

patch: 16×16×3 展平后的向量，W_embed: 可学习的投影矩阵
```

这样一张图像就变成了一个长度为 196 的 token 序列，每个 token 是一个 embedding 向量——后续处理方式跟 NLP 里的词序列完全一样，可以直接套用标准 Transformer encoder。

## 2. 位置编码在视觉上的处理

Transformer 的自注意力本身是**置换等变（permutation-equivariant）** 的——如果打乱输入序列的顺序，输出也会按同样的方式打乱，但每个位置对应的计算结果不变（第 8 节会用代码验证这一点）。也就是说，自注意力天生不知道"谁排在前面、谁排在后面"，这在 NLP 里靠位置编码解决（[位置编码](../../llm/01-Transformer原理/02-位置编码.md)），在 ViT 里同样需要。

ViT 给每个 patch token 加一个可学习的位置编码（learnable position embedding），直接与 patch embedding 相加：

```
token_i = patch_embed_i + pos_embed_i
```

和 NLP 中常见的正弦位置编码不同，ViT 更常直接用可学习的位置向量，让模型自己学出二维图像空间中 patch 之间的位置关系（比 NLP 里的一维序列位置关系更复杂，patch 之间存在上下左右的二维邻接结构）。

## 3. [CLS] token 的作用

ViT 沿用了 BERT（[BERT与自编码路线](../../llm/03-预训练范式/01-BERT与自编码路线.md)）的做法，在 patch token 序列最前面拼接一个额外的**可学习 [CLS] token**：

```
序列 = [CLS, patch_1, patch_2, ..., patch_N]
```

经过多层自注意力后，[CLS] token 的输出被当作整张图像的全局表征，接到分类头做最终预测。之所以用一个专门的 token 而不是直接对所有 patch 输出做平均池化，是因为 [CLS] token 通过自注意力可以**自适应地、有选择地**聚合所有 patch 的信息（哪些 patch 更重要由注意力权重决定），比固定的平均池化更灵活。

## 4. ViT 为何需要大数据：归纳偏置的缺失

**归纳偏置（inductive bias）** 指模型架构本身内置的、关于数据结构的先验假设。CNN 的归纳偏置很强：局部连接假设"相邻像素更相关"，权值共享假设"同一种模式在图像各处的检测方式应该一样"（卷积原理篇已展开）。这些假设与图像的真实统计特性高度吻合，所以 CNN 即使在数据量不大时也能学得不错——先验知识帮它"少走弯路"。

ViT 的自注意力机制里，每个 patch 都可以直接和任意其他 patch 交互，**没有"相邻更相关"这类先验假设**——它必须完全从数据中学习哪些 patch 之间该互相关注、什么样的空间关系是有意义的。这是一把双刃剑：数据足够多时，模型可以学到比人工设计的归纳偏置更灵活、更适配任务的模式；但数据不够时，模型没有先验知识可以依赖，容易学得不充分或过拟合。这正是 ViT 相比同等规模 CNN 更依赖大规模数据（或大规模预训练）才能发挥优势的核心原因。

## 5. CNN 与 ViT 的归纳偏置对比

| 维度 | CNN | ViT |
| --- | --- | --- |
| 局部性假设 | 强（卷积核只看局部邻域） | 弱（自注意力全局交互，无先天局部性） |
| 平移等变性 | 天生具备（权值共享） | 不天生具备（需要靠数据学出类似效果） |
| 层级化特征 | 天生具备（浅层边缘，深层语义，随网络加深感受野扩大） | 不天生具备（标准 ViT 每层都是全局注意力，无层级结构） |
| 对数据量的要求 | 较低 | 较高（小数据下容易不如 CNN） |
| 长距离依赖建模 | 需要堆很多层才能让感受野覆盖全图 | 天生具备（第一层就能看到全图任意两个 patch 的关系） |

## 6. 层级化设计：Swin Transformer 的窗口注意力

标准 ViT 的一个问题是：全局自注意力的计算量随 token 数量呈平方增长（`N` 个 token 需要计算 `N×N` 的注意力矩阵），当处理高分辨率图像（patch 数量很多）时计算量会变得很大；而且标准 ViT 每一层都是全局注意力，缺少 CNN 那种"浅层局部、深层全局"的层级化结构。

Swin Transformer 的解法是**窗口注意力（windowed attention）**：把 token 序列划分成若干个不重叠的局部窗口，自注意力只在每个窗口内部计算，把计算量从 `O(N²)` 降到 `O(N)`（窗口数量随 `N` 线性增长，每个窗口内部计算量是常数）。为了让信息能跨窗口流动，Swin 在相邻层之间**平移窗口划分位置（shifted window）**，让本来分属不同窗口的 patch 在下一层有机会被划入同一个窗口。多层堆叠后，再通过下采样（patch merging）逐步合并相邻 patch、扩大有效感受野，重新引入了 CNN 式的层级化结构。

## 7. 混合架构思路

除了纯 ViT 或纯 CNN，还有一类思路是把两者结合：**用 CNN 做前几层的特征提取（利用其归纳偏置在小数据/低层特征上的优势），再把 CNN 输出的特征图当作 patch 序列送入 Transformer 做后续的全局关系建模**。这类混合架构希望同时获得 CNN 的数据效率和 Transformer 的长距离建模能力，是 ViT 提出后的一个自然延伸方向。

## 8. 自监督预训练在视觉上的作用：MAE 的掩码重建

NLP 里的自监督预训练（如 BERT 的掩码语言建模）证明了"遮住一部分输入，让模型预测被遮住的部分"是一种有效的自监督信号来源。**MAE（Masked Autoencoder）** 把这个思路搬到视觉上：随机遮住图像中大比例的 patch（遮盖比例通常远高于 BERT 遮词的比例，因为图像 patch 之间的信息冗余度更高，少量可见 patch 也能重建大部分被遮内容），只把少数可见 patch 送入一个较重的 encoder，再用一个较轻的 decoder 从 encoder 输出加上位置信息，重建被遮住 patch 的像素值。

这个自监督任务不需要人工标注类别标签，让模型在大量无标注图像上学习通用视觉表征，之后再用少量标注数据微调到具体任务（分类、检测等）。其意义与 NLP 里"预训练+微调"的范式一致（[三阶段范式与数据构造](../../llm/04-微调与对齐/01-三阶段范式与数据构造.md)），核心都是用容易获取的自监督信号替代昂贵的人工标注。

## 9. 最小可运行实现：验证自注意力的置换等变性

```python
"""
用 numpy 演示 ViT 的图像分块(patch embedding)与位置编码相加过程，
并对比"有位置编码"和"打乱 patch 顺序后"自注意力输出的差异，
验证自注意力本身对 patch 顺序不敏感（permutation-equivariant），必须靠位置编码补充顺序信息。
"""
import numpy as np


def patchify(image, patch_size):
    """把 (H,W,C) 图像切成不重叠的 patch，展平成 (num_patches, patch_size*patch_size*C)"""
    H, W, C = image.shape
    ph = pw = patch_size
    n_h, n_w = H // ph, W // pw
    patches = image.reshape(n_h, ph, n_w, pw, C).transpose(0, 2, 1, 3, 4)
    return patches.reshape(n_h * n_w, ph * pw * C)


def softmax(x, axis=-1):
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)


def self_attention(x, Wq, Wk, Wv):
    """标准单头自注意力：softmax(QK^T/sqrt(d)) V"""
    Q, K, V = x @ Wq, x @ Wk, x @ Wv
    d = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d)
    attn = softmax(scores)
    return attn @ V


if __name__ == "__main__":
    rng = np.random.default_rng(0)

    # 构造一张 8x8x3 的小图，切成 4 个 4x4 patch
    image = rng.normal(size=(8, 8, 3))
    patch_size = 4
    patches = patchify(image, patch_size)
    print(f"图像形状: {image.shape}, patch_size={patch_size}")
    print(f"分块后: {patches.shape[0]} 个 patch，每个展平维度={patches.shape[1]}")

    # 线性投影到 embedding 维度，加上 [CLS] token 和可学习位置编码
    embed_dim = 6
    W_embed = rng.normal(0, 0.1, (patches.shape[1], embed_dim))
    patch_embed = patches @ W_embed  # (4, embed_dim)

    cls_token = rng.normal(0, 0.1, (1, embed_dim))
    tokens = np.vstack([cls_token, patch_embed])  # (5, embed_dim)，第0行是 [CLS]

    pos_embed = rng.normal(0, 0.1, tokens.shape)
    tokens_with_pos = tokens + pos_embed

    print(f"\n加入 [CLS] token 后序列长度: {tokens.shape[0]} (1 个 CLS + {patches.shape[0]} 个 patch)")

    # 自注意力权重（共享给两次实验，保证对比公平）
    Wq = rng.normal(0, 0.1, (embed_dim, embed_dim))
    Wk = rng.normal(0, 0.1, (embed_dim, embed_dim))
    Wv = rng.normal(0, 0.1, (embed_dim, embed_dim))

    out_with_pos = self_attention(tokens_with_pos, Wq, Wk, Wv)

    # 打乱 patch 顺序（保留 [CLS] 在第0位不变），只用 tokens（不加位置编码）看输出是否也跟着打乱
    perm = rng.permutation(4) + 1  # patch 索引 1~4 打乱
    perm_full = np.concatenate([[0], perm])
    tokens_shuffled = tokens[perm_full]
    out_no_pos_shuffled = self_attention(tokens_shuffled, Wq, Wk, Wv)
    out_no_pos_original = self_attention(tokens, Wq, Wk, Wv)

    # 验证：打乱后的输出，按同样的 perm 重新排列，应该与原始输出的对应行完全一致（置换等变性）
    out_no_pos_shuffled_unpermuted = np.zeros_like(out_no_pos_shuffled)
    out_no_pos_shuffled_unpermuted[perm_full] = out_no_pos_shuffled

    max_diff_no_pos = np.max(np.abs(out_no_pos_shuffled_unpermuted - out_no_pos_original))
    print(f"\n不加位置编码时，打乱 patch 顺序后再还原，与原始输出的最大差异: {max_diff_no_pos:.2e}")
    print("（应接近 0，说明自注意力对 patch 顺序是置换等变的，本身不携带位置信息）")

    print(f"\n加入位置编码后的自注意力输出（[CLS] token 行）:\n{out_with_pos[0]}")
```

实测输出（numpy 2.4.4）：

```
图像形状: (8, 8, 3), patch_size=4
分块后: 4 个 patch，每个展平维度=48

加入 [CLS] token 后序列长度: 5 (1 个 CLS + 4 个 patch)

不加位置编码时，打乱 patch 顺序后再还原，与原始输出的最大差异: 5.55e-17
（应接近 0，说明自注意力对 patch 顺序是置换等变的，本身不携带位置信息）

加入位置编码后的自注意力输出（[CLS] token 行）:
[-0.05554837 -0.18285607  0.00734118  0.13917637 -0.08074748  0.01507288]
```

`8×8×3` 图像按 `4×4` patch 切分得到 4 个 patch，每个展平维度 `4×4×3=48`，与代码输出一致。核心验证结果是最大差异 `5.55e-17`——这个量级已经是浮点数精度的极限（等价于严格意义上的 0），证实了第 2 节的论断：打乱 patch 顺序后自注意力的输出也按同样方式打乱，但每个 token 对应位置的计算结果完全不变（置换等变），自注意力本身不携带任何顺序信息，位置编码是必需品而非可选项。

## 10. 小结

| 概念 | 一句话总结 |
| --- | --- |
| 图像分块 | 把图像切成 patch，展平后线性投影成 token embedding |
| 位置编码 | 弥补自注意力置换等变、不携带顺序信息的缺陷 |
| [CLS] token | 通过自注意力自适应聚合全局信息，作为分类头输入 |
| 归纳偏置缺失 | ViT 无 CNN 式局部性/平移等变假设，需更多数据弥补 |
| Swin 窗口注意力 | 局部窗口降低计算量，移位窗口+patch merging 重建层级结构 |
| MAE 掩码重建 | 遮住大比例 patch 做自监督重建，无需标注学通用视觉表征 |

## 11. 延伸阅读

- 卷积的局部连接、权值共享等归纳偏置的来源 → [卷积原理](01-卷积原理.md)
- 自注意力机制的完整推导 → [注意力机制推导](../../llm/01-Transformer原理/01-注意力机制推导.md)
- 位置编码的具体形式（正弦编码、旋转位置编码等） → [位置编码](../../llm/01-Transformer原理/02-位置编码.md)
- BERT 的掩码语言建模与 MAE 思路的对应关系 → [BERT与自编码路线](../../llm/03-预训练范式/01-BERT与自编码路线.md)
- 预训练+微调范式在 NLP 中的完整流程 → [三阶段范式与数据构造](../../llm/04-微调与对齐/01-三阶段范式与数据构造.md)
