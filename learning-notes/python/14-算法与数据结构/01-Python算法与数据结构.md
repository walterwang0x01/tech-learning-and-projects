# Python算法与数据结构
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 算法与数据结构概述

算法和数据结构是编程的基础，Python提供了丰富的数据结构，同时也可以实现各种经典算法。

## 2. 数据结构

### 2.1 数组和列表

```python
# 列表操作
arr = [1, 2, 3, 4, 5]

# 访问：O(1)
value = arr[0]

# 插入：O(n)
arr.insert(0, 0)

# 删除：O(n)
arr.remove(3)

# 查找：O(n)
index = arr.index(4)
```

### 2.2 栈（Stack）

```python
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items.pop()
    
    def peek(self):
        return self.items[-1]
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# 使用
stack = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())  # 2
```

### 2.3 队列（Queue）

```python
from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, item):
        self.items.append(item)
    
    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.items.popleft()
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# 使用
queue = Queue()
queue.enqueue(1)
queue.enqueue(2)
print(queue.dequeue())  # 1
```

### 2.4 优先队列

```python
import heapq

# 最小堆
heap = []
heapq.heappush(heap, 3)
heapq.heappush(heap, 1)
heapq.heappush(heap, 2)
print(heapq.heappop(heap))  # 1

# 最大堆（使用负数）
heap = []
heapq.heappush(heap, -3)
heapq.heappush(heap, -1)
heapq.heappush(heap, -2)
print(-heapq.heappop(heap))  # 3
```

### 2.5 链表

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
    
    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
    
    def delete(self, data):
        if not self.head:
            return
        if self.head.data == data:
            self.head = self.head.next
            return
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                return
            current = current.next
```

### 2.6 二叉树

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class BinaryTree:
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        if not self.root:
            self.root = TreeNode(val)
        else:
            self._insert(self.root, val)
    
    def _insert(self, node, val):
        if val < node.val:
            if node.left:
                self._insert(node.left, val)
            else:
                node.left = TreeNode(val)
        else:
            if node.right:
                self._insert(node.right, val)
            else:
                node.right = TreeNode(val)
    
    def inorder(self, node):
        if node:
            self.inorder(node.left)
            print(node.val)
            self.inorder(node.right)
```

### 2.7 哈希表

```python
# Python字典就是哈希表
hash_table = {}

# 插入：O(1)
hash_table['key'] = 'value'

# 查找：O(1)
value = hash_table.get('key')

# 删除：O(1)
del hash_table['key']
```

### 2.8 图

```python
from collections import defaultdict

class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
    
    def add_edge(self, u, v):
        self.graph[u].append(v)
    
    def dfs(self, start, visited=None):
        if visited is None:
            visited = set()
        visited.add(start)
        print(start)
        for neighbor in self.graph[start]:
            if neighbor not in visited:
                self.dfs(neighbor, visited)
    
    def bfs(self, start):
        visited = set()
        queue = [start]
        visited.add(start)
        while queue:
            node = queue.pop(0)
            print(node)
            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
```

## 3. 排序算法

### 3.1 冒泡排序

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# 时间复杂度：O(n²)
# 空间复杂度：O(1)
```

### 3.2 选择排序

```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

# 时间复杂度：O(n²)
# 空间复杂度：O(1)
```

### 3.3 插入排序

```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

# 时间复杂度：O(n²)
# 空间复杂度：O(1)
```

### 3.4 快速排序

```python
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

# 时间复杂度：平均O(n log n)，最坏O(n²)
# 空间复杂度：O(log n)
```

### 3.5 归并排序

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# 时间复杂度：O(n log n)
# 空间复杂度：O(n)
```

### 3.6 堆排序

```python
import heapq

def heap_sort(arr):
    heap = []
    for item in arr:
        heapq.heappush(heap, item)
    return [heapq.heappop(heap) for _ in range(len(heap))]

# 时间复杂度：O(n log n)
# 空间复杂度：O(n)
```

## 4. 搜索算法

### 4.1 线性搜索

```python
def linear_search(arr, target):
    for i, item in enumerate(arr):
        if item == target:
            return i
    return -1

# 时间复杂度：O(n)
```

### 4.2 二分搜索

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# 时间复杂度：O(log n)
# 要求：数组必须有序
```

## 5. 动态规划

### 5.1 斐波那契数列

```python
def fibonacci(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 2:
        return 1
    memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]

# 时间复杂度：O(n)
# 空间复杂度：O(n)
```

### 5.2 最长公共子序列

```python
def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    return dp[m][n]
```

### 5.3 背包问题

```python
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(
                    dp[i - 1][w],
                    dp[i - 1][w - weights[i - 1]] + values[i - 1]
                )
            else:
                dp[i][w] = dp[i - 1][w]
    
    return dp[n][capacity]
```

## 6. 贪心算法

### 6.1 活动选择问题

```python
def activity_selection(activities):
    # 按结束时间排序
    activities.sort(key=lambda x: x[1])
    selected = [activities[0]]
    
    for activity in activities[1:]:
        if activity[0] >= selected[-1][1]:
            selected.append(activity)
    
    return selected
```

### 6.2 找零问题

```python
def make_change(amount, coins):
    coins.sort(reverse=True)
    change = []
    
    for coin in coins:
        while amount >= coin:
            change.append(coin)
            amount -= coin
    
    return change if amount == 0 else None
```

## 7. 回溯算法

### 7.1 N皇后问题

```python
def solve_n_queens(n):
    def is_safe(board, row, col):
        for i in range(row):
            if board[i] == col or \
               board[i] - i == col - row or \
               board[i] + i == col + row:
                return False
        return True
    
    def backtrack(board, row):
        if row == n:
            solutions.append(board[:])
            return
        for col in range(n):
            if is_safe(board, row, col):
                board[row] = col
                backtrack(board, row + 1)
                board[row] = -1
    
    solutions = []
    board = [-1] * n
    backtrack(board, 0)
    return solutions
```

### 7.2 全排列

```python
def permutations(nums):
    def backtrack(path, used):
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if not used[i]:
                used[i] = True
                path.append(nums[i])
                backtrack(path, used)
                path.pop()
                used[i] = False
    
    result = []
    backtrack([], [False] * len(nums))
    return result
```

## 8. 图算法

### 8.1 最短路径（Dijkstra）

```python
import heapq

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        if current_dist > distances[current]:
            continue
        for neighbor, weight in graph[current].items():
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances
```

### 8.2 最小生成树（Kruskal）

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        self.parent[self.find(x)] = self.find(y)

def kruskal(edges, n):
    edges.sort(key=lambda x: x[2])
    uf = UnionFind(n)
    mst = []
    
    for u, v, weight in edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            mst.append((u, v, weight))
    
    return mst
```

## 9. 字符串算法

### 9.1 KMP算法

```python
def kmp_search(text, pattern):
    def build_lps(pattern):
        lps = [0] * len(pattern)
        length = 0
        i = 1
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps
    
    lps = build_lps(pattern)
    i = j = 0
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == len(pattern):
            return i - j
        elif i < len(text) and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return -1
```

## 10. 复杂度分析

### 10.1 时间复杂度

- **O(1)**：常数时间
- **O(log n)**：对数时间
- **O(n)**：线性时间
- **O(n log n)**：线性对数时间
- **O(n²)**：平方时间
- **O(2ⁿ)**：指数时间

### 10.2 空间复杂度

- **O(1)**：常数空间
- **O(n)**：线性空间
- **O(n²)**：平方空间

## 11. 总结

Python算法与数据结构：
- **数据结构**：列表、栈、队列、树、图等
- **排序算法**：冒泡、快速、归并等
- **搜索算法**：线性、二分搜索
- **动态规划**：解决最优化问题
- **贪心算法**：局部最优解
- **回溯算法**：解决组合问题

掌握这些算法和数据结构可以提高编程能力和问题解决能力。

## 12. Python 3.14 / 3.15 对算法实现的影响

<!-- version-check: Python 3.14 free-threaded, Python 3.15 frozendict/sentinel, sortedcontainers 2.4.0, checked 2026-05-06 -->

> 🔄 更新于 2026-05-06

### 12.1 Free-threaded Python 3.14：并行算法真正可行

Python 3.14（2025-10）首次把 free-threaded 构建从实验阶段升级为 Phase II 正式支持（[PEP 779](https://peps.python.org/pep-0779/)）。GIL 被完全移除后，`threading.Thread` 可以在 CPU 密集算法上真正并行执行，而不是像以前那样必须切到 `multiprocessing` 才能利用多核。

```python
# Python 3.14t free-threaded 构建上：归并排序的并行版本
# 标准 Python 中线程因 GIL 串行，free-threaded 上可真正并行
import threading
from typing import List


def parallel_merge_sort(arr: List[int], depth: int = 0, max_depth: int = 3) -> List[int]:
    """并行归并排序：前 max_depth 层用线程分治，之后退回串行"""
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2

    if depth < max_depth:
        # 线程并行分治：free-threaded 模式下真正并行执行
        left_result: List[int] = []
        right_result: List[int] = []

        def sort_left() -> None:
            nonlocal left_result
            left_result = parallel_merge_sort(arr[:mid], depth + 1, max_depth)

        def sort_right() -> None:
            nonlocal right_result
            right_result = parallel_merge_sort(arr[mid:], depth + 1, max_depth)

        t1 = threading.Thread(target=sort_left)
        t2 = threading.Thread(target=sort_right)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        return merge(left_result, right_result)
    else:
        # 深度足够后切回串行，避免线程创建开销超过收益
        left = parallel_merge_sort(arr[:mid], depth + 1, max_depth)
        right = parallel_merge_sort(arr[mid:], depth + 1, max_depth)
        return merge(left, right)


def merge(left: List[int], right: List[int]) -> List[int]:
    result: List[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# 检测是否运行在 free-threaded 构建
import sys
if hasattr(sys, "_is_gil_enabled") and not sys._is_gil_enabled():
    print("Running on free-threaded build, threads can truly parallelize.")
```

关键事实（2026 年最新数据）：

- 单线程性能损耗：3.13 下 20-40% → 3.14 下 5-10% → 3.15 alpha 下 6-9%
- 并行任务加速：CPU 密集独立任务可达 4x 加速，能耗同比下降
- 内存开销：约增加 15-20%（对象头需要额外同步字段）
- 陷阱：导入不支持 free-threaded 的 C 扩展会静默重新启用 GIL，需要通过 `sys._is_gil_enabled()` 主动检测

> 来源：[Python 3.14 Free-Threading Benchmarks](https://www.techreviewer.com/developer-news/2025-10-08-python-314-introduces-optional-free-threading-for-multi-core-performance-gains/) ｜ [Python's Free-Threading Mode: Is It Time to Care?](https://www.nandann.com/blog/python-free-threading-2026)

### 12.2 Python 3.15 frozendict：可哈希的不可变映射

Python 3.15 接受了 [PEP 814](https://peps.python.org/pep-0814/)，在 builtins 中提供 `frozendict` 类型。对算法实现而言，最直接的收益是：可以把字典作为其他字典/集合的 key，也可以用作 `functools.lru_cache` 的参数。

```python
# Python 3.15+：用 frozendict 作为 memoization 的 key
from functools import lru_cache


# 以前：dict 不可哈希，需要转成 tuple 或冻结
def state_signature(state: dict) -> tuple:
    return tuple(sorted(state.items()))  # 冗长且每次排序


# Python 3.15+：直接用 frozendict
@lru_cache(maxsize=None)
def solve(state: frozendict) -> int:
    """图搜索中：把节点状态冻结后作为记忆化 key"""
    if is_terminal(state):
        return 0
    return min(
        1 + solve(frozendict(next_state))
        for next_state in expand(state)
    )


# 使用
initial = frozendict({"x": 0, "y": 0, "visited": frozenset()})
answer = solve(initial)
```

注意：`frozendict` 只是 shallow immutable，里面的 mutable value（如嵌套 `list`）仍可被其他线程修改。用于算法题一般没问题，但在多线程场景下需要保证 value 本身也是不可变的。

> 来源：[Real Python: Python Gains frozendict](https://realpython.com/python-news-march-2026/) ｜ [PEP 814 Discussion](https://discuss.python.org/t/pep-814-add-frozendict-built-in-type/104854/126)

### 12.3 Python 3.15 sentinel：类型化哨兵值

[PEP 661](https://peps.python.org/pep-0661/) 在 Python 3.15 中落地，把 `sentinel` 作为 builtin 提供。算法中经常需要区分"没传值"和"传入 None"，以前需要手写模式，现在可以一行搞定。

```python
# Python 3.15+：标准哨兵值
MISSING = sentinel("MISSING")


def binary_search(arr: list[int], target: int, default=MISSING) -> int | object:
    """二分搜索：没找到时返回 default，未指定则返回 MISSING 哨兵"""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return default


# 调用方清晰区分两种情况
result = binary_search([1, 2, 3], 5)
if result is MISSING:
    raise ValueError("target not found and no default provided")
elif result == -1:
    print("not found, using default")
else:
    print(f"found at index {result}")
```

### 12.4 sortedcontainers：纯 Python 但接近 C 扩展的性能

很多场景（滑动窗口最值、在线中位数、按优先级取 top-k）需要有序容器。标准库的 `heapq` 只支持单向堆操作，`bisect` 需要配合 `list` 但插入是 O(n)。

第三方库 [sortedcontainers](https://grantjenks.com/docs/sortedcontainers/)（纯 Python，Apache 2.0）提供 `SortedList` / `SortedDict` / `SortedSet`，底层用分段列表模拟 B-tree，性能接近 C 实现，在 JIT 优化后甚至 2-10x 更快。

```python
from sortedcontainers import SortedList


class MedianFinder:
    """在线求中位数：每次插入 O(log n)，查询 O(1)"""

    def __init__(self) -> None:
        self.data = SortedList()

    def add_num(self, num: int) -> None:
        self.data.add(num)  # O(log n)

    def find_median(self) -> float:
        n = len(self.data)
        if n % 2 == 1:
            return self.data[n // 2]  # O(log n) 索引访问
        return (self.data[n // 2 - 1] + self.data[n // 2]) / 2


# 滑动窗口最大值：标准做法用单调队列 O(n)，
# 但需要支持任意删除时 SortedList 更通用
from collections import deque


def sliding_window_max(nums: list[int], k: int) -> list[int]:
    window: SortedList = SortedList()
    dq: deque = deque()
    result: list[int] = []
    for i, x in enumerate(nums):
        window.add(x)
        dq.append(x)
        if len(dq) > k:
            window.remove(dq.popleft())
        if len(dq) == k:
            result.append(window[-1])  # 最大值
    return result
```

选型建议（2026 年）：

| 需求 | 推荐方案 | 复杂度 |
| ---- | ------ | ---- |
| 找 top-k 最值 | `heapq.nlargest/nsmallest` | O(n log k) |
| 固定大小优先队列 | `heapq` | push/pop O(log n) |
| 在线求中位数、任意位置删除 | `sortedcontainers.SortedList` | O(log n) |
| 有序键值查询 | `sortedcontainers.SortedDict` | O(log n) |
| 需要哈希的不可变状态 | `frozendict`（Python 3.15+） | O(1) 查询 |
| 并行归并/快排/图搜索 | `threading` + Python 3.14t | 真正多核并行 |

> 来源：[Python Sorted Containers](https://grantjenks.com/docs/sortedcontainers/) ｜ [heapq — Heap queue algorithm](https://docs.python.org/3/library/heapq.html)

