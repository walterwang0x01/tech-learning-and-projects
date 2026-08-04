# KV Cache 与显存分析

> Author: Walter Wang

> **读完你能回答的 3 个问题**
>
> 1. 自回归生成不用 KV Cache 会重复计算什么？KV Cache 省的是哪部分计算？
> 2. KV Cache 显存占用怎么按"层数×头数×头维×序列长×batch×2×字节数"逐项算出？
> 3. 为什么 Prefill 阶段计算密集，Decode 阶段显存带宽密集？这个差异如何影响推理系统设计？

## 1. 自回归生成为何有大量重复计算

Transformer 解码器生成文本是**自回归（autoregressive）**的：给定前面已生成的 token，一次预测下一个 token，生成后拼回输入，再预测下一个，如此循环。

问题在于 self-attention 的计算方式。对于第 `t` 步要生成的 token，attention 需要用它的 query 去和**所有历史位置**（`1` 到 `t-1`）的 key、value 做计算：

```
Attention(Q_t, K_{1:t}, V_{1:t}) = softmax(Q_t · K_{1:t}ᵀ / √d) · V_{1:t}
```

如果不做任何缓存，每生成一个新 token，都要把从头到当前位置的**完整序列**重新输入模型、重新计算一遍所有位置的 `K` 和 `V`：

```
生成第 1 个 token：输入 [x1]              → 算 K1,V1
生成第 2 个 token：输入 [x1,x2]           → 重新算 K1,V1,K2,V2（K1,V1 重复计算）
生成第 3 个 token：输入 [x1,x2,x3]        → 重新算 K1,V1,K2,V2,K3,V3（前两组都重复）
```

**关键观察**：第 `i` 个 token 的 key 向量 `K_i = x_i · W_K` 和 value 向量 `V_i = x_i · W_V`，只依赖该 token 自身的输入表示，跟后面生成了多少新 token 无关，**算出来之后永远不会变**。而朴素实现每步都重新算了一遍，是纯粹的浪费。

## 2. KV Cache 的原理：省的是什么

**KV Cache** 的思路很直接：把每层每个历史位置算出来的 `K`、`V` 向量缓存下来，后续步骤直接复用，不再重新计算。

```
不带 Cache：
  第 t 步输入 = 全部历史 token [x1, ..., xt]
  第 t 步计算 = 重新算 K1..Kt, V1..Vt（O(t) 重复计算）+ 全部 attention

带 Cache：
  第 t 步输入 = 仅新 token [xt]
  第 t 步计算 = 只算 Kt, Vt（O(1) 新计算）+ 从 cache 取出 K1..K(t-1), V1..V(t-1)
  更新：把 Kt, Vt 追加进 cache
```

省掉的是 **Key/Value 的投影计算**（`x · W_K`、`x · W_V`）在历史位置上的重复部分。**Query 不需要缓存**：每步只需当前新 token 的 query 去查历史 K、V，历史 query 用不上（那些位置在自己那一步已产出过输出）。

**没有省掉的部分**：attention 的 softmax 计算量（`Q_t · K_{1:t}ᵀ`）仍是 `O(t)`，随序列长度线性增长；每步仍要过一遍 FFN。KV Cache 解决的是"投影计算的重复"，不是"attention 本身随长度增长"这件事。

用 numpy 直观对比"不带 cache"和"带 cache"两种解码方式的浮点计算量（FLOPs），见第 6 节。

## 3. 显存占用公式：逐项拆解

KV Cache 要用显存换计算，具体占多少显存需要精确算清楚，是推理系统容量规划的基础。

对于一个标准多头注意力（不考虑 GQA/MQA 压缩），单个 token 在单层要缓存的 K 和 V 各是一个 `n_heads × d_head` 维的向量。总显存占用公式：```
Cache_bytes = n_layers × n_heads × d_head × seq_len × batch_size × 2 × dtype_bytes
```

逐项含义：

| 因子 | 含义 | 典型量级影响 |
| --- | --- | --- |
| `n_layers` | Transformer 层数 | 每层独立缓存自己的 K/V，线性增长 |
| `n_heads` | 注意力头数 | 每个 head 的 K/V 独立存储 |
| `d_head` | 每个 head 的维度（通常 `d_model / n_heads`） | 决定单个 K/V 向量长度 |
| `seq_len` | 当前缓存的序列长度 | 随生成持续增长，是显存增长主因 |
| `batch_size` | 并发请求数 | 多请求同时服务时线性叠加 |
| `2` | K 和 V 两份 | 缺一不可 |
| `dtype_bytes` | 存储精度对应字节数（FP16=2, FP32=4, INT8=1） | 直接线性影响显存 |

注意 `n_heads × d_head = d_model`（模型隐藏维度），公式也常写作：

```
Cache_bytes = n_layers × d_model × seq_len × batch_size × 2 × dtype_bytes
```

**这个公式说明什么**：显存占用与 `seq_len` 和 `batch_size` 都是**线性关系**且相乘——序列越长、并发越多，显存需求同时被两个维度放大。这是长上下文和高并发难以同时满足的根本原因：显存有限，KV Cache 会和模型权重、激活值抢显存。

> ⚠️ 待确认：具体模型的层数、头数、隐藏维度等结构参数因模型而异，这里不给具体数字，只讲公式结构。

## 4. Prefill 与 Decode：两种完全不同的计算特性

自回归生成分两个阶段，计算特性截然不同：

**Prefill（预填充）**：处理用户输入的完整 prompt，一次性对所有输入 token 做前向计算，同时把每一层每个位置的 K、V 填进 cache。这一步是**计算密集（compute-bound）**的——矩阵乘法规模是 `[seq_len, d_model] × [d_model, d_model]`，GPU 算力能被充分利用。

**Decode（解码）**：每步只处理 1 个新 token（batch 内每个请求各 1 个），从 cache 读出全部历史 K、V 做 attention，把新算出的 K、V 追加进 cache。这一步是**显存带宽密集（memory-bandwidth-bound）**的——矩阵乘法退化成 `[1, d_model] × [d_model, d_model]`，即向量乘矩阵，计算量小，但要把整份 KV Cache 从显存搬到计算单元参与 attention，**搬运时间远超实际计算时间**。

```
Prefill：
  [seq_len, d_model] · W          ← 大矩阵乘法，算力主导
  同时写入 K/V cache（seq_len 个位置一次性写完）

Decode（第 t 步）：
  [1, d_model] · W                ← 向量乘矩阵，算力需求小
  从 cache 读出 [t, d_head] 的 K, V ← 显存搬运主导，t 越大搬运量越大
  写入 1 个新位置的 K/V 进 cache
```

**这个差异直接决定推理系统的优化方向**：Prefill 阶段提升吞吐靠算力利用率（更大矩阵乘法效率、并行度）；Decode 阶段提升吞吐靠**减少显存搬运量**或**让更多请求共享搬运成本**——这正是 MQA/GQA（压缩 cache 尺寸）和连续批处理（共享调度开销）存在的原因。

## 5. MQA/GQA：压缩 KV Cache 的思路

标准多头注意力（MHA）里，Query、Key、Value 都各有 `n_heads` 组独立投影，KV Cache 大小与 `n_heads` 成正比。

**Multi-Query Attention (MQA)**：所有 query head 仍独立，但**所有 head 共享同一组 Key/Value**。KV Cache 的 `n_heads` 因子变成 `1`，显存占用直接除以原来的头数。代价是模型表达能力有所下降（所有 head 只能看同一份 K/V，注意力模式多样性降低）。

**Grouped-Query Attention (GQA)**：介于 MHA 和 MQA 之间，把 `n_heads` 个 query head 分成 `n_groups` 组，组内共享一份 K/V。`n_groups = n_heads` 时退化为 MHA，`n_groups = 1` 时退化为 MQA。

```
MHA:  n_heads 个 Q，n_heads 个 K/V   → cache 因子 n_heads
GQA:  n_heads 个 Q，n_groups 个 K/V  → cache 因子 n_groups
MQA:  n_heads 个 Q，1 个 K/V         → cache 因子 1
```

GQA 是常见折中方案：显存压缩比例可通过 `n_groups` 灵活调节，同时相比 MQA 保留更多表达能力多样性。压缩比例直接体现在第 3 节公式的 `n_heads` 因子上——把它替换成 `n_groups` 即可。

## 6. 代码：带/不带 Cache 的解码计算量对比

用 numpy 实现简化的单层单头 self-attention 解码过程，统计"不带 cache 每步重算全部历史 K/V"与"带 cache 只算新 token"两种方式的浮点乘加次数，验证 KV Cache 省的到底是哪部分计算。

```python
import numpy as np

rng = np.random.default_rng(0)

d_model = 64      # 模型隐藏维度
seq_len_final = 32  # 最终生成序列长度（含初始 prompt 长度）
prompt_len = 4    # 初始 prompt 长度，之后逐步生成到 seq_len_final

# 随机初始化投影矩阵，模拟一层 attention 的 K/V/Q 投影
W_q = rng.normal(0, 0.1, (d_model, d_model))
W_k = rng.normal(0, 0.1, (d_model, d_model))
W_v = rng.normal(0, 0.1, (d_model, d_model))

# 模拟完整序列的输入表示（真实场景中来自上一层的输出）
full_hidden = rng.normal(0, 1.0, (seq_len_final, d_model))


def matmul_flops(m, k, n):
    """m×k 乘 k×n 的乘加次数"""
    return m * k * n


def decode_without_cache(hidden, prompt_len, seq_len_final, d_model):
    """不带 cache：每一步都重新对全部历史 token 做 K/V/Q 投影"""
    total_flops = 0
    for t in range(prompt_len, seq_len_final + 1):
        cur_len = t
        total_flops += matmul_flops(cur_len, d_model, d_model)  # K 投影
        total_flops += matmul_flops(cur_len, d_model, d_model)  # V 投影
        total_flops += matmul_flops(cur_len, d_model, d_model)  # Q 投影（最坏情况按全量算，作对比参照系）
        total_flops += matmul_flops(cur_len, d_model, cur_len)  # Q·K^T 打分
        total_flops += matmul_flops(cur_len, cur_len, d_model)  # softmax 后加权求和 V
    return total_flops


def decode_with_cache(hidden, prompt_len, seq_len_final, d_model):
    """带 cache：prefill 阶段一次性算完 prompt，之后每步只对 1 个新 token 算 K/V/Q"""
    total_flops = 0

    # Prefill：一次性对 prompt_len 个 token 做投影
    total_flops += matmul_flops(prompt_len, d_model, d_model) * 3  # K, V, Q
    total_flops += matmul_flops(prompt_len, d_model, prompt_len)   # 打分
    total_flops += matmul_flops(prompt_len, prompt_len, d_model)   # 加权求和

    # Decode：每步只对新 token（1 个）算 K/V/Q，attention 与全部历史 cache 交互
    for t in range(prompt_len, seq_len_final):
        cur_len = t + 1  # 加上这一步新生成的 token 后的历史长度
        total_flops += matmul_flops(1, d_model, d_model) * 3  # 新 token 的 K, V, Q 投影
        total_flops += matmul_flops(1, d_model, cur_len)      # 与全部 cache 的 K 打分
        total_flops += matmul_flops(1, cur_len, d_model)      # 与全部 cache 的 V 加权求和

    return total_flops


flops_no_cache = decode_without_cache(full_hidden, prompt_len, seq_len_final, d_model)
flops_with_cache = decode_with_cache(full_hidden, prompt_len, seq_len_final, d_model)

print(f"不带 KV Cache 的总乘加次数: {flops_no_cache:,}")
print(f"带 KV Cache 的总乘加次数:   {flops_with_cache:,}")
print(f"计算量比例（不带 / 带）:     {flops_no_cache / flops_with_cache:.2f}x")

# 验证：随着生成长度增加，这个比例应该继续扩大（不带 cache 是 O(n^2) 级别的重复计算）
for extra_len in [32, 64, 128]:
    fnc = decode_without_cache(None, prompt_len, extra_len, d_model)
    fwc = decode_with_cache(None, prompt_len, extra_len, d_model)
    print(f"生成到长度 {extra_len:4d}：不带/带 cache 计算量比例 = {fnc / fwc:.2f}x")
```

实测输出（numpy 2.4.4）：

```
不带 KV Cache 的总乘加次数: 7,876,864
带 KV Cache 的总乘加次数:   461,568
计算量比例（不带 / 带）:     17.07x

生成到长度   32：不带/带 cache 计算量比例 = 17.07x
生成到长度   64：不带/带 cache 计算量比例 = 35.06x
生成到长度  128：不带/带 cache 计算量比例 = 72.96x
```

结果验证了预期：**序列越长，不带 cache 的重复计算问题越严重**，比例随长度增长扩大——不带 cache 每步计算量是 `O(t)`，累加是 `O(t²)`；带 cache 每步只有 `O(1)` 新投影加 `O(t)` 打分，避免不了 attention 本身，但省掉了投影上的全部重复部分，常数因子小得多。

## 7. PagedAttention：分页管理与碎片问题

传统实现里，每个请求的 KV Cache 通常按**预分配的连续显存块**存储（比如预留最大序列长度的空间）。这带来两个问题：**内部碎片**（按最大长度预分配，实际生成长度远小于最大值时大量预留空间被浪费）和**外部碎片**（不同请求实际长度不同，连续显存分配容易产生大小不一的空闲空隙，难以复用）。

**PagedAttention** 借鉴操作系统虚拟内存的分页思想：把 KV Cache 切成固定大小的"块（block）"，每个请求的 cache 由一系列逻辑块组成，物理上这些块可以分散在显存的任何位置，通过块表（block table）做逻辑到物理的映射：

```
请求 A 的逻辑 KV 序列：[block0, block1, block2, ...]
块表（block table）:
  逻辑块 0 → 物理块 17
  逻辑块 1 → 物理块 3
  逻辑块 2 → 物理块 42
```

好处：按需分配，不需要为最大长度预留空间，消除内部碎片；固定大小的块可灵活复用，显存利用率提升；相同 prefix 的请求（如共享 system prompt）可以共享物理块，进一步省显存。代价是每次 attention 需要通过块表做一次间接寻址，比连续内存访问多一层查找开销，但相比换来的显存利用率提升通常是值得的。

## 8. 连续批处理（Continuous Batching）

传统静态批处理要求同一个 batch 里所有请求**长度对齐、同时开始同时结束**——batch 里有请求提前结束时，槙位空闲浪费，要等整个 batch 跑完才能换入新请求。

**连续批处理**允许在 batch 执行过程中动态移出已完成请求、移入新到达请求，槙位不再被"对齐"绑死：

```
静态批处理：req2 第 3 步结束，但槙位空闲，等其它请求跑完才能塞新请求
连续批处理：req2 结束 → 立刻把 req5 换入同一个槙位，其它请求不受影响
```

这项技术配合 PagedAttention 效果更好：每个请求的 KV Cache 独立分页管理，换入换出请求不需要挪动其他请求的显存布局。连续批处理提升的是 **GPU 利用率**——尤其在请求生成长度差异很大的真实流量场景下收益明显。

## 9. 小结

| 主题 | 核心结论 |
| --- | --- |
| 重复计算来源 | 不缓存时每步重新计算历史 token 的 K/V 投影 |
| KV Cache 省的是什么 | 省 K/V 投影重复计算，没省 attention 打分的 `O(t)` 增长 |
| 显存公式 | `n_layers × n_heads × d_head × seq_len × batch × 2 × dtype_bytes`，序列长/batch 都线性相关 |
| Prefill 特性 | 大矩阵乘法，计算密集，GPU 算力利用率高 |
| Decode 特性 | 向量乘矩阵 + 显存搬运，带宽密集，是延迟主要瓶颈 |
| MQA/GQA | 压缩 K/V head 数（`n_heads → n_groups → 1`），压低公式头数因子 |
| PagedAttention | 分页管理 cache，消除碎片，支持前缀共享 |
| 连续批处理 | 动态换入换出请求，避免槙位空闲，提升整体吞吐 |

## 10. 延伸阅读

- 量化如何进一步压缩 KV Cache 与权重显存 → [02-量化.md](02-量化.md)
- 投机解码如何缓解 Decode 阶段的带宽瓶颈 → [04-投机解码与推理引擎.md](04-投机解码与推理引擎.md)
- self-attention 的完整推导 → [../01-Transformer原理/](../01-Transformer原理/)

## 🎬 推荐视频资源

> 以下资源均为频道 / 课程 / 官网入口级链接（已于 2026-08-04 实测可访问）。刻意不收录单个视频 ID——那类链接失效率高，且难以核实归属。
> 从入口进去按本篇主题检索，命中率比一条可能失效的直链更高。

### 📺 视频频道与课时

- [Andrej Karpathy YouTube](https://www.youtube.com/@AndrejKarpathy)
- [跟李沐学AI（B 站）](https://space.bilibili.com/1567748478)

### 🎓 系统课程与教材

- [Dive into Deep Learning（英文版）](https://d2l.ai/)

### 📖 专题图文

- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
