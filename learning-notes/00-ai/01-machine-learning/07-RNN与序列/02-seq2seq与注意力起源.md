# seq2seq 与注意力起源：从固定长度向量瓶颈到自适应对齐

> Author: Walter Wang

> **读完你能回答的 3 个问题**
>
> 1. Encoder-Decoder 结构的固定长度向量瓶颈具体指什么？为什么序列越长这个问题越严重？
> 2. Bahdanau 加法注意力和 Luong 乘法注意力的打分函数分别怎么算？两者的核心差异是什么？
> 3. Teacher Forcing 为什么会导致暴露偏差？Beam Search 又是怎么缓解贪心解码的局限的？

## 1. Encoder-Decoder 结构与固定长度向量瓶颈

seq2seq（sequence-to-sequence）要解决的是"输入序列长度和输出序列长度不必相等"的任务，例如机器翻译（源语言句子长度和目标语言句子长度通常不同）。经典结构是 **Encoder-Decoder**：

```
Encoder: x_1, x_2, ..., x_n  --RNN-->  h_n（最后一个隐藏状态，压缩了整句信息）
Decoder: h_n  --RNN-->  y_1, y_2, ..., y_m（逐步生成目标序列）
```

Encoder（用上一篇的 RNN/LSTM/GRU 实现）把整个源序列处理完，只把**最后一个时间步的隐藏状态 `h_n`** 传给 Decoder 作为初始状态——这个固定维度的向量要承载整句话的全部语义信息，这就是**固定长度向量瓶颈（fixed-length vector bottleneck）**。

问题在于：无论源序列多长（5 个词还是 50 个词），`h_n` 的维度是固定的。序列越长，需要压缩进同一个固定维度向量里的信息量越大，模型越难把所有必要信息都保留下来——这类似于试图把一本书的内容压缩进一句话摘要，句子越长信息损失通常越严重。这直接限制了 Encoder-Decoder 在长序列任务上的表现。

## 2. Bahdanau 加法注意力的推导

注意力机制最早正是为了解决这个瓶颈提出的：**不再只用 Encoder 的最后一个隐藏状态，而是让 Decoder 在生成每一个目标词时，都能"回头看"Encoder 的所有隐藏状态，并动态决定该重点关注哪些位置**。

Bahdanau 注意力（加法注意力）的打分函数：

```
score(s_{t-1}, h_i) = v_a^T · tanh(W_a @ s_{t-1} + U_a @ h_i)

s_{t-1}: decoder 上一步的隐藏状态，h_i: encoder 第 i 个位置的隐藏状态
W_a, U_a: 线性投影矩阵，v_a: 打分向量，把 tanh 输出压成一个标量
```

对 Encoder 的每个位置 `h_i` 都算一个分数，再对所有分数做 softmax 得到归一化的**对齐权重（alignment weights）** `α_i`，用这些权重对所有 `h_i` 加权求和得到当前步的**上下文向量（context vector）**：

```
α_i = softmax(score(s_{t-1}, h_i))
c_t = Σ_i α_i · h_i
```

`c_t` 会和 decoder 当前的输入一起送入 RNN，参与生成当前步的输出。之所以叫"加法"注意力，是因为 `W_a@s_{t-1}` 和 `U_a@h_i` 是先相加再经过 `tanh` 非线性，而不是像点积那样直接相乘。

## 3. Luong 乘法注意力的差异

Luong 注意力提出了更简单的打分方式，用双线性（乘法）形式替代加法+非线性：

```
score(s_t, h_i) = s_t^T @ W_l @ h_i
```

没有 `tanh` 非线性，也不需要独立的打分向量 `v_a`，只用一个矩阵 `W_l` 直接对两个隐藏状态做双线性打分——计算更直接、参数更少。当 `W_l` 取单位矩阵时，打分退化成两个向量的点积，这正是后续 Transformer 自注意力打分函数 `QK^T` 的直接前身。两种注意力在实践中效果接近，Luong 因为形式更简单、计算更快，逐渐成为后续工作的主流选择（Transformer 的缩放点积注意力正是乘法注意力路线的延续）。

## 4. 注意力对齐的可解释性

注意力权重矩阵 `α` 有一个额外的好处：它本身构成了一张"源序列位置 -> 目标序列位置"的**软对齐（soft alignment）图**——如果把每一步 decoder 生成时的权重向量堆叠起来，得到一个矩阵，可以直接可视化看出模型在生成某个目标词时主要关注了源序列的哪些位置。这在机器翻译里天然对应人类理解的"词对齐"直觉（比如生成某个目标语言词时，权重最高的源语言位置通常就是它的翻译来源），也是注意力机制相比"黑箱"RNN 更容易被解释的原因之一。

## 5. Teacher Forcing 与暴露偏差

训练 seq2seq 模型时，decoder 在生成第 `t` 步的输出时，需要知道第 `t-1` 步的"输入"（自回归结构）。**Teacher Forcing** 指训练时直接把真实的第 `t-1` 步目标词（ground truth）作为输入，而不是用模型自己在第 `t-1` 步实际生成的词——这样可以避免早期训练时模型生成质量差、导致误差累积拖累后续所有步骤，让训练更快收敛。

代价是**暴露偏差（exposure bias）**：训练时 decoder 总是看到"正确答案"作为历史输入，但推理时模型只能用自己生成的（可能有误的）词作为下一步输入——训练和推理时 decoder 看到的输入分布不一致。如果模型在推理早期生成了一个错误的词，这个错误会像滚雪球一样影响后续所有步骤的生成，而这种"从错误中恢复"的场景在 Teacher Forcing 训练中从未被模型见过。

## 6. Beam Search 解码

如果 decoder 每一步都只贪心地选概率最高的词（**贪心解码，greedy decoding**），容易陷入局部最优——某一步选的"当前看起来最好"的词，可能导致后续步骤只能在更差的选项里挑，而当步选个稍差的词反而可能让整体序列概率更高。

**Beam Search** 用一个宽度参数 `k`（beam size）缓解这个问题：每一步不再只保留概率最高的 1 个候选，而是同时保留 `k` 个概率最高的部分序列（beam），下一步基于这 `k` 个候选分别扩展，再从所有扩展结果中重新选出概率最高的 `k` 个——相当于在贪心和穷举所有可能序列（计算量随序列长度指数爆炸）之间找一个折中。`k=1` 时退化为贪心解码，`k` 越大越接近全局最优，但计算量也线性增长。

## 7. 从这里到 Transformer 自注意力的思路跳跃

注意力机制在 seq2seq 里最初的角色，是**给 RNN 结构"打补丁"**——RNN 依然承担主要的序列建模工作（逐步递推处理序列），注意力只是额外提供了一条让 decoder 直接访问 encoder 全部历史状态的捷径，用来缓解固定长度向量瓶颈。

Transformer 的关键跳跃在于：**如果注意力已经能让任意两个位置直接交互，那 RNN 的逐步递推是否还必要？** 答案是不必要——完全去掉循环结构，只用注意力机制本身（自注意力，序列对自己求注意力）就足以建模序列内部任意两个位置的依赖关系，而且因为不再依赖递推，所有位置的计算可以完全并行（呼应上一篇末尾提到的 RNN 并行性限制）。这个"注意力从辅助机制变成唯一的核心机制"的转变，正是 Transformer 架构的起点（[注意力机制推导](../../02-llm/01-Transformer原理/01-注意力机制推导.md)会展开自注意力和缩放点积的具体形式）。

## 8. 最小可运行实现：手写加法/乘法注意力对齐

```python
"""
手写 Bahdanau 加法注意力与 Luong 乘法注意力，构造一个简单的对齐场景验证权重矩阵：
encoder 输出一串源语言隐藏状态，人工构造位置2与 decoder 当前状态"该对齐"，
观察两种注意力算出的对齐权重是否都能正确聚焦到这个位置。
"""
import numpy as np


def softmax(x, axis=-1):
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)


def bahdanau_attention(decoder_state, encoder_states, Wa, Ua, va):
    """Bahdanau (加法) 注意力：score_i = v^T @ tanh(Wa@s + Ua@h_i)，再整体 softmax"""
    n = encoder_states.shape[0]
    scores = np.zeros(n)
    for i in range(n):
        e = np.tanh(Wa @ decoder_state + Ua @ encoder_states[i])
        scores[i] = va @ e
    weights = softmax(scores)
    context = weights @ encoder_states
    return weights, context


def luong_attention(decoder_state, encoder_states, Wl):
    """Luong (乘法/双线性) 注意力：score_i = s^T @ Wl @ h_i，比加法注意力少一次 tanh"""
    n = encoder_states.shape[0]
    scores = np.array([decoder_state @ Wl @ encoder_states[i] for i in range(n)])
    weights = softmax(scores)
    context = weights @ encoder_states
    return weights, context


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    dim = 6
    n_src = 5  # 源序列长度

    # 构造 encoder 隐藏状态：让位置2的向量刻意与某个方向对齐，模拟"该被关注的词"
    encoder_states = rng.normal(0, 0.15, (n_src, dim))
    target_direction = rng.normal(0, 1.0, dim)
    target_direction = target_direction / np.linalg.norm(target_direction)
    encoder_states[2] = target_direction * 0.8  # 位置2与目标方向对齐，范数适中避免 tanh 饱和

    # decoder 当前状态构造为与目标方向高度相关
    decoder_state = target_direction * 0.8

    # 用近似恒等矩阵（对角占优 + 小噪声），让打分函数尽量保留原始向量的方向信息
    Wa = np.eye(dim) + rng.normal(0, 0.02, (dim, dim))
    Ua = np.eye(dim) + rng.normal(0, 0.02, (dim, dim))
    va = target_direction  # 打分向量对齐目标方向，放大"匹配方向"的贡献
    Wl = np.eye(dim) + rng.normal(0, 0.02, (dim, dim))

    weights_add, context_add = bahdanau_attention(decoder_state, encoder_states, Wa, Ua, va)
    weights_mul, context_mul = luong_attention(decoder_state, encoder_states, Wl)

    print("=== Bahdanau 加法注意力对齐权重 ===")
    for i, w in enumerate(weights_add):
        marker = " <- 构造的目标对齐位置" if i == 2 else ""
        print(f"  位置{i}: {w:.4f}{marker}")
    print(f"权重和: {weights_add.sum():.6f}")
    print(f"注意力最大权重位置: {np.argmax(weights_add)} (应为构造的位置2)")

    print("\n=== Luong 乘法注意力对齐权重 ===")
    for i, w in enumerate(weights_mul):
        marker = " <- 构造的目标对齐位置" if i == 2 else ""
        print(f"  位置{i}: {w:.4f}{marker}")
    print(f"注意力最大权重位置: {np.argmax(weights_mul)} (应为构造的位置2)")

    print(f"\n两种注意力上下文向量差异范数: {np.linalg.norm(context_add - context_mul):.4f}")
```

实测输出（numpy 2.4.4）：

```
=== Bahdanau 加法注意力对齐权重 ===
  位置0: 0.1863
  位置1: 0.1516
  位置2: 0.3045 <- 构造的目标对齐位置
  位置3: 0.1910
  位置4: 0.1668
权重和: 1.000000
注意力最大权重位置: 2 (应为构造的位置2)

=== Luong 乘法注意力对齐权重 ===
  位置0: 0.1771
  位置1: 0.1454
  位置2: 0.3381 <- 构造的目标对齐位置
  位置3: 0.1814
  位置4: 0.1579
注意力最大权重位置: 2 (应为构造的位置2)

两种注意力上下文向量差异范数: 0.0303
```

两种注意力都正确地把最高权重（Bahdanau 0.3045，Luong 0.3381）分配给了人工构造的"该对齐"位置2，且权重和精确为 1（符合 softmax 归一化性质）——验证了第 2、3 节的打分公式确实能让注意力权重反映向量之间的方向相似度。两种注意力算出的上下文向量差异范数仅 0.03（相对于向量本身量级很小），印证了第 3 节的论断：当打分矩阵接近恒等变换时，加法注意力（多一次 `tanh` 非线性）和乘法注意力（直接双线性打分）在效果上高度接近，这也是后续工作更多转向计算更简单的乘法/点积注意力的实践依据。

## 9. 小结

| 概念 | 一句话总结 |
| --- | --- |
| 固定长度向量瓶颈 | Encoder 最后隐藏状态承载整句信息，序列越长损失越大 |
| Bahdanau 加法注意力 | `v^T·tanh(Wa·s+Ua·h)` 打分，多一次非线性 |
| Luong 乘法注意力 | `s^T·Wl·h` 双线性打分，是点积注意力的前身 |
| 对齐权重 | softmax 归一化后的注意力分布，天然具备可解释性 |
| Teacher Forcing | 训练用真实标签做输入，加快收敛但引入暴露偏差 |
| Beam Search | 保留 k 个候选序列扩展，折中贪心解码与全局最优 |
| 到 Transformer 的跳跃 | 注意力从"RNN 的补丁"变成唯一核心机制，摆脱递推限制 |

## 10. 延伸阅读

- RNN/LSTM 的递推结构与并行限制 → [RNN-LSTM-GRU](01-RNN-LSTM-GRU.md)
- 自注意力和缩放点积注意力的完整推导 → [注意力机制推导](../../02-llm/01-Transformer原理/01-注意力机制推导.md)
- Transformer 的位置编码如何替代 RNN 隐式的顺序信息 → [位置编码](../../02-llm/01-Transformer原理/02-位置编码.md)
- Transformer 编码器解码器架构中的残差与归一化设计 → [架构组件与训练稳定性](../../02-llm/01-Transformer原理/03-架构组件与训练稳定性.md)

## 🎬 推荐视频资源

> 以下资源均为频道 / 课程 / 官网入口级链接（已于 2026-08-04 实测可访问）。刻意不收录单个视频 ID——那类链接失效率高，且难以核实归属。
> 从入口进去按本篇主题检索，命中率比一条可能失效的直链更高。

### 📺 视频频道与课时

- [跟李沐学AI（B 站）](https://space.bilibili.com/1567748478)
- [3Blue1Brown - 注意力机制](https://www.3blue1brown.com/lessons/attention)

### 🎓 系统课程与教材

- [动手学深度学习（中文版）](https://zh.d2l.ai/)
- [Stanford CS224n 深度学习与自然语言处理](https://web.stanford.edu/class/cs224n/)

### 📖 专题图文

- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
