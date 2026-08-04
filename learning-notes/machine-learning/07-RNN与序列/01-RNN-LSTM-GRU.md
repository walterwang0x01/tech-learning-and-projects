# RNN / LSTM / GRU：序列建模与梯度消失的博弈

> Author: Walter Wang

> **读完你能回答的 3 个问题**
>
> 1. RNN 的参数共享体现在哪里？BPTT 展开后为什么会出现梯度连乘、进而导致梯度消失？
> 2. LSTM 的细胞状态为什么能缓解梯度消失？三个门分别在这个机制里起什么作用？
> 3. GRU 相比 LSTM 简化了什么？RNN 系列模型在结构上有什么本质限制，是后来 Transformer 要解决的？

## 1. RNN 的参数共享与展开计算图

RNN 处理序列数据的核心思想是**在每个时间步复用同一套参数**，把当前时刻的输入和上一时刻的隐藏状态一起映射成新的隐藏状态：

```
h_t = tanh(Wx @ x_t + Wh @ h_{t-1} + b)
```

`Wx`、`Wh`、`b` 在所有时间步上是同一组参数——这是卷积权值共享思想（卷积原理篇）在序列维度的对应版本：假设"同一种时序模式无论出现在序列哪个位置，处理方式应该一样"。这个假设让 RNN 参数量与序列长度无关，可以处理任意长度输入。

把这个递推展开成计算图：`h_0 → h_1 → h_2 → ... → h_T`，每一步依赖前一步输出，反向传播时要沿这条链逐步往回传，这个过程称为**BPTT（Backpropagation Through Time）**。

## 2. BPTT 推导与梯度连乘问题

对损失 `L`（通常是所有时间步损失之和）求关于早期隐藏状态 `h_0` 的梯度，链式法则会把梯度沿时间维度逐步相乘：

```
∂L/∂h_0 = ∂L/∂h_T · ∏_{t=1}^{T} ∂h_t/∂h_{t-1}

∂h_t/∂h_{t-1} = diag(1 - tanh²(z_t)) · Wh，其中 z_t = Wx@x_t + Wh@h_{t-1} + b
```

这与经典网络演进篇中 ResNet 一节推导的"普通堆叠网络梯度连乘"是同一个数学结构，只是"层数"变成了"时间步数"。如果 `Wh` 谱范数小于 1，或 `tanh` 导数持续压制梯度，经过很多时间步连乘后梯度会指数级衰减到接近 0——这是 RNN 学不到长距离依赖的根本原因（梯度消失）；反过来谱范数大于 1 则梯度爆炸，是 RNN 训练中常见的数值不稳定来源（[反向传播推导](../04-神经网络原理/02-反向传播推导.md)已给出这个连乘现象的一般性结论）。

## 3. LSTM：三个门与细胞状态

LSTM（Long Short-Term Memory）在隐藏状态之外，额外引入一条**细胞状态（cell state）** `c_t`，并用三个门控制信息流动：

```
f_t = sigmoid(Wf @ [x_t, h_{t-1}] + bf)   # 遗忘门
i_t = sigmoid(Wi @ [x_t, h_{t-1}] + bi)   # 输入门
o_t = sigmoid(Wo @ [x_t, h_{t-1}] + bo)   # 输出门
g_t = tanh(Wg @ [x_t, h_{t-1}] + bg)      # 候选值（本步新信息）

c_t = f_t * c_{t-1} + i_t * g_t           # 细胞状态更新：加法路径
h_t = o_t * tanh(c_t)                     # 隐藏状态：细胞状态经输出门筛选后暴露
```

三个门的直觉分工：**遗忘门**决定旧细胞状态保留多少（`f_t≈1` 大量保留，`f_t≈0` 几乎清空）；**输入门**决定当前新信息 `g_t` 写入多少；**输出门**决定当前细胞状态暴露给隐藏状态多少。

## 4. 细胞状态为何能缓解梯度消失：关键是加法更新路径

对比 RNN 的隐藏状态递推 `h_t=tanh(Wh@h_{t-1}+...)`（乘法为主导）和 LSTM 的细胞状态递推 `c_t = f_t*c_{t-1} + i_t*g_t`（**加法**更新），求关于 `c_{t-1}` 的偏导：

```
∂c_t/∂c_{t-1} = f_t
```

这个梯度**只是遗忘门 `f_t` 本身**，不需要经过 `tanh` 导数和权重矩阵的复合变换。若遗忘门学到"该长期保留"，`f_t` 会稳定在接近 1 的区间，连乘 `∏ f_t` 只要每个 `f_t` 接近 1 就不会指数衰减。这与 ResNet 恒等跳连 `y=x+F(x)` 给梯度的"恒等路径 `+1`"是同一原理——LSTM 把这条路径的权重从固定 1 变成了可学习的门控值 `f_t`。

工程实践中常把遗忘门偏置初始化为正值（如 1~2），让 `sigmoid` 输出在训练初期就偏向 0.8 以上，从一开始给梯度回传留一条默认畅通的通道。

## 5. GRU：简化与权衡

GRU（Gated Recurrent Unit）把 LSTM 的三个门简化成两个：**更新门**和**重置门**，不再维护独立的细胞状态，直接在隐藏状态上做门控更新：

```
z_t = sigmoid(Wz @ [x_t, h_{t-1}])        # 更新门：类似 LSTM 遗忘门+输入门的合并
r_t = sigmoid(Wr @ [x_t, h_{t-1}])        # 重置门：控制多少历史信息参与候选值计算
g_t = tanh(Wg @ [x_t, r_t * h_{t-1}])     # 候选隐藏状态
h_t = (1 - z_t) * h_{t-1} + z_t * g_t     # 隐藏状态更新：同样是加法路径
```

`h_t` 的更新式同样是**加法主导**，保留了 LSTM 缓解梯度消失的核心机制，同时少了一套独立的细胞状态和一个门，参数量更少、计算更快。权衡在于 GRU 的表达能力理论上略弱于 LSTM，但在很多任务上效果接近甚至持平，具体哪个更优依赖任务和数据规模，没有绝对结论。

## 6. 双向 RNN

标准 RNN 只能利用"过去"的信息，但很多任务里"未来"的上下文同样重要（如词性标注中一个词的角色可能取决于后面的词）。**双向 RNN（Bidirectional RNN）** 用两个独立的 RNN 分别沿正向和反向扫描序列，把每个时间步两个方向的隐藏状态拼接作为最终表示：`h_t = [h_t_forward, h_t_backward]`。代价是必须等整条序列输入完才能计算反向部分，因此不能用于严格的自回归生成任务，主要用在编码阶段（如 seq2seq 的 encoder，下一篇展开）。

## 7. 序列建模的本质限制：无法并行

RNN 系列模型有一个结构性限制：`h_t` 的计算必须等 `h_{t-1}` 算完才能开始，这是递推定义本身决定的，不管硬件算力多强都无法把不同时间步的计算并行展开。序列越长，串行链条越长，训练和推理时间开销与序列长度基本呈线性关系，且无法通过增加算力缩短单条序列内部的计算时间。

这正是 Transformer 用自注意力取代循环结构的核心动机之一：自注意力让序列中任意两个位置的交互都能**一次性、并行**计算完成，不再需要逐时间步递推（[注意力机制推导](../../llm/01-Transformer原理/01-注意力机制推导.md)展开这个机制）。下一篇讲 seq2seq 与注意力起源时会看到，注意力机制最早正是在 RNN 框架内部被提出来解决另一个问题（固定长度向量瓶颈），后来才独立发展成完全替代循环结构的自注意力。

## 8. 最小可运行实现：LSTM 与 RNN 的梯度衰减对比

```python
"""
手写 RNN 与 LSTM 的单步前向 + 多步梯度回传对比：
  1. 普通 RNN：h_t = tanh(Wx @ x_t + Wh @ h_{t-1})，梯度沿 h 连乘容易衰减
  2. LSTM：细胞状态 c_t = f_t * c_{t-1} + i_t * g_t，加法更新路径缓解梯度消失
观察在同样步数下，两者把梯度传回最初时间步时的量级差异。
"""
import numpy as np

rng = np.random.default_rng(0)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def lstm_step(x_t, h_prev, c_prev, params):
    """LSTM 单步前向：遗忘门 f、输入门 i、输出门 o、候选值 g（各门都有独立 bias 向量）"""
    Wf, Wi, Wo, Wg = params["Wf"], params["Wi"], params["Wo"], params["Wg"]
    bf, bi, bo, bg = params["bf"], params["bi"], params["bo"], params["bg"]
    z = np.concatenate([x_t, h_prev])
    f = sigmoid(Wf @ z + bf)   # 遗忘门：决定保留多少旧细胞状态
    i = sigmoid(Wi @ z + bi)   # 输入门：决定写入多少新候选信息
    o = sigmoid(Wo @ z + bo)   # 输出门：决定细胞状态多少暴露给隐藏状态
    g = np.tanh(Wg @ z + bg)  # 候选值：本步产生的新信息
    c_t = f * c_prev + i * g   # 细胞状态更新：加法路径，f≈1 时旧状态几乎原样保留
    h_t = o * np.tanh(c_t)
    return h_t, c_t, (f, i, o, g)


def rnn_grad_through_time(dim, n_steps, scale):
    """普通 RNN：梯度沿隐藏状态连乘，dh_t/dh_{t-1} = diag(1-tanh^2) @ Wh"""
    rng_local = np.random.default_rng(1)
    Wh = rng_local.normal(0, scale, (dim, dim))
    Wx = rng_local.normal(0, scale, (dim, dim))
    h = np.zeros(dim)
    x_seq = [rng_local.normal(size=dim) for _ in range(n_steps)]
    zs = []
    for x_t in x_seq:
        z = Wx @ x_t + Wh @ h
        zs.append(z)
        h = np.tanh(z)
    grad = np.ones(dim)
    for t in range(n_steps - 1, -1, -1):
        tanh_grad = 1 - np.tanh(zs[t]) ** 2
        grad = Wh.T @ (grad * tanh_grad)
    return np.linalg.norm(grad)


def lstm_grad_through_time(dim, n_steps, forget_bias):
    """LSTM：细胞状态梯度 dc_t/dc_{t-1} = f_t（遗忘门），只要 f_t 接近 1 梯度就不会消失。
    forget_bias 是遗忘门的偏置向量取值，权重矩阵 Wf 用小 scale，让 f_t 主要由 bias 决定、
    不被输入大幅扰动（对应工程实践中遗忘门 bias 初始化偏正、让门默认偏向"保留"）"""
    rng_local = np.random.default_rng(1)
    concat_dim = dim * 2
    params = {
        "Wf": rng_local.normal(0, 0.1, (dim, concat_dim)),
        "Wi": rng_local.normal(0, 0.3, (dim, concat_dim)),
        "Wo": rng_local.normal(0, 0.3, (dim, concat_dim)),
        "Wg": rng_local.normal(0, 0.3, (dim, concat_dim)),
        "bf": np.full(dim, forget_bias),
        "bi": np.zeros(dim),
        "bo": np.zeros(dim),
        "bg": np.zeros(dim),
    }
    h = np.zeros(dim)
    c = np.zeros(dim)
    x_seq = [rng_local.normal(size=dim) for _ in range(n_steps)]
    fs = []
    for x_t in x_seq:
        h, c, (f, i, o, g) = lstm_step(x_t, h, c, params)
        fs.append(f)
    # 细胞状态梯度回传：只沿遗忘门 f_t 连乘（对应 c_t = f_t*c_{t-1} + ... 的加法路径导数）
    grad = np.ones(dim)
    for t in range(n_steps - 1, -1, -1):
        grad = grad * fs[t]
    return np.linalg.norm(grad), np.mean(fs)


if __name__ == "__main__":
    dim = 8
    scale = 0.3

    print("=== LSTM 单步前向示例（遗忘门 bias=2.0） ===")
    params = {
        "Wf": rng.normal(0, 0.1, (dim, dim * 2)),
        "Wi": rng.normal(0, 0.3, (dim, dim * 2)),
        "Wo": rng.normal(0, 0.3, (dim, dim * 2)),
        "Wg": rng.normal(0, 0.3, (dim, dim * 2)),
        "bf": np.full(dim, 2.0),
        "bi": np.zeros(dim),
        "bo": np.zeros(dim),
        "bg": np.zeros(dim),
    }
    x0 = rng.normal(size=dim)
    h0 = np.zeros(dim)
    c0 = np.zeros(dim)
    h1, c1, (f, i, o, g) = lstm_step(x0, h0, c0, params)
    print(f"遗忘门 f 均值={f.mean():.4f}, 输入门 i 均值={i.mean():.4f}, 输出门 o 均值={o.mean():.4f}")
    print(f"细胞状态 c_1 范数={np.linalg.norm(c1):.4f}, 隐藏状态 h_1 范数={np.linalg.norm(h1):.4f}")

    print("\n=== 不同序列长度下，梯度传回第一步的范数对比 ===")
    print("普通RNN权重 scale=0.3（谱范数<1，易梯度消失）；LSTM遗忘门bias=2.0(sigmoid≈0.88)")
    print(f"{'步数':>4} | {'普通RNN(隐藏状态连乘)':>20} | {'LSTM(细胞状态遗忘门连乘)':>22} | {'遗忘门均值':>10}")
    for n_steps in [5, 10, 20, 40]:
        g_rnn = rnn_grad_through_time(dim, n_steps, scale)
        g_lstm, f_mean = lstm_grad_through_time(dim, n_steps, forget_bias=2.0)
        print(f"{n_steps:>4} | {g_rnn:>20.6e} | {g_lstm:>22.6e} | {f_mean:>10.4f}")
```

实测输出（numpy 2.4.4）：

```
=== LSTM 单步前向示例（遗忘门 bias=2.0） ===
遗忘门 f 均值=0.8832, 输入门 i 均值=0.4678, 输出门 o 均值=0.5587
细胞状态 c_1 范数=0.9805, 隐藏状态 h_1 范数=0.6154

=== 不同序列长度下，梯度传回第一步的范数对比 ===
普通RNN权重 scale=0.3（谱范数<1，易梯度消失）；LSTM遗忘门bias=2.0(sigmoid≈0.88)
  步数 |        普通RNN(隐藏状态连乘) |        LSTM(细胞状态遗忘门连乘) |      遗忘门均值
   5 |         1.496980e-01 |           1.478855e+00 |     0.8782
  10 |         9.626202e-04 |           7.256445e-01 |     0.8729
  20 |         7.485439e-08 |           1.879734e-01 |     0.8728
  40 |         2.744657e-14 |           1.420769e-02 |     0.8743
```

遗忘门 bias 设为 2.0，`sigmoid(2.0)≈0.88`，实测遗忘门均值稳定在 0.87~0.88，与设置一致。梯度对比印证了第 4 节的推导：普通 RNN 梯度范数随步数**指数级衰减**——40 步后降到 `2.7e-14`，梯度信号实质已消失；LSTM 梯度范数（沿遗忘门连乘）衰减明显更慢，40 步后仍保持 `1.4e-2` 量级，比同等步数下的 RNN 高出约 12 个数量级。这正是"加法更新路径 + 门控值接近 1"能显著缓解长序列梯度消失的直接证据。

## 9. 小结

| 概念 | 一句话总结 |
| --- | --- |
| RNN 参数共享 | 所有时间步复用同一套权重，参数量与序列长度无关 |
| BPTT | 沿时间展开的反向传播，梯度沿隐藏状态连乘 |
| 梯度消失/爆炸 | 连乘项谱范数<1 则消失，>1 则爆炸，长序列尤其明显 |
| LSTM 细胞状态 | 加法更新路径 `c_t=f_t·c_{t-1}+i_t·g_t`，梯度只需乘 `f_t` |
| 三个门 | 遗忘门控保留、输入门控写入、输出门控暴露 |
| GRU | 合并门控、去掉独立细胞状态，参数更少 |
| 双向 RNN | 拼接正反向隐藏状态，利用未来上下文，不能用于自回归生成 |
| 序列建模本质限制 | 递推结构无法并行，是 Transformer 用自注意力取代 RNN 的核心动机 |

## 10. 延伸阅读

- 梯度连乘导致消失/爆炸的一般性推导 → [反向传播推导](../04-神经网络原理/02-反向传播推导.md)
- ResNet 恒等跳连与本篇加法更新路径的同构关系 → [经典网络演进](../06-CNN与视觉/02-经典网络演进.md)
- 下一篇：seq2seq 结构与注意力机制如何从 RNN 框架内部萌芽 → [seq2seq与注意力起源](02-seq2seq与注意力起源.md)
- 自注意力如何彻底摆脱递推、实现并行计算 → [注意力机制推导](../../llm/01-Transformer原理/01-注意力机制推导.md)
