# Java并发编程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 线程基础

### 1.1 线程的创建

#### 方式一：继承Thread类

```java
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("线程执行");
    }
}

MyThread thread = new MyThread();
thread.start();
```

#### 方式二：实现Runnable接口

```java
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("线程执行");
    }
}

Thread thread = new Thread(new MyRunnable());
thread.start();
```

#### 方式三：实现Callable接口

```java
class MyCallable implements Callable<String> {
    @Override
    public String call() throws Exception {
        return "线程执行结果";
    }
}

FutureTask<String> futureTask = new FutureTask<>(new MyCallable());
Thread thread = new Thread(futureTask);
thread.start();
String result = futureTask.get();
```

### 1.2 run()与start()的区别

- **run()方法**：不会开启新线程，还在main线程运行，只是普通的方法调用
- **start()方法**：会开启一个新线程，在新的线程中执行run()方法

### 1.3 线程状态

- **NEW**：新建状态，线程被创建但尚未启动
- **RUNNABLE**：可运行状态，线程正在JVM中执行
- **BLOCKED**：阻塞状态，线程被阻塞等待监视器锁
- **WAITING**：等待状态，线程无限期等待另一个线程执行特定操作
- **TIMED_WAITING**：超时等待状态，线程在指定时间内等待
- **TERMINATED**：终止状态，线程已执行完毕

## 2. 线程同步

### 2.1 synchronized关键字

#### 2.1.1 同步方法

```java
public synchronized void method() {
    // 同步代码
}
```

#### 2.1.2 同步代码块

```java
synchronized (object) {
    // 同步代码
}
```

#### 2.1.3 同步静态方法

```java
public static synchronized void method() {
    // 同步代码
}
```

### 2.2 Lock接口

#### 2.2.1 ReentrantLock

```java
Lock lock = new ReentrantLock();
try {
    lock.lock();
    // 同步代码
} finally {
    lock.unlock();
}
```

#### 2.2.2 ReadWriteLock

```java
ReadWriteLock readWriteLock = new ReentrantReadWriteLock();
Lock readLock = readWriteLock.readLock();
Lock writeLock = readWriteLock.writeLock();
```

### 2.3 synchronized与Lock的区别

| 特性 | synchronized | Lock |
|------|-------------|------|
| 类型 | Java关键字 | 接口 |
| 锁释放 | 自动释放 | 手动释放 |
| 可中断性 | 不可中断 | 可中断 |
| 公平性 | 非公平锁 | 可设置为公平锁 |
| 锁获取 | 无法知道是否获取到锁 | 可以知道是否获取到锁 |
| 使用范围 | 方法和代码块 | 只能用于代码块 |
| 性能 | 在JDK 1.6后优化，性能相当 | 性能相当 |

### 2.4 volatile关键字

- **作用**：保证变量的可见性，防止指令重排序
- **特点**：
  - 解决的是变量在多个线程之间的可见性
  - 无法保证原子性
  - 禁止指令重排序优化

```java
private volatile boolean flag = false;
```

## 3. 线程池

### 3.1 线程池的优势

1. **降低资源消耗**：通过重复利用已创建的线程降低线程创建和销毁造成的消耗
2. **提高响应速度**：当任务到达时，任务可以不需要等到线程创建就能立即执行
3. **提高线程的可管理性**：线程是稀缺资源，如果无限制地创建，不仅会消耗系统资源，还会降低系统的稳定性

### 3.2 线程池参数

ThreadPoolExecutor的七大参数：

1. **corePoolSize**：核心线程数
2. **maximumPoolSize**：最大线程数
3. **keepAliveTime**：线程存活时间
4. **unit**：时间单位
5. **workQueue**：阻塞队列
6. **threadFactory**：线程创建工厂
7. **handler**：拒绝策略

### 3.3 线程池执行流程

1. 提交任务时，如果当前线程数小于corePoolSize，创建新线程执行任务
2. 如果当前线程数等于corePoolSize，将任务放入阻塞队列
3. 如果阻塞队列已满，且当前线程数小于maximumPoolSize，创建新线程执行任务
4. 如果阻塞队列已满，且当前线程数等于maximumPoolSize，执行拒绝策略

### 3.4 拒绝策略

- **AbortPolicy**：直接抛出异常（默认）
- **CallerRunsPolicy**：调用者运行策略，在调用者线程中执行任务
- **DiscardPolicy**：直接丢弃任务
- **DiscardOldestPolicy**：丢弃队列中最老的任务，然后重新提交当前任务

### 3.5 Executors提供的线程池

#### 3.5.1 newCachedThreadPool

```java
ExecutorService executor = Executors.newCachedThreadPool();
```

- **特点**：创建一个可缓存线程池，如果线程池长度超过处理需要，可灵活回收空闲线程，若无可回收，则新建线程

#### 3.5.2 newFixedThreadPool

```java
ExecutorService executor = Executors.newFixedThreadPool(10);
```

- **特点**：创建一个定长线程池，可控制线程最大并发数，超出的线程会在队列中等待

#### 3.5.3 newScheduledThreadPool

```java
ScheduledExecutorService executor = Executors.newScheduledThreadPool(10);
```

- **特点**：创建一个定长线程池，支持定时及周期性任务执行

#### 3.5.4 newSingleThreadExecutor

```java
ExecutorService executor = Executors.newSingleThreadExecutor();
```

- **特点**：创建一个单线程化的线程池，它只会用唯一的工作线程来执行任务，保证所有任务按照指定顺序(FIFO, LIFO, 优先级)执行

### 3.6 自定义线程池

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    5,                              // 核心线程数
    10,                             // 最大线程数
    60L,                            // 存活时间
    TimeUnit.SECONDS,               // 时间单位
    new LinkedBlockingQueue<>(100), // 阻塞队列
    new ThreadFactory() {           // 线程工厂
        @Override
        public Thread newThread(Runnable r) {
            Thread thread = new Thread(r);
            thread.setName("my-thread-" + thread.getId());
            return thread;
        }
    },
    new ThreadPoolExecutor.CallerRunsPolicy() // 拒绝策略
);
```

## 4. 并发集合

### 4.1 ConcurrentHashMap

- **特点**：线程安全的HashMap
- **实现原理**：
  - JDK 1.7：使用分段锁(Segment)
  - JDK 1.8：使用CAS + synchronized，底层使用数组+链表+红黑树

```java
Map<String, Object> map = new ConcurrentHashMap<>();
```

### 4.2 CopyOnWriteArrayList

- **特点**：线程安全的ArrayList
- **实现原理**：写时复制，读操作不加锁，写操作时复制一份新的数组

```java
List<String> list = new CopyOnWriteArrayList<>();
```

### 4.3 BlockingQueue

#### 4.3.1 ArrayBlockingQueue

```java
BlockingQueue<String> queue = new ArrayBlockingQueue<>(10);
```

#### 4.3.2 LinkedBlockingQueue

```java
BlockingQueue<String> queue = new LinkedBlockingQueue<>();
```

#### 4.3.3 SynchronousQueue

```java
BlockingQueue<String> queue = new SynchronousQueue<>();
```

### 4.4 线程安全的Map对比

| 类型 | 特点 | 性能 | 推荐度 |
|------|------|------|--------|
| HashMap | 线程不安全 | 高 | 单线程使用 |
| Hashtable | 线程安全，方法级同步 | 低 | 不推荐 |
| Collections.synchronizedMap | 线程安全，对象锁 | 低 | 不推荐 |
| ConcurrentHashMap | 线程安全，分段锁/CAS | 高 | 推荐 |

## 5. 原子类

### 5.1 AtomicInteger

```java
AtomicInteger count = new AtomicInteger(0);
count.incrementAndGet();  // 原子性自增
count.getAndIncrement();  // 先获取后自增
```

### 5.2 AtomicLong

```java
AtomicLong count = new AtomicLong(0);
```

### 5.3 AtomicReference

```java
AtomicReference<String> ref = new AtomicReference<>("初始值");
```

## 6. CAS (Compare And Swap)

### 6.1 CAS原理

- **比较并交换**：比较内存中的值与期望值，如果相同则更新为新值
- **原子性**：通过CPU的原子指令实现
- **乐观锁**：假设没有冲突，如果有冲突则重试

### 6.2 CAS的问题

1. **ABA问题**：值从A变成B再变回A，CAS无法检测到变化
   - **解决**：使用版本号，AtomicStampedReference
2. **循环时间长开销大**：如果CAS失败，会一直重试
3. **只能保证一个共享变量的原子操作**
   - **解决**：使用AtomicReference包装多个变量

## 7. 锁的分类

### 7.1 乐观锁与悲观锁

- **乐观锁**：假设没有冲突，使用CAS实现
- **悲观锁**：假设会有冲突，使用synchronized和ReentrantLock实现

### 7.2 公平锁与非公平锁

- **公平锁**：按照线程等待时间顺序获取锁
- **非公平锁**：不按照等待时间顺序，可能造成线程饥饿

### 7.3 可重入锁

- **特点**：同一个线程可以多次获取同一把锁
- **实现**：synchronized和ReentrantLock都是可重入锁

### 7.4 读写锁

- **读锁**：共享锁，多个线程可以同时获取
- **写锁**：排他锁，同一时间只能有一个线程获取

## 8. 并发工具类

### 8.1 CountDownLatch

```java
CountDownLatch latch = new CountDownLatch(3);
// 等待3个线程完成
latch.await();
// 每个线程完成后调用
latch.countDown();
```

### 8.2 CyclicBarrier

```java
CyclicBarrier barrier = new CyclicBarrier(3);
// 等待3个线程都到达屏障
barrier.await();
```

### 8.3 Semaphore

```java
Semaphore semaphore = new Semaphore(3);
// 获取许可
semaphore.acquire();
// 释放许可
semaphore.release();
```

### 8.4 Exchanger

```java
Exchanger<String> exchanger = new Exchanger<>();
// 交换数据
String data = exchanger.exchange("数据");
```

## 9. CompletableFuture

### 9.1 基本使用

```java
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
    return "结果";
});

String result = future.get();
```

### 9.2 链式调用

```java
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> "Hello")
    .thenApply(s -> s + " World")
    .thenApply(String::toUpperCase);
```

### 9.3 组合多个Future

```java
CompletableFuture<String> future1 = CompletableFuture.supplyAsync(() -> "结果1");
CompletableFuture<String> future2 = CompletableFuture.supplyAsync(() -> "结果2");

CompletableFuture<String> combined = future1.thenCombine(future2, (r1, r2) -> r1 + r2);
```

## 10. 并发场景应用

### 10.1 秒杀系统

- 使用线程池处理并发请求
- 使用分布式锁保证库存一致性
- 使用消息队列削峰填谷

### 10.2 12306抢票

- 使用乐观锁处理并发购票
- 使用队列处理高并发请求
- 使用缓存提高查询性能

## 11. 并发编程最佳实践

1. **使用线程池**：避免频繁创建和销毁线程
2. **合理设置线程池参数**：根据业务场景设置核心线程数和最大线程数
3. **使用并发集合**：优先使用ConcurrentHashMap等并发集合
4. **避免死锁**：按相同顺序获取锁，设置锁超时时间
5. **使用volatile保证可见性**：多线程共享变量使用volatile
6. **使用原子类**：简单操作使用AtomicInteger等原子类
7. **避免过度同步**：只在必要时使用同步
8. **使用CompletableFuture**：处理异步任务和组合多个异步操作
## 🎬 推荐视频资源

- [Jakob Jenkov - Java Concurrency](https://www.youtube.com/playlist?list=PLL8woMHwr36EDxjUoCzboZjedsnhLP1j4) — Java并发编程完整系列
- [Defog Tech - Java Multithreading](https://www.youtube.com/playlist?list=PLhfHPmPYPPRk6yMrcbfafFGSbE2EPK_A6) — Java多线程教程
### 📺 B站（Bilibili）
- [黑马程序员 - Java并发编程](https://www.bilibili.com/video/BV16J411h7Rd) — Java并发完整教程
- [尚硅谷 - JUC并发编程](https://www.bilibili.com/video/BV1Kw411Z7dF) — JUC深入讲解
