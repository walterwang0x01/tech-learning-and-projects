# DPO与免RL对齐

> Author: Walter Wang

> **读完你能回答的 3 个问题**
>
> 1. DPO 是怎么从 RLHF 的优化目标推导出不需要显式奖励模型的直接优化形式的？
> 2. beta 参数在 DPO 里起什么作用？
> 3. DPO 有哪些已知问题，KTO/SimPO 这类改进想解决什么？

## 1. 从 RLHF 目标出发

回顾 [RLHF全链路](03-RLHF全链路.md) 里 PPO 优化的目标：在最大化奖励的同时用 KL 惩罚约束策略不偏离参考模型太远：

```
max_π  E_{y~π(·|x)}[ r(x, y) ] - β · KL(π(·|x) || π_ref(·|x))
```

DPO（Direct Preference Optimization）的关键洞察是：**这个带 KL 约束的奖励最大化问题存在解析解**，能直接推导出最优策略 `π*` 和奖励函数 `r` 之间的关系，不需要真正跑强化学习去逼近这个解。

## 2. 关键推导步骤

**第一步：写出目标对应的最优策略形式。**

上面这个"带 KL 正则的奖励最大化"问题，其最优解在理论上有闭式形式：

```
π*(y|x) = (1 / Z(x)) · π_ref(y|x) · exp( r(x,y) / β )

其中 Z(x) = Σ_y π_ref(y|x) · exp(r(x,y)/β)   是归一化常数（对所有可能回答y求和）
```

这个式子说的是：最优策略相对参考策略做了一次"指数倾斜（exponential tilting）"——奖励高的回答概率被放大，奖励低的被压低，倾斜幅度由 `β` 控制，`Z(x)` 只是保证概率归一化，只依赖 prompt `x`。

**第二步：反解出奖励函数用策略表示。**

对上式做代数变形，用最优策略 `π*` 反过来表示奖励函数：

```
两边取对数：
  log π*(y|x) = log π_ref(y|x) + r(x,y)/β - log Z(x)

整理得到：
  r(x,y) = β · log( π*(y|x) / π_ref(y|x) ) + β · log Z(x)
```

这一步是整个推导的核心转折：**奖励函数可以完全用策略（当前策略和参考策略的比值）来表达**，不再需要独立的奖励模型。`log Z(x)` 只依赖 `x`，不依赖具体回答 `y`。

**第三步：代入 Bradley-Terry 偏好模型，消去 `Z(x)`。**

回顾 [RLHF全链路](03-RLHF全链路.md) 第 2 节的 Bradley-Terry 假设：`y_win` 优于 `y_lose` 的概率是两者奖励差值的 sigmoid：

```
P(y_win ≻ y_lose | x) = σ( r(x, y_win) - r(x, y_lose) )
```

把第二步的 `r(x,y)` 表达式代入这个差值：

```
r(x, y_win) - r(x, y_lose)
  = [β·log(π*(y_win|x)/π_ref(y_win|x)) + β·log Z(x)]
  - [β·log(π*(y_lose|x)/π_ref(y_lose|x)) + β·log Z(x)]
  = β · [ log(π*(y_win|x)/π_ref(y_win|x)) - log(π*(y_lose|x)/π_ref(y_lose|x)) ]
```

**关键之处**：两个 `log Z(x)` 项完全抵消——因为 `y_win` 和 `y_lose` 用的是同一个 `x`，`Z(x)` 只依赖 `x`，做差后自然消去。这意味着偏好概率完全不依赖那个难以计算的归一化常数，也不需要显式算出 `r(x,y)` 这个中间量。

**第四步：写出 DPO 的最终损失函数。**

把消去 `Z(x)` 后的差值代入 Bradley-Terry 的负对数似然，直接得到一个可以对策略参数 `θ` 求梯度、用标准梯度下降训练的损失函数：

```
L_DPO(θ) = - log σ( β·log(π_θ(y_win|x)/π_ref(y_win|x)) - β·log(π_θ(y_lose|x)/π_ref(y_lose|x)) )
```

这个损失里只出现了策略模型 `π_θ`（要训练的模型）和参考模型 `π_ref`（冻结，通常就是SFT模型），两者都可以直接算出对数概率，不再需要奖励模型、不再需要采样生成、不再需要强化学习的训练循环。

## 3. 为什么不再需要显式奖励模型

把 RLHF 和 DPO 的训练流程摆在一起看差异非常直观：

```
RLHF: 偏好数据 → 训练奖励模型 → 用奖励模型 + PPO 强化学习循环去优化策略
      (需要：奖励模型+Actor+Critic+Reference，四个模型，采样生成+打分+策略梯度)

DPO:  偏好数据 → 直接对策略模型和参考模型的对数概率做梯度下降
      (需要：策略模型+参考模型，两个模型，标准的监督式梯度下降)
```

第 2 节的推导已说明原因：奖励函数在数学上被重新表达成了"当前策略和参考策略的对数概率比值"，这个量可以直接从语言模型的输出算出（每个token对数概率之和），不需要单独训练一个模型去近似它。DPO 把强化学习问题转化成了形式上类似监督学习的分类问题——损失函数长得很像二分类交叉熵，只是"分类"的对象是"哪个回答更受偏好"。

## 4. beta 参数的作用

`β` 在原始 RLHF 目标里是 KL 惩罚的强度；在 DPO 损失函数里，它变成了控制 `log π_θ/π_ref` 这个比值在损失里的放大程度的系数。

- `β` 越小：损失函数对"策略偏离参考模型的程度"越不敏感，允许策略在偏好方向上做更激进调整，风险是更容易偏离参考模型的合理分布
- `β` 越大：损失函数对偏离参考模型的惩罚越强，策略调整更保守，更贴近参考模型原始行为，学到新偏好的速度和幅度也更受限制

这与 RLHF 里 `β` 的直觉一致——本来就是同一个正则化系数，只是在 DPO 里不需要通过强化学习中间步骤体现，而是直接出现在封闭形式的损失函数里，这也是 DPO 相比 RLHF 更容易调试的原因：少了强化学习训练过程的方差和不稳定性，`β` 的效果更直接、更可预测。

## 5. DPO 的已知问题

**对分布外数据（OOD）的表现**：DPO 的推导基于参考模型给出的分布作为基准，训练数据里的偏好对通常来自参考模型本身或与其接近的模型采样得到的回答。当推理时的输入明显超出训练分布覆盖范围时，DPO 学到的偏好方向的可靠性会下降——它本质是在参考模型已能生成的候选里做"重新加权"，而非学习全新生成能力。

**降低选中回答概率的现象**：直觉上应期望训练后 win 概率上升、lose 概率下降。但实践中观察到反直觉现象：DPO 训练有时会让 win 的绝对概率也一起下降，只是降幅比 lose 小，维持"相对"偏好差距扩大，但两者绝对概率都在下降。这是因为 DPO 损失只约束两者的**差值**方向，没有约束哪一方绝对概率必须上升。

> ⚠️ 待确认：这一现象的具体成因和影响程度在不同研究里有差异，此处只描述现象本身，不列具体数值。

## 6. KTO / ORPO / SimPO 的改进思路

**KTO（Kahneman-Tversky Optimization）**：DPO 需要成对偏好数据（同一 prompt 下明确的 win/lose 对比），但很多真实场景只有单条回答的"好/不好"二元反馈。KTO 借鉴行为经济学中"收益/损失"感知不对称的理论，直接用非成对二元反馈优化，不要求数据构造成严格的比较对。

**ORPO（Odds Ratio Preference Optimization）**：DPO 依赖独立训练好的 SFT 模型作参考模型，相当于先做 SFT 再做 DPO，两阶段分开训练。ORPO 把 SFT 目标和偏好优化目标合并到同一训练阶段，用几率比（odds ratio）惩罚项在做常规 SFT 时引入偏好信号，减少训练阶段数。

**SimPO（Simple Preference Optimization）**：DPO 损失需要参考模型计算对数概率比值，训练时要同时保留两份前向计算。SimPO 去掉对参考模型的依赖，直接用策略模型自身回答的长度归一化平均对数概率作隐式奖励信号，简化训练流程和显存开销。

> ⚠️ 待确认：以上三种方法的具体损失函数形式和相对效果差异仍在持续演进，此处只描述改进动机，不列具体数值。

## 7. 如何选择 RLHF 还是 DPO

| 考虑维度 | 倾向 RLHF | 倾向 DPO |
| --- | --- | --- |
| 工程复杂度 | 有成熟强化学习训练基础设施 | 希望用标准监督学习流程降低门槛 |
| 数据形式 | 能持续收集在线偏好反馈 | 已有静态成对偏好数据集，离线训练 |
| 显存/算力 | 预算充足，能同时维护四个模型 | 资源有限，只维护策略+参考两个模型 |
| 训练稳定性 | 能承受强化学习波动并投入调试 | 希望更接近监督学习的可预测性 |
| 在线探索 | 采样-打分循环天然支持探索新生成方式 | 更依赖已有偏好数据覆盖的回答分布 |

实践中的常见思路：DPO 因工程简单、训练稳定，往往是更实用的默认起点；如果对齐效果天花板不够，或需要模型持续通过在线反馈自我提升，才考虑投入更复杂的 RLHF 流程。这不是绝对规则，具体选择取决于团队的数据、资源和目标。

## 8. 用 NumPy 实现 DPO Loss 并验证偏好方向

用 NumPy 实现 DPO 的损失函数：给定策略模型和参考模型对 win/lose 回答的对数概率，计算 DPO loss 及梯度，验证训练后策略模型学会了让偏好回答的相对概率优势扩大。

```python
import numpy as np


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def dpo_loss_and_grad(logp_win, logp_lose, ref_logp_win, ref_logp_lose, beta):
    """
    计算一个 batch 的 DPO 损失，及对 (logp_win, logp_lose) 的梯度。
    logp_*：策略模型对数概率 log π_θ(y|x)，可训练
    ref_logp_*：参考模型对数概率 log π_ref(y|x)，冻结
    """
    # 策略与参考模型的对数概率比值差，对应推导中消去 log Z(x) 后的核心量
    logits = beta * ((logp_win - ref_logp_win) - (logp_lose - ref_logp_lose))

    probs_correct = sigmoid(logits)
    loss = -np.mean(np.log(np.clip(probs_correct, 1e-12, 1.0)))

    # d(loss)/d(logits) = probs_correct - 1
    grad_logits = (probs_correct - 1.0) * beta
    grad_logp_win = grad_logits
    grad_logp_lose = -grad_logits

    return loss, grad_logp_win / beta, grad_logp_lose / beta, probs_correct


def train_dpo_step(logp_win, logp_lose, ref_logp_win, ref_logp_lose, beta, lr, n_steps=40):
    """用梯度下降模拟策略模型对数概率在 DPO loss 下的更新轨迹"""
    logp_win = logp_win.copy()
    logp_lose = logp_lose.copy()
    history = []

    for step in range(n_steps):
        loss, grad_win, grad_lose, _ = dpo_loss_and_grad(
            logp_win, logp_lose, ref_logp_win, ref_logp_lose, beta
        )
        logp_win -= lr * grad_win
        logp_lose -= lr * grad_lose
        if step % 10 == 0 or step == n_steps - 1:
            history.append((step, float(loss)))

    return logp_win, logp_lose, history


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    n_pairs = 6
    beta = 0.1

    ref_logp_win = rng.uniform(-3.0, -1.0, size=n_pairs)
    ref_logp_lose = rng.uniform(-3.0, -1.0, size=n_pairs)
    logp_win = ref_logp_win.copy()
    logp_lose = ref_logp_lose.copy()

    print(f"beta = {beta}")
    print("训练前 - 策略与参考模型相同:")
    print(f"  logp_win  = {np.round(logp_win, 3)}")
    print(f"  logp_lose = {np.round(logp_lose, 3)}")

    initial_loss, _, _, initial_probs = dpo_loss_and_grad(
        logp_win, logp_lose, ref_logp_win, ref_logp_lose, beta
    )
    print(f"  初始 loss = {initial_loss:.4f}, 初始判断win更优的概率均值 = {np.mean(initial_probs):.4f}")

    final_win, final_lose, history = train_dpo_step(
        logp_win, logp_lose, ref_logp_win, ref_logp_lose, beta, lr=0.1, n_steps=40
    )

    print("\n训练过程 loss:")
    for step, loss in history:
        print(f"  step {step:3d}: loss = {loss:.4f}")

    final_loss, _, _, final_probs = dpo_loss_and_grad(
        final_win, final_lose, ref_logp_win, ref_logp_lose, beta
    )
    print(f"\n训练后 logp_win  = {np.round(final_win, 3)}")
    print(f"训练后 logp_lose = {np.round(final_lose, 3)}")
    print(f"训练后判断win更优的概率均值 = {np.mean(final_probs):.4f}")

    win_shift = final_win - ref_logp_win
    lose_shift = final_lose - ref_logp_lose
    print(f"\nwin相对参考模型的对数概率变化: {np.round(win_shift, 3)}")
    print(f"lose相对参考模型的对数概率变化: {np.round(lose_shift, 3)}")
    print(f"win的相对变化是否系统性高于lose: {np.all(win_shift > lose_shift)}")
```

实测输出（numpy 2.4.4）：

```
beta = 0.1
训练前 - 策略与参考模型相同:
  logp_win  = [-1.75  -1.206 -1.449 -2.55  -2.4   -1.253]
  logp_lose = [-2.989 -1.358 -1.406 -2.064 -2.394 -2.443]
  初始 loss = 0.6931, 初始判断win更优的概率均值 = 0.5000

训练过程 loss:
  step   0: loss = 0.6931
  step  10: loss = 0.6455
  step  20: loss = 0.6023
  step  30: loss = 0.5632
  step  39: loss = 0.5312

训练后 logp_win  = [ 0.068  0.612  0.369 -0.732 -0.582  0.565]
训练后 logp_lose = [-4.807 -3.175 -3.224 -3.882 -4.212 -4.261]
训练后判断win更优的概率均值 = 0.5899

win相对参考模型的对数概率变化: [1.818 1.818 1.818 1.818 1.818 1.818]
lose相对参考模型的对数概率变化: [-1.818 -1.818 -1.818 -1.818 -1.818 -1.818]
win的相对变化是否系统性高于lose: True
```

初始时策略等于参考模型，loss 恰好是 `-log(0.5) ≈ 0.693`（"完全不知道哪个更好"）；训练 40 步后 loss 降到 0.53，判断 win 更优的概率均值从 0.5 升到 0.59。观察相对参考模型的对数概率变化：win 统一上升 1.818，lose 统一下降 1.818——两者变化量精确对称，这正是 DPO 只约束"相对差值"的直接体现：`beta` 和梯度结构对 win/lose 完全对称，优化不单独控制某一方的绝对走向，只保证差值朝偏好方向扩大，验证了第 5 节"DPO 只保证相对偏好方向，不直接约束绝对概率走向"这一机制。

> ⚠️ 这里的 `logp_win`/`logp_lose` 是简化 toy 变量，没做"对数概率必须 ≤ 0"这类合法性约束，训练后 `logp_win` 出现正值在真实语言模型里不可能出现。这个简化模型只演示 DPO 梯度更新的方向性机制，不代表真实概率数值；真实训练中 `logp` 来自模型对 token 序列对数概率的求和，天然满足 ≤ 0。

## 9. 小结

| 概念 | 一句话总结 |
| --- | --- |
| 推导起点 | RLHF 带 KL 约束的奖励最大化问题存在解析最优策略形式 |
| 关键代换 | 奖励函数可用策略与参考模型的对数概率比值表示 |
| 消去 Z(x) | 偏好差值中归一化常数抵消，不再需要显式计算 |
| 免奖励模型 | 偏好概率直接由策略和参考模型对数概率算出，无需单独训练RM |
| beta | 控制偏离参考模型的惩罚强度，与RLHF里KL系数含义一致 |
| 已知问题 | 对分布外数据可靠性下降；可能出现win/lose绝对概率一起下降的现象 |
| KTO/ORPO/SimPO | 分别解决非成对数据、两阶段训练、依赖参考模型三个不同痛点 |
| 选择依据 | 工程复杂度、数据形式、显存预算、是否需要在线探索 |

## 10. 延伸阅读

- RLHF 完整链路与 KL 惩罚原始形式 → [RLHF全链路](03-RLHF全链路.md)
- SFT 阶段如何为 DPO 提供参考模型 → [三阶段范式与数据构造](01-三阶段范式与数据构造.md)
- PEFT 降低 DPO 训练显存开销 → [PEFT参数高效微调](02-PEFT参数高效微调.md)
- 大模型使用视角基础概念 → [大语言模型基础](../../ai-agent/00-基础概念/02-大语言模型基础.md)

## 🎬 推荐视频资源

> 以下资源均为频道 / 课程 / 官网入口级链接（已于 2026-08-04 实测可访问）。刻意不收录单个视频 ID——那类链接失效率高，且难以核实归属。
> 从入口进去按本篇主题检索，命中率比一条可能失效的直链更高。

### 🎓 系统课程与教材

- [OpenAI Spinning Up in Deep RL](https://spinningup.openai.com/en/latest/)

### 📖 专题图文

- [RLHF Book（在线书）](https://rlhfbook.com/)
- [Hugging Face - RLHF 图解](https://huggingface.co/blog/rlhf)
