# VLM 架构

> Author: Walter Wang

> **读完你能回答的 3 个问题**
>
> 1. 视觉编码器、连接器、LLM 三段式里，连接器到底在解决什么问题？
> 2. Q-Former 和线性投影两种连接器路线，各自在什么场景下更划算？
> 3. 视觉幻觉（visual hallucination）的根本原因是什么，和文本幻觉是同一类问题吗？

## 1. 三段式结构：视觉编码器 + 连接器 + LLM

主流 VLM（Vision-Language Model）的结构可以拆成三段，各自职责边界清晰：

```
图像 → [视觉编码器] → 视觉特征 → [连接器] → 视觉 token → [LLM] → 文本输出
        (如 ViT)                 (Connector)              (如 Llama/Qwen)
```

- **视觉编码器**：把像素转成一组特征向量，通常直接复用预训练好的 ViT（参考 [../../machine-learning/06-CNN与视觉/03-ViT与视觉Transformer.md](../../machine-learning/06-CNN与视觉/03-ViT与视觉Transformer.md)），或复用 CLIP 的视觉塔（参考 [./01-CLIP与对比学习.md](./01-CLIP与对比学习.md)）——CLIP 视觉编码器已在海量图文对上学过"图像里哪些特征和语言语义相关"，比从头训练的纯视觉编码器更适合接到语言模型上。
- **LLM**：负责语言理解和生成，通常直接复用预训练好的纯文本 LLM。
- **连接器（Connector）**：三段式里真正需要针对多模态设计的部分，解决**视觉特征空间和 LLM 输入空间（词嵌入空间）维度不同、分布不同**的对接问题。

这个"缝合"式设计能奏效的本质原因和 CLIP 零样本分类能工作的原因类似（参考 [./01-CLIP与对比学习.md](./01-CLIP与对比学习.md) 第5节）：两段预训练好的模型已分别学到丰富的模态表示，多模态训练只需学一个较小的桥接模块重新组合已有能力，不必重新学习语言或视觉本身，这也是 VLM 训练成本远低于从头预训练同等能力纯语言模型的原因。

## 2. 连接器三路线对比

### 2.1 线性/MLP 投影

最简单的做法：视觉编码器输出的每个 patch 特征，独立过一个线性层（或两层 MLP），把维度从 `vision_dim` 投影到 `llm_dim`，然后**逐 token 拼接**进 LLM 的输入序列。

```
视觉特征: [v1, v2, ..., vN]  (每个 vi 维度 = vision_dim)
线性投影:  vi' = W @ vi + b   (维度 = llm_dim)
拼接进 LLM 输入: [text_tokens..., v1', v2', ..., vN', text_tokens...]
```

**优点**：结构最简单，参数量最小，训练最容易收敛，语义信息几乎无损。**代价**：视觉 token 数量等于输入 patch 数量，分辨率越高、token 越多，直接推高 LLM 的上下文长度和推理成本。

### 2.2 Q-Former（Query-based Transformer）

Q-Former 引入一组**固定数量、可学习的 query 向量**，通过 cross-attention 从视觉特征里"抽取"信息，输出的 token 数量由 query 数量决定，**与输入图像分辨率无关**。

```
可学习 queries: [q1, ..., qK]   (K 是固定超参数，如 32 或 64)
Cross-Attention: Query=queries, Key/Value=视觉特征
输出: K 个融合后的 token，K 与视觉 patch 数量 N 无关（无论 N 是 256 还是 4096）
```

**优点**：把视觉信息压缩到固定长度，占用的 LLM 上下文不随分辨率变化，对高分辨率、多图、视频场景友好。**代价**：压缩必然有信息损失，K 越小损失越大，细粒度视觉细节更容易丢失；同时结构本身参数更多，训练成本比线性投影高。

### 2.3 Cross-Attention 连接器

不改变视觉 token 的数量表示形式，而是**在 LLM 内部插入 cross-attention 子层**：文本侧的隐状态作为 Query，视觉特征作为 Key/Value，视觉信息不进入 LLM 的输入 token 序列，而是在每一层（或部分层）通过注意力"旁路"注入。

```
LLM 第 l 层: hidden = SelfAttn(hidden)
             hidden = hidden + CrossAttn(Query=hidden, Key/Value=视觉特征)
             hidden = FFN(hidden)
```

**优点**：视觉特征不占用输入序列长度，不受视觉 token 数挤占；且每层都能重新访问原始视觉特征，不像前两种方案那样信息只在输入层注入一次、随层数加深被逐渐稀释。**代价**：需要修改 LLM 内部结构，不能直接复用未改造的纯文本权重前向，架构改动更大，通常需要更大规模数据重新训练这部分新增参数。

### 2.4 三路线权衡小结

```
                token数量        对LLM改动      信息损失      典型代价
线性/MLP        随分辨率增长      无需改动        最小          上下文预算被挤占
Q-Former        固定，与分辨率无关 无需改动        较大（压缩）   细粒度细节易丢失
Cross-Attention 不占用输入序列    需要改内部结构   较小          需要更大训练成本
```

没有绝对最优，选择取决于场景：单图、需要精细定位的任务（如文档理解、图表读取）偏好线性投影保留细节；多图、视频、长上下文场景偏好 Q-Former 或 cross-attention 压缩视觉 token 占用。

## 3. 视觉 token 数对上下文和成本的影响

视觉 token 一旦进入 LLM 的输入序列，就要和文本 token 一起被 self-attention 处理，代价是二次方增长的注意力计算量（参考 [../01-Transformer原理/01-注意力机制推导.md](../01-Transformer原理/01-注意力机制推导.md)），推理时同样要写入 KV Cache（参考 [../05-推理优化/01-KV-Cache与显存分析.md](../05-推理优化/01-KV-Cache与显存分析.md)）——高分辨率图切出的视觉 token 可能比一整段文本 prompt 还多，直接推高显存占用和延迟。这也是为什么"视觉 token 数量"是 VLM 工程里持续被优化的指标。

## 4. 高分辨率切图（Tiling）

原生 ViT 训练时的输入分辨率通常是固定的（如 336×336），直接把高分辨率图像缩放到这个尺寸会丢失细节（小字文档、密集图表尤其明显）。高分辨率切图（tiling / AnyRes）的思路是：**把大图切成多个固定尺寸的小块，每块独立过一次视觉编码器，再把所有块的视觉 token 拼在一起，外加一个整图缩略图提供全局上下文**。

```
原图（如 1008x1008）
  ├─ 切成 3x3 = 9 个 336x336 的 tile，每个独立编码
  ├─ 额外加一张整图缩略图（提供全局构图信息，弥补切块丢失的整体关系）
  └─ 拼接：[缩略图token, tile1 token, tile2 token, ..., tile9 token]
```

代价直接且线性：tile 数量翻倍，视觉 token 数量也大致翻倍——这正是实验3要验证的部分。分辨率越高，收益（细节保留）和成本（token 数、连接器计算量）同步上升，没有免费的午餐。

## 5. 两阶段训练与冻结/解冻选择

VLM 训练通常分两阶段，核心矛盾是：**连接器是随机初始化的，需要学习；但视觉编码器和 LLM 都是预训练好的，一开始就用大量新数据联合训练容易把已学到的能力冲坏（灾难性遗忘）**。

```
阶段1：对齐预训练（Alignment Pretraining）
  冻结视觉编码器 + 冻结（或部分冻结）LLM，只训练连接器
  目标：让连接器学会把视觉特征"翻译"成 LLM 能理解的表示
  数据：大量粗粒度图文对（图片+简单描述），规模大、质量要求相对低

阶段2：指令微调（Instruction Tuning）
  解冻 LLM（连接器继续训练，视觉编码器视情况解冻或保持冻结）
  目标：学会遵循复杂指令、做视觉问答、多轮对话
  数据：精细标注的图文指令数据，规模小、质量要求高
```

**冻结/解冻的权衡**：视觉编码器通常倾向于冻结或只做轻量微调——它已从海量图文对学到通用视觉语义，重新解冻训练容易在小规模指令数据上过拟合；LLM 阶段1冻结、阶段2解冻是常见选择，阶段1数据质量参差不齐，直接暴露 LLM 风险较高，阶段2数据经过筛选，解冻后 LLM 才能学会真正结合视觉信息推理；连接器全程训练，因为它是新引入、没有预训练先验的模块。

## 6. 视觉幻觉的成因

视觉幻觉（visual hallucination）指模型描述图像中不存在的物体、关系或属性。几个结构性原因：

```
1. 压缩损失
   Q-Former 等压缩式连接器丢弃细节后，LLM 拿到的是"模糊"的视觉信息，
   容易用语言模型自身的先验知识"猜"而不是"看"

2. 语言先验过强
   LLM 部分预训练时学到的世界知识（如"厨房里通常有冰箱"）在推理时
   会和视觉证据竞争，视觉证据弱时语言先验会主导输出，生成语言上
   "合理"但图像里不存在的内容

3. 视觉token在深层被稀释
   线性投影和大多数 Q-Former 方案里，视觉token只在输入层注入一次，
   随着 LLM 层数加深、后续文本token不断累积，早期注入的视觉信息
   在自注意力权重分布中占比相对下降

4. 训练数据里的图文不完全对应
   预训练图文对本身存在描述不准确、过度泛化的情况，模型学到的
   "图文关联"带有噪声
```

这和纯文本 LLM 的幻觉（编造不存在的事实）是同一类问题在不同模态上的表现：本质都是生成过程依赖参数化知识和局部上下文统计规律，而非对事实/证据的显式校验。第3点是 cross-attention 连接器相对线性/Q-Former 路线的潜在优势——每层重新访问原始视觉特征能缓解稀释问题，但无法根除幻觉，因为压缩损失和语言先验过强依然存在。

## 7. 原生多模态 vs 拼接式

三段式（视觉编码器 + 连接器 + LLM，且三部分权重来源不同、分阶段训练）常被称为"拼接式"（modular / stitched）多模态架构，是目前工程上最主流、成本最低的路线，因为可以复用现成的预训练视觉模型和语言模型。

"原生多模态"（natively multimodal）指的是从预训练最早期就把多种模态数据混合在同一个模型里从头训练，不存在"先训练好的纯视觉/纯文本模型再拼接"这个阶段。

```
拼接式：       [预训练好的视觉模型] + [连接器] + [预训练好的LLM]
              分阶段训练，可复用现成权重，训练成本低

原生多模态：   从随机初始化开始，图像/文本/音频等模态数据从第一步起
              就混合参与同一套预训练，不存在单独的"视觉专家模块"拼接阶段
```

> ⚠️ 待确认：原生多模态是否仍存在某种模态专属编码/分词层（如图像 patch 化、音频离散化），以及两种设计间是否存在更细的中间形态，业界实现和命名并不统一，这里只呈现核心区别，不对具体模型架构下判断。

拼接式的核心权衡是"训练成本低、复用现成能力"换来"模态间融合终究是后天缝合，存在结构性的信息传递瓶颈（连接器）"；原生多模态希望通过从头联合训练获得更深层的跨模态表示，但训练成本和数据规模要求也随之大幅提高。

## 8. 代码：三种连接器参数量与视觉 token 数对比

用 numpy 估算线性投影、Q-Former、cross-attention 三种连接器在同一维度设定下的参数量级，以及高分辨率切图对视觉 token 数的影响。

```python
import numpy as np

rng = np.random.default_rng(0)


def linear_mlp_connector_params(vision_dim, llm_dim, hidden=None):
    """线性/MLP 连接器参数量：把每个视觉 token 的维度从 vision_dim 投影到 llm_dim
    线性版本只有一个矩阵；MLP 版本中间加一层 hidden，用 GELU 类激活（这里只算参数量不跑激活）"""
    linear_params = vision_dim * llm_dim + llm_dim  # W + bias
    if hidden is None:
        return linear_params, None
    mlp_params = (vision_dim * hidden + hidden) + (hidden * llm_dim + llm_dim)
    return linear_params, mlp_params


def qformer_params(vision_dim, llm_dim, num_queries, num_layers, num_heads):
    """Q-Former 连接器参数量估算：num_queries 个可学习 query 向量做 cross-attention
    从视觉特征里抽取信息，输出固定数量的 token（与输入视觉 token 数无关）
    每层包含：self-attn(Q/K/V/O) + cross-attn(Q/K/V/O) + FFN"""
    d = llm_dim
    learnable_queries = num_queries * d
    per_layer = (
        4 * d * d            # self-attention 的 Q,K,V,O 四个投影矩阵
        + 4 * d * vision_dim  # cross-attention：Q 用 d 维，K/V 来自视觉特征 vision_dim 维，O 回到 d 维（近似）
        + 2 * d * (4 * d)    # FFN 两层，中间维度取 4d
    )
    return learnable_queries + per_layer * num_layers


def cross_attention_connector_params(vision_dim, llm_dim, num_layers):
    """Cross-attention 连接器：不改变视觉 token 数量，而是在 LLM 每层（或部分层）
    插入 cross-attention 子层，用文本侧做 Query，视觉特征做 Key/Value
    这里估算插入 num_layers 层所需的新增参数（Q/K/V/O 四个投影）"""
    d = llm_dim
    per_layer = d * d + 2 * (vision_dim * d) + d * d  # Q(d->d) + K,V(vision_dim->d) + O(d->d)
    return per_layer * num_layers


def visual_token_count(image_size, patch_size, tiles=1):
    """视觉 token 数：(image_size/patch_size)^2 每个 tile，高分辨率切图会产生多个 tile
    tiles=1 是原图整体过一次编码器；tiles>1 是切成多块再各自编码（token 数线性增长）"""
    per_tile = (image_size // patch_size) ** 2
    return per_tile * tiles


# --- 实验1：三种连接器的参数量对比 ---
vision_dim = 1024   # 视觉编码器输出维度（如 ViT-L 的 hidden size 量级）
llm_dim = 4096       # LLM hidden size 量级
num_vision_tokens = 576  # 例如 24x24 patch 网格

linear_p, mlp_p = linear_mlp_connector_params(vision_dim, llm_dim, hidden=4096)
qformer_p = qformer_params(vision_dim, llm_dim, num_queries=32, num_layers=6, num_heads=8)
cross_attn_p = cross_attention_connector_params(vision_dim, llm_dim, num_layers=12)

print("实验1：三种连接器架构的参数量对比（同一 vision_dim/llm_dim 设定下）")
print(f"  线性投影(Linear)      参数量 ≈ {linear_p:>12,}")
print(f"  MLP(2层)              参数量 ≈ {mlp_p:>12,}")
print(f"  Q-Former(6层,32query) 参数量 ≈ {qformer_p:>12,}")
print(f"  Cross-Attention(12层) 参数量 ≈ {cross_attn_p:>12,}")

# --- 实验2：连接器对"送入 LLM 的视觉 token 数"的影响 ---
print("\n实验2：三种连接器路线对送入 LLM 的视觉 token 数量的影响")
print(f"  原始视觉 token 数（如 24x24 patch）= {num_vision_tokens}")
print(f"  线性/MLP 路线：逐 token 投影，token 数量不变 → 送入 LLM {num_vision_tokens} 个 token")
print(f"  Q-Former 路线：num_queries 个可学习 query 压缩 → 送入 LLM 32 个 token（与输入无关，固定）")
print("  Cross-Attention 路线：视觉特征留在 K/V 侧，不占用 LLM 的输入 token 序列长度 → 送入 LLM 0 个额外 token")

# --- 实验3：高分辨率切图对 token 数和线性投影连接器计算量的影响 ---
print("\n实验3：高分辨率切图（tiling）对视觉 token 数的影响（patch_size=14 固定）")
for image_size, tiles in [(336, 1), (336, 1), (672, 4), (1008, 9)]:
    tok = visual_token_count(image_size, patch_size=14, tiles=tiles)
    flops_linear = tok * vision_dim * llm_dim  # 线性连接器对 token 数是线性开销
    print(f"  image_size={image_size:<5} tiles={tiles:<2} → token数={tok:<6} 线性连接器乘加量≈{flops_linear:,}")
```

实测输出（numpy 2.4.4）：

```
实验1：三种连接器架构的参数量对比（同一 vision_dim/llm_dim 设定下）
  线性投影(Linear)      参数量 ≈    4,198,400
  MLP(2层)              参数量 ≈   20,979,712
  Q-Former(6层,32query) 参数量 ≈ 1,308,753,920
  Cross-Attention(12层) 参数量 ≈  503,316,480

实验2：三种连接器路线对送入 LLM 的视觉 token 数量的影响
  原始视觉 token 数（如 24x24 patch）= 576
  线性/MLP 路线：逐 token 投影，token 数量不变 → 送入 LLM 576 个 token
  Q-Former 路线：num_queries 个可学习 query 压缩 → 送入 LLM 32 个 token（与输入无关，固定）
  Cross-Attention 路线：视觉特征留在 K/V 侧，不占用 LLM 的输入 token 序列长度 → 送入 LLM 0 个额外 token

实验3：高分辨率切图（tiling）对视觉 token 数的影响（patch_size=14 固定）
  image_size=336   tiles=1  → token数=576    线性连接器乘加量≈2,415,919,104
  image_size=336   tiles=1  → token数=576    线性连接器乘加量≈2,415,919,104
  image_size=672   tiles=4  → token数=9216   线性连接器乘加量≈38,654,705,664
  image_size=1008  tiles=9  → token数=46656  线性连接器乘加量≈195,689,447,424
```

结果印证了第2节的权衡：线性投影参数量最小（约420万），但视觉 token 数随分辨率/tile 数线性增长，9 个 tile 时 token 数从 576 暴涨到 46656，连接器计算量同步暴涨；Q-Former 和 cross-attention 结构本身参数量远大于线性投影（多头注意力和 FFN 带来更多矩阵），但换来的是视觉 token 数量与分辨率解耦——Q-Former 恒定输出 32 个 token，cross-attention 甚至不占用输入序列长度。这正是"参数量小但token开销随分辨率暴涨"与"参数量大但token开销恒定"之间的直接权衡，没有免费的选择。

## 9. 小结

| 主题 | 核心结论 |
| --- | --- |
| 三段式结构 | 视觉编码器+连接器+LLM，两端复用预训练权重，连接器是唯一需要新学的桥接模块 |
| 线性/MLP 连接器 | 参数量最小、信息损失最小，但视觉 token 数随分辨率线性增长，挤占上下文 |
| Q-Former | 固定数量 query 压缩视觉信息，token 数与分辨率无关，代价是细节损失 |
| Cross-Attention | 视觉信息不占用输入序列，每层可重新访问，但需要改动 LLM 内部结构 |
| 高分辨率切图 | 切块+缩略图保留细节，token 数随 tile 数线性增长，没有免费的午餐 |
| 两阶段训练 | 阶段1对齐（冻结两端只训连接器），阶段2指令微调（解冻LLM学会遵循指令） |
| 视觉幻觉 | 压缩损失+语言先验过强+视觉信息层间稀释+训练数据噪声共同导致 |
| 拼接式 vs 原生 | 拼接式复用现成权重成本低，原生多模态从头联合训练但成本更高 |

## 10. 延伸阅读

- CLIP 视觉编码器为何适合接入 VLM → [./01-CLIP与对比学习.md](./01-CLIP与对比学习.md)
- 注意力机制与 cross-attention 基础 → [../01-Transformer原理/01-注意力机制推导.md](../01-Transformer原理/01-注意力机制推导.md)
- 视觉 token 序列长度对 KV Cache 和显存的影响 → [../05-推理优化/01-KV-Cache与显存分析.md](../05-推理优化/01-KV-Cache与显存分析.md)
- ViT 如何把图像切成 patch token → [../../machine-learning/06-CNN与视觉/03-ViT与视觉Transformer.md](../../machine-learning/06-CNN与视觉/03-ViT与视觉Transformer.md)
