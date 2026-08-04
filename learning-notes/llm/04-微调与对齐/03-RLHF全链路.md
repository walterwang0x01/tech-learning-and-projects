# RLHF全链路

> Author: Walter Wang

> **读完你能回答的 3 个问题**
>
> 1. SFT 已经能让模型学会对话格式了，为什么还需要 RLHF？
> 2. RLHF 里的 actor、critic、reward、reference 四个模型分别扮演什么角色？
> 3. 为什么必须加 KL 惩罚，没有它会出现什么问题？

## 1. 为什么 SFT 不够

SFT 教模型"模仿"人写的高质量回复，本质是一种监督学习：给定输入，让模型输出尽量接近示范答案。但这里有一个结构性局限：**SFT 只能教会模型"复述"人类写好的答案，没法教会模型判断"两个不同的回答哪个更好"**。

真实场景里，"好回答"往往不是唯一的——同一个问题可能有多种合理的回答方式，很难为每种情况都写标准示范；而且有些质量维度（比如"更有帮助但不啰嗦"）很难通过单一示范样本教会，更容易通过"比较"来表达：给模型看两个回答，告诉它哪个更符合期望，这种相对判断的标注成本更低，也更能捕捉细腻的偏好差异。RLHF（Reinforcement Learning from Human Feedback）就是把这种"比较"信号转化成训练信号的机制，在 SFT 基础上进一步用人类偏好调整模型行为。

## 2. 奖励模型：Bradley-Terry 偏好建模

RLHF 的第一步是训练一个**奖励模型（Reward Model, RM）**，把"人类更喜欢哪个回答"这种比较判断转化成一个可以打分的函数。

标注数据的形式是：给定同一个 prompt，模型生成两个（或更多）候选回答，人类标注者判断哪个更好，得到一个偏好对 `(prompt, 回答_win, 回答_lose)`。

**Bradley-Terry 模型**假设：一个回答被判定为"更好"的概率，取决于两个回答的潜在分数（reward）之差，通过 sigmoid 函数转化成概率：

```
P(y_win 优于 y_lose | x) = σ(r(x, y_win) - r(x, y_lose))

其中 σ(z) = 1 / (1 + e^(-z))  是 sigmoid 函数
     r(x, y) 是奖励模型对 (prompt x, 回答 y) 打的分数
```

直觉理解：两个回答的奖励分数差得越大，其中分高的那个被判定为更好的概率就越接近 1；分数越接近，判断的置信度也越接近 50%——这和分数差异的直觉是一致的。

**训练目标**：让奖励模型对人类标注为"更好"的回答打出更高分数。基于 Bradley-Terry 假设，损失函数是负对数似然：

```
L(θ) = - log σ(r_θ(x, y_win) - r_θ(x, y_lose))
```

最小化这个损失，等价于让 `r(x, y_win) - r(x, y_lose)` 尽量大（在 sigmoid 意义下逼近判断正确）。训练完成后，奖励模型可以对任意一个 `(prompt, 回答)` 打出标量分数，即使这个回答从未在训练数据里出现过——这正是它有用的地方：把有限的人工比较标注,泛化成一个能在训练循环里反复调用、给任意新生成回答打分的自动化评分函数。

## 3. PPO 在 RLHF 中的具体形式：四个模型的角色

有了奖励模型之后，RLHF 用强化学习（通常是 PPO，Proximal Policy Optimization）来调整语言模型的参数，让它生成能拿到更高奖励分数的回答。这个过程里涉及四个模型，各自角色不同：

```
┌─────────────┐     生成回答      ┌─────────────┐
│   Actor     │ ───────────────→ │   Reward    │
│ (待优化的策略) │                  │  (打分)      │
└─────────────┘ ←─────────────── └─────────────┘
       │              奖励信号
       │ 估计价值
       ▼
┌─────────────┐
│   Critic    │
│ (价值函数)   │
└─────────────┘

┌─────────────┐
│  Reference  │ ── 提供 KL 惩罚的基准，不参与更新
│ (冻结的SFT模型)│
└─────────────┘
```

- **Actor（策略模型）**：要优化的语言模型本身，初始化自 SFT 之后的模型。"动作"是生成 token，训练目标是调整参数让生成的回答获得更高奖励
- **Critic（价值模型）**：估计"在当前状态下未来能拿到的期望奖励"，用于计算 PPO 里的优势函数（advantage），降低训练方差、让梯度更新更稳定。通常与 Actor 共享大部分参数或结构类似，是训练时的辅助角色，推理阶段不需要
- **Reward（奖励模型）**：第 2 节训练好的模型，训练过程中被冻结，只负责给 Actor 生成的回答打分
- **Reference（参考模型）**：通常直接是 SFT 之后、还没做强化学习优化的模型副本，训练过程中完全冻结。作用是给 KL 惩罚项提供一个"不能偏离太远"的基准（详见第 4 节）

四个模型加起来意味着显存里同时要放得下：一份可训练的 Actor（含梯度和优化器状态）、一份可训练的 Critic（含梯度和优化器状态）、一份冻结的 Reward、一份冻结的 Reference——这是 RLHF 工程复杂度和显存开销高的直接原因（详见第 5 节）。

## 4. KL 惩罚为什么必须有

PPO 优化的目标不是单纯"奖励分数越高越好"，而是奖励分数减去一个 KL 散度惩罚项：

```
目标 = E[ reward(x, y) ] - β · KL(π_actor(y|x) || π_reference(y|x))
```

`KL(π_actor || π_reference)` 衡量当前策略（Actor）的输出分布相对参考模型（Reference）的输出分布偏离了多少，`β` 是控制惩罚强度的系数。

**为什么必须有这一项**：奖励模型本身是训练出来的近似函数，不是"人类偏好"本身，它在训练数据分布之外区域的打分不可靠。如果没有约束，强化学习的优化过程会疯狂寻找任何能让奖励模型打高分的输出方式，哪怕这种方式是奖励模型的"盲区"——比如输出奇怪的重复模式、堆砌某些奖励模型偏好的词汇、生成语法不通但恰好被误判为高质量的文本。这类现象统称**奖励黑客（reward hacking）**，第 5 节详细展开。

KL 惩罚的作用是给优化过程加一条"绳子"：策略可以调整，但不能离参考模型（也就是"还算正常、通过了 SFT 训练"的分布）太远。这样即使奖励模型在某个方向上给出了不可靠的高分，KL 惩罚也会限制策略真正滑向那个方向的幅度，把优化约束在"奖励模型判断相对更可信"的区域附近。

## 5. 奖励黑客与过优化

**奖励黑客（reward hacking）**指的是：策略模型找到了某种能让奖励模型打高分、但实际上不符合人类真实偏好的输出模式。这不是策略模型"作弊"的主观行为，而是优化过程的必然倾向——只要奖励函数和真实目标之间存在缝隙，足够强的优化压力就会找到并利用它。常见表现：输出长度被系统性拉长（如果奖励模型偏好更长回答）、堆砌某些标志性礼貌用语或免责声明、生成表面格式规范但内容空洞的文本。

**过优化（over-optimization）**是奖励黑客的更普遍的现象描述：随着强化学习训练步数增加，"奖励模型给出的分数"和"真实人类偏好"之间的相关性会逐渐减弱——训练初期两者高度一致，训练后期奖励分数继续上涨，人类评价却趋于平缓甚至下降。这说明策略模型学到的不是"更好满足人类偏好"，而是"更好利用奖励模型的弱点"。

缓解手段没有一次性解法，通常是多种手段组合：适度的 KL 惩罚（第 4 节）、定期用真实人类评估校准奖励模型是否仍可信、限制训练步数不要过度优化、使用多个不同奖励模型或加入规则性检查作为补充信号等。

## 6. RLHF 的工程难点

**显存**：如第 3 节所述，需要同时维护 Actor、Critic 两个可训练模型（各自的参数、梯度、优化器状态）以及 Reward、Reference 两个冻结但仍需占显存做前向推理的模型，四个模型同时驻留显存，是 RLHF 显存开销远高于普通 SFT 的直接原因。

**稳定性**：强化学习训练本身方差就比监督学习高——奖励信号来自采样生成的完整回答，一条回答里某个环节的微小变化都可能导致最终奖励波动很大，训练曲线容易震荡、甚至崩溃（某次更新后策略突然大幅偏移，输出质量骤降且难以恢复）。

**超参数敏感**：KL 惩罚系数 `β`、PPO 裁剪范围、学习率、采样温度等超参数，对最终效果的影响比监督学习阶段更敏感，同一套超参在不同奖励模型、不同基座模型上表现可能差异很大，需针对具体设置调优，通用"默认值"往往不够可靠。

**训练循环复杂**：一步 RLHF 更新至少包含"用 Actor 采样生成回答 → 用 Reward 打分 → 用 Critic 估计优势 → 计算 PPO 损失 → 更新 Actor 和 Critic"这一整条流水线，比 SFT 阶段"前向-反向-更新"的单一循环复杂得多，工程实现和调试难度也相应更高。这也是后续 DPO 等免强化学习对齐方法（详见 [DPO与免RL对齐](04-DPO与免RL对齐.md)）想要绕开的复杂度来源。

## 7. 用 NumPy 实现 Bradley-Terry 奖励模型训练

用 NumPy 实现简化的奖励模型训练：线性函数模拟打分，Bradley-Terry 损失梯度下降训练，验证模型能正确区分"更好"和"更差"的样本。

```python
import numpy as np


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def bradley_terry_loss_and_grad(features_win, features_lose, w):
    """
    计算一个 batch 的 Bradley-Terry 负对数似然损失及对 w 的梯度。
    features_win/lose: (batch, dim)；w: (dim,)，线性打分 r(x) = w · x
    """
    reward_win = features_win @ w
    reward_lose = features_lose @ w
    diff = reward_win - reward_lose

    probs_correct = sigmoid(diff)
    loss = -np.mean(np.log(np.clip(probs_correct, 1e-12, 1.0)))

    # d(loss)/d(diff) = sigmoid(diff) - 1
    grad_diff = (probs_correct - 1.0)
    grad_w = np.mean(grad_diff[:, None] * (features_win - features_lose), axis=0)

    return loss, grad_w, probs_correct


def train_reward_model(features_win, features_lose, dim, n_steps=500, lr=0.1, seed=0):
    """用批量梯度下降训练奖励模型的线性权重"""
    rng = np.random.default_rng(seed)
    w = rng.normal(0, 0.1, size=dim)

    for step in range(n_steps):
        loss, grad_w, _ = bradley_terry_loss_and_grad(features_win, features_lose, w)
        w -= lr * grad_w
        if step % 100 == 0:
            print(f"  step {step:3d}: loss = {loss:.4f}")

    return w


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    dim = 5       # 假设每个回答被编码成 5 维特征向量（真实场景是模型的隐藏表示）
    n_pairs = 300

    # 构造一个"真实"的偏好方向：假设特征的第 0 维越大，回答质量越高（人类真实偏好）
    true_w = np.array([2.0, 0.0, 0.0, 0.0, 0.0])

    # 生成候选回答的特征，win 组特征第0维系统性地比 lose 组大
    features_lose = rng.normal(0, 1, size=(n_pairs, dim))
    features_win = features_lose.copy()
    features_win[:, 0] += rng.uniform(0.5, 2.0, size=n_pairs)  # 让 win 组在第0维上更"好"

    print("训练奖励模型（Bradley-Terry 损失，批量梯度下降）：")
    learned_w = train_reward_model(features_win, features_lose, dim, seed=1)

    print(f"\n学到的权重: {np.round(learned_w, 3)}")
    print(f"真实偏好方向: {true_w}")

    # 验证：用学到的奖励模型给 win/lose 打分，检查是否正确区分
    reward_win = features_win @ learned_w
    reward_lose = features_lose @ learned_w
    accuracy = np.mean(reward_win > reward_lose)
    print(f"\n奖励模型正确判断 win > lose 的比例: {accuracy:.4f}")

    # 用一对全新样本验证泛化：只在第0维上有差异，其余维度相同
    test_lose = np.array([0.0, 1.0, -1.0, 0.5, 0.5])
    test_win = test_lose.copy()
    test_win[0] += 1.5
    r_win, r_lose = test_win @ learned_w, test_lose @ learned_w
    print(f"\n新样本测试: reward(win)={r_win:.3f}, reward(lose)={r_lose:.3f}, "
          f"win优于lose: {r_win > r_lose}")
```

实测输出（numpy 2.4.4）：

```
训练奖励模型（Bradley-Terry 损失，批量梯度下降）：
  step   0: loss = 0.6714
  step 100: loss = 0.0945
  step 200: loss = 0.0549
  step 300: loss = 0.0397
  step 400: loss = 0.0315

学到的权重: [ 3.6    0.082  0.033 -0.13   0.091]
真实偏好方向: [2. 0. 0. 0. 0.]

奖励模型正确判断 win > lose 的比例: 1.0000

新样本测试: reward(win)=5.429, reward(lose)=0.029, win优于lose: True
```

训练损失从 0.67 持续下降到 0.03，学到的权重在第 0 维上明显大于其余维度（其余维度都在 0 附近小幅波动），方向上与构造数据时设定的真实偏好 `[2, 0, 0, 0, 0]` 一致——权重的绝对数值比真实值大是因为 Bradley-Terry 损失只约束"差值的符号和相对大小"，不约束权重的绝对尺度，只要能正确区分 win/lose 即可继续降低损失。训练集上的判断正确率达到 100%，全新构造的测试样本上也正确判断出 `win` 优于 `lose`，说明这个简化的奖励模型确实学到了"哪个维度决定偏好"这一底层信号，而不是单纯记住了训练样本。真实的 RLHF 里，这里的"特征向量"会换成语言模型的隐藏表示，"线性打分"通常会换成一个小型的打分头，但 Bradley-Terry 损失函数和训练逻辑与这里完全一致。

## 8. 小结

| 概念 | 一句话总结 |
| --- | --- |
| SFT 的局限 | 只能模仿示范答案，学不到"哪个更好"这种相对偏好判断 |
| Bradley-Terry | 奖励差值经过 sigmoid 转化为"更好"的概率，用负对数似然训练奖励模型 |
| Actor | 待优化的策略模型，初始化自 SFT 模型 |
| Critic | 估计期望奖励，用于降低 PPO 训练方差 |
| Reward | 冻结的奖励模型，给 Actor 生成的回答打分 |
| Reference | 冻结的 SFT 模型副本，为 KL 惩罚提供基准 |
| KL 惩罚 | 防止策略偏离参考模型太远，约束优化不去利用奖励模型的盲区 |
| 奖励黑客/过优化 | 优化压力找到奖励模型的弱点，奖励分数和真实偏好逐渐脱钩 |
| 工程难点 | 四模型同时驻留显存、训练方差大、超参敏感、流水线复杂 |

## 9. 延伸阅读

- 三阶段范式中对齐阶段的定位 → [三阶段范式与数据构造](01-三阶段范式与数据构造.md)
- 绕开显式奖励模型和强化学习的对齐方法 → [DPO与免RL对齐](04-DPO与免RL对齐.md)
- 用更少参数完成策略模型的更新 → [PEFT参数高效微调](02-PEFT参数高效微调.md)
- 大模型的使用视角基础概念 → [大语言模型基础](../../ai-agent/00-基础概念/02-大语言模型基础.md)
