# PyTorch 训练实战

> Author: Walter Wang

> **读完你能回答的 3 个问题**
>
> 1. 一个标准的 PyTorch 训练循环有哪几步？为什么每步开始要 `optimizer.zero_grad()`？
> 2. `model.train()` 和 `model.eval()` 到底切换了什么？漏掉会有什么后果？
> 3. 训练中途断了，怎么保证不用从头开始？checkpoint 该存哪些东西？

## 0. 这篇的定位

前面所有原理笔记的代码都是纯 numpy——为了让你看清每一步在算什么。但**真实工作用框架**，因为你不会想手写反向传播和 GPU 调度。

这篇是「从看懂原理」到「能训模型」的桥。它不是 PyTorch API 手册，只讲**训练一个模型必须知道的那些**。

> <!-- version-check: PyTorch API 在 2.x 内相对稳定，但 MPS 后端算子支持范围与 checkpoint 最佳实践会演进，checked 2026-08-04 -->

本篇代码在 macOS + PyTorch 2.13.0 + Python 3.14 实测运行通过。

## 1. 五个核心概念

PyTorch 的心智模型可以压缩成五个部件：

```
Tensor        数据容器，会记录梯度
  ↓
nn.Module     模型：装参数 + 定义 forward
  ↓
DataLoader    喂数据：分批、打乱
  ↓
Loss          算差距
  ↓
Optimizer     按梯度更新参数
```

### Tensor：会记梯度的数组

Tensor 和 numpy 数组几乎一样，多了两件事：**能上 GPU**、**能自动求导**。

```python
x = torch.randn(3, 4)                          # 普通张量
w = torch.randn(4, 2, requires_grad=True)      # 标记「要算它的梯度」
```

`requires_grad=True` 是关键开关。打开后，PyTorch 会记录这个张量参与的所有运算，构成计算图，`backward()` 时沿图回传——这就是 [反向传播推导](../01-machine-learning/04-神经网络原理/02-反向传播推导.md) 讲的那套机制的自动化版本。

### nn.Module：模型的标准写法

```python
class MyModel(nn.Module):
    def __init__(self):
        super().__init__()              # 必须先调，否则参数注册不上
        self.fc1 = nn.Linear(10, 32)    # 定义有参数的层
        self.fc2 = nn.Linear(32, 2)

    def forward(self, x):               # 定义前向怎么算
        x = torch.relu(self.fc1(x))
        return self.fc2(x)
```

两条规则：

| 规则 | 原因 |
| --- | --- |
| `__init__` 里必须调 `super().__init__()` | 否则子模块和参数不会被注册，优化器拿不到参数 |
| 只写 `forward`，不写 `backward` | 反向由 autograd 自动生成 |

调用时**不要**直接调 `model.forward(x)`，要写 `model(x)`——后者会触发钩子等机制。

## 2. 训练循环：五步，顺序不能错

这是本篇最核心的内容。**几乎所有 PyTorch 训练代码都是这五步的变体**：

```python
for epoch in range(num_epochs):
    for batch_x, batch_y in dataloader:
        optimizer.zero_grad()          # 1. 清空上一步的梯度
        pred = model(batch_x)          # 2. 前向：算预测
        loss = criterion(pred, batch_y)# 3. 算损失
        loss.backward()                # 4. 反向：算梯度
        optimizer.step()               # 5. 更新参数
```

### 为什么必须 zero_grad()

这是新手最常见的 bug 来源。**PyTorch 的梯度是累加的，不是覆盖的**：

```
不清零会发生什么：

第 1 步  梯度 = g₁
第 2 步  梯度 = g₁ + g₂      ← 上一步的还在！
第 3 步  梯度 = g₁ + g₂ + g₃
              ↓
        梯度越来越大，参数更新失控，损失爆炸
```

「累加」这个设计不是缺陷，它让**梯度累积**成为可能——显存不够时，可以分几个小批次累积梯度再更新一次，等效于用大 batch 训练：

```python
for i, (bx, by) in enumerate(dataloader):
    loss = criterion(model(bx), by) / accum_steps   # 损失要除以累积步数
    loss.backward()                                  # 梯度累加
    if (i + 1) % accum_steps == 0:
        optimizer.step()
        optimizer.zero_grad()                        # 只在更新后清零
```

详见 [学习率调度与训练技巧](../01-machine-learning/05-训练工程/04-学习率调度与训练技巧.md)。

## 3. train() vs eval()：漏掉会出错的开关

```python
model.train()   # 训练模式
model.eval()    # 评估模式
```

它切换的是**两类层的行为**：

| 层 | `train()` 时 | `eval()` 时 |
| --- | --- | --- |
| Dropout | 随机丢弃神经元 | **全部保留** |
| BatchNorm | 用当前 batch 的统计量，同时更新 running stats | **用累积的 running stats**，不更新 |

**漏掉的后果**：

```
评估时忘了 model.eval()
  → Dropout 还在随机丢神经元
  → 同一个输入跑两次结果不同
  → 评估指标偏低且不稳定

训练时忘了 model.train()（比如评估后没切回来）
  → BatchNorm 不再更新统计量
  → 训练效果莫名变差
```

配套还有一个 `torch.no_grad()`——评估时不需要梯度，关掉能省显存加速：

```python
model.eval()
with torch.no_grad():
    for bx, by in val_loader:
        pred = model(bx)
```

**记住这个组合**：`model.eval()` + `torch.no_grad()` 一起用，两者管的事不同（前者管层行为，后者管是否建计算图）。

BatchNorm 的 running stats 机制详见 [归一化技术](../01-machine-learning/05-训练工程/03-归一化技术.md)。

## 4. DataLoader：批量与打乱

```python
from torch.utils.data import TensorDataset, DataLoader

dataset = TensorDataset(X, y)
loader = DataLoader(dataset, batch_size=32, shuffle=True)
```

三个参数的意义：

| 参数 | 作用 | 注意 |
| --- | --- | --- |
| `batch_size` | 一次喂多少样本 | 越大越稳但越吃显存；OOM 时先降这个 |
| `shuffle` | 每个 epoch 是否打乱 | **训练集必须 True，验证集 False** |
| `num_workers` | 几个进程加载数据 | 大于 0 能加速，但 Windows/Notebook 里易出问题 |

`shuffle` 为什么对训练集必须开：如果数据按标签排序，不打乱会让模型先连续看几百个类别 A，再连续看类别 B，梯度方向剧烈摇摆，训练不稳定。

## 5. Checkpoint：训练中断的保险

云端 Notebook 会话超时、本地断电、任务被抢占——**训练中断是常态**。不存 checkpoint 就是白跑。

### 存什么

新手常犯的错是「只存模型权重」，那样恢复后优化器状态丢了，训练不能真正续上：

```python
torch.save({
    "epoch": epoch,
    "model_state": model.state_dict(),          # 模型参数
    "optimizer_state": optimizer.state_dict(),  # ★ 优化器状态（Adam 的动量等）
    "best_val_loss": best_val_loss,             # 便于判断是否是最佳
}, "checkpoint.pt")
```

为什么优化器状态必须存：Adam 这类优化器内部维护一阶、二阶动量估计。丢了它们相当于重新「热身」，恢复后前几步的更新会失准。详见 [梯度下降与优化器](../01-machine-learning/04-神经网络原理/03-梯度下降与优化器.md)。

### 怎么恢复

```python
ckpt = torch.load("checkpoint.pt", map_location=device)
model.load_state_dict(ckpt["model_state"])
optimizer.load_state_dict(ckpt["optimizer_state"])
start_epoch = ckpt["epoch"] + 1        # 从下一轮继续
```

### 两种保存策略

| 策略 | 用途 |
| --- | --- |
| `last.pt`（每轮覆盖） | 断了能续，防止白跑 |
| `best.pt`（验证集最优时才存） | 最终部署用这个，防止用到过拟合后的权重 |

**两个都要存**。只存 last 会拿到过拟合的模型；只存 best 断了没法续训。

## 6. 设备管理：CPU / CUDA / MPS

```python
if torch.cuda.is_available():
    device = "cuda"          # NVIDIA
elif torch.backends.mps.is_available():
    device = "mps"           # Mac M 系列
else:
    device = "cpu"

model = model.to(device)
batch_x = batch_x.to(device)   # ★ 数据也要搬过去
```

**最常见的报错**：`Expected all tensors to be on the same device`——模型在 GPU 但数据还在 CPU。规则很简单：**参与同一次运算的所有张量必须在同一设备上**。

Mac MPS 的注意事项见 [开发环境与算力](../00-入门准备/02-开发环境与算力.md)：部分算子未实现会回落 CPU，某些操作精度与 CUDA 有细微差异。

## 7. 完整可运行示例

一个端到端的最小训练脚本，包含上面所有要点。**在 macOS + PyTorch 2.13.0 实测通过**。

```python
"""PyTorch 训练循环最小完整示例

包含：设备选择、Dataset/DataLoader、nn.Module、训练循环五步、
      train/eval 切换、checkpoint 存取、早停判断。

只依赖 torch，不需要下载任何数据集（数据是构造的）。
"""

import os
import tempfile

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

torch.manual_seed(0)


# ── 1. 设备选择 ─────────────────────────────────────
def pick_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


device = pick_device()
print(f"PyTorch {torch.__version__}  使用设备: {device}")


# ── 2. 造数据（真实项目里换成读文件）────────────────
def make_data(n, n_feat=10, seed=0):
    """造一个二分类任务：由前 3 个特征的线性组合决定标签"""
    g = torch.Generator().manual_seed(seed)
    X = torch.randn(n, n_feat, generator=g)
    logit = 1.5 * X[:, 0] - 2.0 * X[:, 1] + 0.8 * X[:, 2]
    noise = 0.5 * torch.randn(n, generator=g)
    y = ((logit + noise) > 0).long()
    return X, y


X_train, y_train = make_data(2000, seed=1)
X_val, y_val = make_data(500, seed=2)

train_loader = DataLoader(TensorDataset(X_train, y_train),
                          batch_size=64, shuffle=True)    # 训练集打乱
val_loader = DataLoader(TensorDataset(X_val, y_val),
                        batch_size=128, shuffle=False)    # 验证集不打乱

print(f"训练集 {len(X_train)} 条，验证集 {len(X_val)} 条")


# ── 3. 定义模型 ─────────────────────────────────────
class MLP(nn.Module):
    def __init__(self, n_in=10, n_hidden=32, n_out=2, p_drop=0.2):
        super().__init__()                      # 必须先调
        self.net = nn.Sequential(
            nn.Linear(n_in, n_hidden),
            nn.BatchNorm1d(n_hidden),           # 训练/评估行为不同的层
            nn.ReLU(),
            nn.Dropout(p_drop),                 # 训练/评估行为不同的层
            nn.Linear(n_hidden, n_out),
        )

    def forward(self, x):
        return self.net(x)


model = MLP().to(device)
n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"模型可训练参数: {n_params}")


# ── 4. 损失与优化器 ─────────────────────────────────
criterion = nn.CrossEntropyLoss()               # 内部含 softmax，不要自己再加
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-2)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=15)


# ── 5. 训练与评估函数 ───────────────────────────────
def train_one_epoch():
    model.train()                               # ★ 切训练模式
    total_loss, total_n = 0.0, 0
    for bx, by in train_loader:
        bx, by = bx.to(device), by.to(device)    # ★ 数据搬到同一设备

        optimizer.zero_grad()                    # 1. 清梯度
        pred = model(bx)                         # 2. 前向
        loss = criterion(pred, by)               # 3. 算损失
        loss.backward()                          # 4. 反向
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)  # 梯度裁剪
        optimizer.step()                         # 5. 更新

        total_loss += loss.item() * bx.size(0)
        total_n += bx.size(0)
    return total_loss / total_n


@torch.no_grad()                                 # ★ 评估不需要梯度
def evaluate(loader):
    model.eval()                                 # ★ 切评估模式
    total_loss, correct, total_n = 0.0, 0, 0
    for bx, by in loader:
        bx, by = bx.to(device), by.to(device)
        pred = model(bx)
        total_loss += criterion(pred, by).item() * bx.size(0)
        correct += (pred.argmax(dim=1) == by).sum().item()
        total_n += bx.size(0)
    return total_loss / total_n, correct / total_n


# ── 6. 训练主循环（含 checkpoint 与早停）────────────
ckpt_dir = tempfile.mkdtemp()
last_path = os.path.join(ckpt_dir, "last.pt")
best_path = os.path.join(ckpt_dir, "best.pt")

best_val = float("inf")
patience, bad_epochs = 4, 0

print()
print("epoch | train_loss | val_loss | val_acc |   lr    | 备注")
print("-" * 62)

for epoch in range(1, 16):
    tr_loss = train_one_epoch()
    va_loss, va_acc = evaluate(val_loader)
    lr_now = optimizer.param_groups[0]["lr"]
    scheduler.step()

    note = ""
    # 每轮都存 last：断了能续
    torch.save({"epoch": epoch,
                "model_state": model.state_dict(),
                "optimizer_state": optimizer.state_dict(),
                "best_val_loss": best_val}, last_path)

    # 只在验证集变好时存 best：防止用到过拟合权重
    if va_loss < best_val:
        best_val = va_loss
        bad_epochs = 0
        torch.save({"epoch": epoch,
                    "model_state": model.state_dict(),
                    "optimizer_state": optimizer.state_dict(),
                    "best_val_loss": best_val}, best_path)
        note = "← 保存 best"
    else:
        bad_epochs += 1
        if bad_epochs >= patience:
            note = f"← 连续 {patience} 轮无改善，早停"

    print(f"{epoch:5d} | {tr_loss:10.4f} | {va_loss:8.4f} | {va_acc:7.2%} "
          f"| {lr_now:.2e} | {note}")

    if bad_epochs >= patience:
        break


# ── 7. 演示 checkpoint 恢复 ─────────────────────────
print()
print("=" * 62)
print("演示：从 checkpoint 恢复")
print("=" * 62)

ckpt = torch.load(last_path, map_location=device, weights_only=True)
print(f"  last.pt   停在 epoch {ckpt['epoch']}，恢复后应从 {ckpt['epoch'] + 1} 继续")


def quick_acc(m):
    """用同一套逻辑测准确率，便于对比"""
    m.eval()
    with torch.no_grad():
        correct = sum((m(bx.to(device)).argmax(1) == by.to(device)).sum().item()
                      for bx, by in val_loader)
    return correct / len(X_val)


fresh = MLP().to(device)
acc_random = quick_acc(fresh)                      # 未载入权重，等于随机初始化

best_ckpt = torch.load(best_path, map_location=device, weights_only=True)
fresh.load_state_dict(best_ckpt["model_state"])
acc_restored = quick_acc(fresh)                    # 载入 best 权重后

print(f"  随机初始化的模型准确率: {acc_random:.2%}")
print(f"  载入 best.pt 后准确率 : {acc_restored:.2%}")
print(f"  → 权重确实被正确恢复了")


# ── 8. 演示 train/eval 模式的实际差异 ───────────────
print()
print("=" * 62)
print("演示：train() 与 eval() 的差异（Dropout 导致的随机性）")
print("=" * 62)

sample = X_val[:8].to(device)

model.train()
out1 = model(sample)
out2 = model(sample)
diff_train = (out1 - out2).abs().max().item()

model.eval()
with torch.no_grad():
    out3 = model(sample)
    out4 = model(sample)
diff_eval = (out3 - out4).abs().max().item()

print(f"  train() 模式下同一输入跑两次，最大差异 = {diff_train:.6f}")
print(f"  eval()  模式下同一输入跑两次，最大差异 = {diff_eval:.6f}")
print()
print("  → train() 下有差异，因为 Dropout 在随机丢弃")
print("  → eval() 下完全一致，这才是评估该有的行为")
print("  → 所以评估前忘了 model.eval() 会得到偏低且不稳定的指标")


# ── 9. 演示忘记 zero_grad() 的后果 ──────────────────
print()
print("=" * 62)
print("演示：忘记 zero_grad() 会让梯度累加失控")
print("=" * 62)

toy = nn.Linear(4, 1).to(device)
tx = torch.randn(16, 4, device=device)
ty = torch.randn(16, 1, device=device)
mse = nn.MSELoss()

print("  正确做法（每步清零）:")
for step in range(1, 4):
    toy.zero_grad()
    mse(toy(tx), ty).backward()
    print(f"    第 {step} 步  梯度范数 = {toy.weight.grad.norm().item():.6f}")

print("  错误做法（不清零）:")
toy.zero_grad()
for step in range(1, 4):
    mse(toy(tx), ty).backward()
    print(f"    第 {step} 步  梯度范数 = {toy.weight.grad.norm().item():.6f}  ← 在累加")

print()
print("  → 不清零时梯度线性累加，参数更新会越来越猛，最终损失爆炸")

# 清理临时文件
import shutil
shutil.rmtree(ckpt_dir, ignore_errors=True)
```

实测输出：

```
PyTorch 2.13.0  使用设备: mps
训练集 2000 条，验证集 500 条
模型可训练参数: 482

epoch | train_loss | val_loss | val_acc |   lr    | 备注
--------------------------------------------------------------
    1 |     0.6826 |   0.5945 |  71.80% | 1.00e-03 | ← 保存 best
    2 |     0.5667 |   0.4867 |  85.20% | 9.89e-04 | ← 保存 best
    3 |     0.4721 |   0.3974 |  90.00% | 9.57e-04 | ← 保存 best
    4 |     0.3916 |   0.3330 |  93.00% | 9.05e-04 | ← 保存 best
    5 |     0.3352 |   0.2845 |  94.20% | 8.35e-04 | ← 保存 best
    6 |     0.2908 |   0.2517 |  94.40% | 7.50e-04 | ← 保存 best
    7 |     0.2689 |   0.2373 |  95.60% | 6.55e-04 | ← 保存 best
    8 |     0.2491 |   0.2152 |  94.80% | 5.52e-04 | ← 保存 best
    9 |     0.2512 |   0.2108 |  95.40% | 4.48e-04 | ← 保存 best
   10 |     0.2303 |   0.2023 |  95.80% | 3.45e-04 | ← 保存 best
   11 |     0.2227 |   0.1980 |  93.40% | 2.50e-04 | ← 保存 best
   12 |     0.2161 |   0.1983 |  95.20% | 1.65e-04 | 
   13 |     0.2228 |   0.1937 |  94.00% | 9.55e-05 | ← 保存 best
   14 |     0.2227 |   0.1909 |  94.60% | 4.32e-05 | ← 保存 best
   15 |     0.2221 |   0.1907 |  95.00% | 1.09e-05 | ← 保存 best

==============================================================
演示：从 checkpoint 恢复
==============================================================
  last.pt   停在 epoch 15，恢复后应从 16 继续
  随机初始化的模型准确率: 53.40%
  载入 best.pt 后准确率 : 95.00%
  → 权重确实被正确恢复了

==============================================================
演示：train() 与 eval() 的差异（Dropout 导致的随机性）
==============================================================
  train() 模式下同一输入跑两次，最大差异 = 2.195314
  eval()  模式下同一输入跑两次，最大差异 = 0.000000

  → train() 下有差异，因为 Dropout 在随机丢弃
  → eval() 下完全一致，这才是评估该有的行为
  → 所以评估前忘了 model.eval() 会得到偏低且不稳定的指标

==============================================================
演示：忘记 zero_grad() 会让梯度累加失控
==============================================================
  正确做法（每步清零）:
    第 1 步  梯度范数 = 1.125002
    第 2 步  梯度范数 = 1.125002
    第 3 步  梯度范数 = 1.125002
  错误做法（不清零）:
    第 1 步  梯度范数 = 1.125002  ← 在累加
    第 2 步  梯度范数 = 2.250004  ← 在累加
    第 3 步  梯度范数 = 3.375005  ← 在累加

  → 不清零时梯度线性累加，参数更新会越来越猛，最终损失爆炸
```

## 8. 常见报错速查

| 报错 | 原因 | 解决 |
| --- | --- | --- |
| `Expected all tensors to be on the same device` | 模型和数据不在同一设备 | 数据也要 `.to(device)` |
| `CUDA out of memory` | 显存不够 | 降 batch_size、梯度累积、混合精度 |
| 损失变成 `nan` | 学习率太大 / 梯度爆炸 / log(0) | 降 lr、加梯度裁剪、检查损失函数输入 |
| 损失不下降 | lr 太小 / 忘了 `optimizer.step()` / 数据标签错位 | 逐项排查，先确认能过拟合一个小批次 |
| 评估结果每次不同 | 忘了 `model.eval()` | 评估前切模式 |
| `element 0 of tensors does not require grad` | 在 `no_grad()` 里做了 backward | 检查上下文 |
| 训练效果比预期差很多 | 评估后忘了切回 `model.train()` | 每个 epoch 开头显式调用 |

**一个高效的调试技巧**：新写的训练代码，先只用 **一个** batch 反复训练，看损失能不能降到接近 0。如果连一个 batch 都过拟合不了，说明代码有 bug（而不是模型能力不够）。

## 9. 小结

| 要点 | 内容 |
| --- | --- |
| **训练循环五步** | zero_grad → forward → loss → backward → step |
| **梯度是累加的** | 所以必须 zero_grad；也因此梯度累积才可行 |
| `train()` / `eval()` | 切换 Dropout 与 BatchNorm 的行为，漏掉会出错 |
| `no_grad()` | 评估时用，省显存加速，与 `eval()` 管的事不同 |
| DataLoader | 训练集 `shuffle=True`，验证集 `False` |
| **Checkpoint 存三样** | 模型权重 + **优化器状态** + epoch |
| last 与 best 都要存 | 只存 last 会拿到过拟合模型；只存 best 断了没法续 |
| 设备一致 | 模型和数据必须在同一 device |
| 调试起手式 | 先确认能过拟合一个 batch |

## 10. 延伸阅读

- 这些代码背后的数学 → [反向传播推导](../01-machine-learning/04-神经网络原理/02-反向传播推导.md)
- AdamW 与其他优化器的区别 → [梯度下降与优化器](../01-machine-learning/04-神经网络原理/03-梯度下降与优化器.md)
- 为什么用交叉熵而非 MSE → [损失函数](../01-machine-learning/04-神经网络原理/05-损失函数.md)
- BatchNorm 的 running stats 机制 → [归一化技术](../01-machine-learning/05-训练工程/03-归一化技术.md)
- 梯度裁剪、梯度累积、混合精度 → [学习率调度与训练技巧](../01-machine-learning/05-训练工程/04-学习率调度与训练技巧.md)
- 早停与过拟合监控 → [过拟合与偏差方差](../01-machine-learning/05-训练工程/01-过拟合与偏差方差.md)
- 环境与设备配置 → [开发环境与算力](../00-入门准备/02-开发环境与算力.md)
- 框架 API 的更多用法 → [深度学习框架应用](../../01-languages/python/03-机器学习/02-深度学习框架应用.md)

## 🎬 推荐视频资源

> 以下资源均为频道 / 课程 / 官网入口级链接（已于 2026-08-04 实测可访问）。刻意不收录单个视频 ID——那类链接失效率高，且难以核实归属。
> 从入口进去按本篇主题检索，命中率比一条可能失效的直链更高。

### 📺 视频频道与课时

- [Andrej Karpathy YouTube](https://www.youtube.com/@AndrejKarpathy)（从零手写神经网络到 GPT，代码级讲解）
- [跟李沐学AI（B 站）](https://space.bilibili.com/1567748478)

### 🎓 系统课程与教材

- [动手学深度学习（中文版）](https://zh.d2l.ai/)（**与本篇最互补：完整的 PyTorch 代码实现**）
- [PyTorch 官方安装指引](https://pytorch.org/get-started/locally/)
