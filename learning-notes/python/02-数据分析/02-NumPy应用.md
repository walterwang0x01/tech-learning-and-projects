# NumPy应用
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

<!-- version-check: NumPy 2.5.x, checked 2026-07-08 -->

## 1. NumPy概述

NumPy 是一个开源的 Python 科学计算库，**用于快速处理任意维度的数组**。NumPy **支持常见的数组和矩阵操作**，对于同样的数值计算任务，使用 NumPy 不仅代码要简洁的多，而且 NumPy 在性能上也远远优于原生 Python，至少是一到两个数量级的差距，而且数据量越大，NumPy 的优势就越明显。

### 1.1 NumPy的核心特性

- **ndarray对象**：NumPy 最为核心的数据类型是`ndarray`，使用`ndarray`可以处理一维、二维和多维数组
- **高性能**：NumPy 底层代码使用 C 语言编写，解决了 GIL 的限制，性能远优于 Python 原生列表
- **连续内存**：`ndarray`在存取数据的时候，数据与数据的地址都是连续的，这确保了可以进行高效率的批量操作
- **丰富的功能**：提供了大量处理数据的方法，尤其获取数据统计特征的方法

## 2. 准备工作

### 2.1 安装NumPy

```bash
pip install numpy
```

### 2.2 导入NumPy

```python
import numpy as np
```

## 3. 创建数组对象

### 3.1 使用array函数

通过列表创建数组对象：

```python
array1 = np.array([1, 2, 3, 4, 5])
print(array1)  # [1 2 3 4 5]

array2 = np.array([[1, 2, 3], [4, 5, 6]])
print(array2)
# [[1 2 3]
#  [4 5 6]]
```

### 3.2 使用arange函数

指定取值范围和跨度创建数组对象：

```python
array3 = np.arange(0, 20, 2)
print(array3)  # [ 0  2  4  6  8 10 12 14 16 18]
```

### 3.3 使用linspace函数

用指定范围和元素个数创建数组对象，生成等差数列：

```python
array4 = np.linspace(-1, 1, 11)
print(array4)  # [-1.  -0.8 -0.6 -0.4 -0.2  0.   0.2  0.4  0.6  0.8  1. ]
```

### 3.4 使用logspace函数

生成等比数列：

```python
array5 = np.logspace(1, 10, num=10, base=2)
print(array5)  # [   2.    4.    8.   16.   32.   64.  128.  256.  512. 1024.]
```

### 3.5 使用随机数函数

```python
# 产生10个[0, 1)范围的随机小数
array6 = np.random.rand(10)

# 产生10个[1, 100)范围的随机整数
array7 = np.random.randint(1, 100, 10)

# 产生20个μ=50，σ=10的正态分布随机数
array8 = np.random.normal(50, 10, 20)

# 产生3行4列的二维数组
array9 = np.random.rand(3, 4)
```

### 3.6 创建特殊数组

```python
# 全0数组
zeros_array = np.zeros((3, 4))

# 全1数组
ones_array = np.ones((3, 4))

# 指定值数组
full_array = np.full((3, 4), 10)

# 单位矩阵
eye_array = np.eye(4)
```

## 4. 数组的属性

### 4.1 基本属性

```python
array = np.array([[1, 2, 3], [4, 5, 6]])

print(array.ndim)    # 2（维度）
print(array.shape)   # (2, 3)（形状）
print(array.size)    # 6（元素总数）
print(array.dtype)   # int64（数据类型）
print(array.itemsize)  # 8（每个元素占用的字节数）
```

### 4.2 数据类型

```python
# 指定数据类型
array1 = np.array([1, 2, 3], dtype=np.float64)
array2 = np.array([1, 2, 3], dtype='i8')  # 8字节整数
array3 = np.array([1, 2, 3], dtype='f4')  # 4字节浮点数

# 类型转换
array4 = array1.astype(np.int32)
```

## 5. 数组的索引和切片

### 5.1 一维数组索引

```python
array = np.array([1, 2, 3, 4, 5])
print(array[0])    # 1
print(array[-1])   # 5
print(array[1:4])  # [2 3 4]
```

### 5.2 二维数组索引

```python
array = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

print(array[0, 1])      # 2（第0行第1列）
print(array[0])        # [1 2 3]（第0行）
print(array[:, 1])      # [2 5 8]（第1列）
print(array[0:2, 1:3])  # [[2 3] [5 6]]（切片）
```

### 5.3 布尔索引

```python
array = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
print(array[array > 5])  # [6 7 8 9]
print(array[(array > 3) & (array < 7)])  # [4 5 6]
```

### 5.4 花式索引

```python
array = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
print(array[[0, 2, 4]])  # [1 3 5]
```

## 6. 数组的运算

### 6.1 数组与标量的运算

```python
array = np.arange(1, 10)
print(array + 10)  # [11 12 13 14 15 16 17 18 19]
print(array * 10)  # [10 20 30 40 50 60 70 80 90]
print(array > 5)   # [False False False False False  True  True  True  True]
```

### 6.2 数组与数组的运算

```python
array1 = np.arange(1, 10)
array2 = np.array([1, 1, 1, 2, 2, 2, 3, 3, 3])

print(array1 + array2)  # [ 2  3  4  6  7  8 10 11 12]
print(array1 * array2)   # [ 1  2  3  8 10 12 21 24 27]
print(array1 ** array2)  # [  1   2   3  16  25  36 343 512 729]
```

### 6.3 广播机制

当两个数组的形状不同时，NumPy 会尝试使用广播机制进行运算：

```python
array1 = np.array([[1, 2, 3], [4, 5, 6]])
array2 = np.array([10, 20, 30])

# 广播：array2会被扩展为[[10, 20, 30], [10, 20, 30]]
print(array1 + array2)  # [[11 22 33] [14 25 36]]
```

## 7. 通用函数

### 7.1 一元函数

```python
array = np.array([1, 4, 9, 16, 25])

print(np.sqrt(array))    # 平方根
print(np.square(array))  # 平方
print(np.exp(array))     # e的x次方
print(np.log(array))     # 自然对数
print(np.log2(array))    # 以2为底的对数
print(np.abs(array))     # 绝对值
print(np.sin(array))     # 正弦
print(np.cos(array))     # 余弦
```

### 7.2 二元函数

```python
array1 = np.array([[4, 5, 6], [7, 8, 9]])
array2 = np.array([[1, 2, 3], [3, 2, 1]])

print(np.maximum(array1, array2))  # 对应元素的最大值
print(np.minimum(array1, array2))  # 对应元素的最小值
print(np.power(array1, array2))    # 对应元素的幂运算
print(np.add(array1, array2))      # 加法
print(np.multiply(array1, array2)) # 乘法
```

## 8. 数组的方法

### 8.1 统计方法

```python
array = np.random.randint(1, 100, 10)

print(array.sum())    # 总和
print(array.mean())   # 均值
print(array.std())    # 标准差
print(array.var())    # 方差
print(array.max())    # 最大值
print(array.min())    # 最小值
print(np.median(array))  # 中位数
```

### 8.2 轴参数

对于多维数组，可以通过`axis`参数指定运算的轴：

```python
array = np.random.randint(60, 101, (5, 3))

print(array.mean())      # 所有元素的均值
print(array.mean(axis=0))  # 沿第0轴（行）求均值，结果形状为(3,)
print(array.mean(axis=1))  # 沿第1轴（列）求均值，结果形状为(5,)
```

## 9. 数组的形状操作

### 9.1 改变形状

```python
array = np.arange(12)

# reshape：改变形状（不改变原数组）
array2d = array.reshape(3, 4)

# resize：改变形状（改变原数组）
array.resize(3, 4)

# flatten：展平为一维数组
array1d = array2d.flatten()
```

### 9.2 数组转置

```python
array = np.array([[1, 2, 3], [4, 5, 6]])
print(array.T)  # 转置
print(array.transpose())  # 转置
```

## 10. 数组的拼接和分割

### 10.1 数组拼接

```python
array1 = np.array([[1, 2], [3, 4]])
array2 = np.array([[5, 6], [7, 8]])

# 垂直拼接
vstack = np.vstack([array1, array2])

# 水平拼接
hstack = np.hstack([array1, array2])

# 通用拼接
concatenate = np.concatenate([array1, array2], axis=0)  # 垂直
```

### 10.2 数组分割

```python
array = np.arange(12).reshape(3, 4)

# 垂直分割
vsplit = np.vsplit(array, 3)

# 水平分割
hsplit = np.hsplit(array, 2)

# 通用分割
split = np.split(array, 2, axis=1)
```

## 11. 线性代数运算

### 11.1 矩阵运算

```python
array1 = np.array([[1, 2], [3, 4]])
array2 = np.array([[5, 6], [7, 8]])

# 矩阵乘法
dot_product = np.dot(array1, array2)
# 或使用@运算符
dot_product = array1 @ array2

# 矩阵转置
transpose = array1.T

# 矩阵求逆
inverse = np.linalg.inv(array1)

# 行列式
determinant = np.linalg.det(array1)

# 特征值和特征向量
eigenvalues, eigenvectors = np.linalg.eig(array1)
```

### 11.2 向量运算

```python
vector1 = np.array([1, 2, 3])
vector2 = np.array([4, 5, 6])

# 点积
dot = np.dot(vector1, vector2)

# 叉积
cross = np.cross(vector1, vector2)

# 向量长度
norm = np.linalg.norm(vector1)
```

## 12. 数组的保存和加载

### 12.1 保存数组

```python
array = np.random.rand(3, 4)

# 保存为文本文件
np.savetxt('array.txt', array)

# 保存为二进制文件
np.save('array.npy', array)

# 保存多个数组
np.savez('arrays.npz', arr1=array1, arr2=array2)
```

### 12.2 加载数组

```python
# 从文本文件加载
array = np.loadtxt('array.txt')

# 从二进制文件加载
array = np.load('array.npy')

# 加载多个数组
data = np.load('arrays.npz')
array1 = data['arr1']
array2 = data['arr2']
```

## 13. 数组的高级索引

### 13.1 整数数组索引

```python
array = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# 使用整数数组索引
rows = np.array([0, 1, 2])
cols = np.array([0, 1, 2])
print(array[rows, cols])  # [1 5 9]
```

### 13.2 布尔数组索引

```python
array = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# 布尔索引
mask = array > 5
print(array[mask])  # [6 7 8 9]
```

## 14. 数组的复制

### 14.1 视图（View）

视图是数组的浅拷贝，共享数据：

```python
array = np.array([1, 2, 3, 4, 5])
view = array.view()
view[0] = 100
print(array)  # [100   2   3   4   5]（原数组也被修改）
```

### 14.2 副本（Copy）

副本是数组的深拷贝，不共享数据：

```python
array = np.array([1, 2, 3, 4, 5])
copy = array.copy()
copy[0] = 100
print(array)  # [1 2 3 4 5]（原数组不变）
```

## 15. 常用NumPy函数

### 15.1 数学函数

```python
array = np.array([1, 2, 3, 4, 5])

np.sum(array)      # 求和
np.prod(array)     # 求积
np.cumsum(array)   # 累积和
np.cumprod(array)  # 累积积
```

### 15.2 排序和搜索

```python
array = np.array([3, 1, 4, 1, 5, 9, 2, 6])

np.sort(array)           # 排序
np.argsort(array)        # 排序索引
np.argmax(array)          # 最大值索引
np.argmin(array)          # 最小值索引
np.where(array > 5)       # 条件查找
```

### 15.3 集合操作

```python
array1 = np.array([1, 2, 3, 4, 5])
array2 = np.array([3, 4, 5, 6, 7])

np.unique(array1)              # 去重
np.intersect1d(array1, array2)  # 交集
np.union1d(array1, array2)     # 并集
np.setdiff1d(array1, array2)   # 差集
```

## 16. 性能优化建议

1. **使用向量化操作**：避免使用 Python 循环，使用 NumPy 的向量化操作
2. **选择合适的数据类型**：使用合适的数据类型可以减少内存占用
3. **使用视图而非副本**：在不需要修改原数组时，使用视图可以节省内存
4. **利用广播机制**：合理使用广播可以简化代码并提高性能

## 17. 总结

NumPy 是 Python 科学计算的基础库，提供了高性能的多维数组对象和丰富的数组操作函数。掌握 NumPy 的基本操作、数组运算、统计方法和线性代数运算，是进行数据分析和科学计算的基础。
## 🎬 推荐视频资源

- [freeCodeCamp - NumPy Full Course](https://www.youtube.com/watch?v=QUT1VHiLmmI) — NumPy完整教程
- [Keith Galli - NumPy Tutorial](https://www.youtube.com/watch?v=GB9ByFAIAH4) — NumPy实战教程
