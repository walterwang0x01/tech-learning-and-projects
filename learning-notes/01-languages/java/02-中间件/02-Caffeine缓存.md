# Caffeine
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

### 1. What is [caffeine](https://github.com/ben-manes/caffeine)?

#### 1.1 Caffeine简介
Caffeine 是基于 Java 8 的高性能，接近最佳的缓存库。

Caffeine 使用 Google Guava 启发的 API 提供内存缓存。 改进取决于您设计 Guava 缓存和 ConcurrentLinkedHashMap 的体验。
~~~java
LoadingCache<Key, Graph> graphs = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(Duration.ofMinutes(5))
    .refreshAfterWrite(Duration.ofMinutes(1))
    .build(key -> createExpensiveGraph(key));
~~~

#### 1.2 功能一览
Caffeine 提供了灵活的构造来创建具有以下功能组合的缓存：

- 自动将条目自动加载到缓存中，可以选择异步加载
- 基于频率和新近度超过最大值时基于大小的逐出
- 自上次访问或上次写入以来测得的基于时间的条目到期
- 发生第一个陈旧的条目请求时，异步刷新
- 键自动包装在弱引用中
- 值自动包装在弱引用或软引用中
- 逐出（或以其他方式删除）条目的通知
- 写入传播到外部资源
- 缓存访问统计信息的累积

### 2 使用方式

#### 2.1 配置文件方式
不够灵活，多缓存配置文件很长。

- properties
```properties
spring.cache.cache-names=cacheOne
spring.cache.caffeine.spec=initialCapacity=50,maximumSize=500,expireAfterWrite=10s
```

- Yaml文件
```yaml
spring:
  cache:
    type: caffeine
    cache-names:
    - cacheOne
    caffeine:
      spec: maximumSize=5000,refreshAfterWrite=60s
```

#### 2.2 配置类方式
不够配置化，增删缓存需要硬编码。

```java
@Configuration
public class CacheConfig {

    /**
     * 创建基于Caffeine的Cache Manager
     *        
     * @return
     */
    @Bean
    @Primary
    public CacheManager caffeineCacheManager() {
        SimpleCacheManager cacheManager = new SimpleCacheManager();
        ArrayList<CaffeineCache> caches = Lists.newArrayList();
        List<CacheObject> list = setCacheObjects();
        for(CacheObject cacheObject : list){
            caches.add(new CaffeineCache(cacheObject.getKey(),
                    Caffeine.newBuilder().recordStats()
                            .expireAfterWrite(cacheObject.getTtl(), TimeUnit.SECONDS)
                            .maximumSize(cacheObject.getMaximumSize())
                            .build()));
        }
        cacheManager.setCaches(caches);
        return cacheManager;
    }


    /**
     * 添加缓存对象
     *
     * @return
     */
    private List<CacheObject> setCacheObjects(){

        List<CacheObject> list = Lists.newArrayList();
        CacheObject userCache = new CacheObject();
        userCache.setKey("userCache");
        userCache.setTtl(60);
        userCache.setMaximumSize(10000);

        CacheObject sysCfnCache = new cacheObject();
        sysCfnCache.setKey("sysCfnCache");
        sysCfnCache.setTtl(60);
        sysCfnCache.setMaximumSize(10000);

        list.add(userCache);
        list.add(deptCache);

        return list;
    }

    @Data    
    class CacheObject {
        private String key;
        private long ttl;
        private long maximumSize;
    }

}
```
#### 2.3 基于 **W-TinyLFU** 设计
caffeine 基于 **W-TinyLFU** 设计，包含三种加载方法和一个过期策略。
1. 加载方法（手动、同步、异步）
```java
1.手动
Cache<String, Object> cache = Caffeine.newBuilder().build();

2.同步 
//默认的数据加载实现，当调用get取值的时候，如果key没有对应的值，就调用自定义方法 getValue 进行加载
LoadingCache<String, Object> cache = Caffeine.newBuilder().build(k -> getValue(key));

3.异步
//AsyncLoadingCache是继承自LoadingCache类的，异步加载使用Executor去调用方法并返回一个CompletableFuture。异步加载缓存使用了响应式编程模型。
AsyncLoadingCache<String, Object> cache = Caffeine.newBuilder().buildAsync(k -> getAsyncValue(key).get());
```
2. 过期策略
```java
1. 基于大小的过期方式
基于大小的回收策略有两种方式：一种是基于缓存大小，一种是基于权重。

// 根据缓存的计数进行驱逐
LoadingCache<String, Object> cache = Caffeine.newBuilder()
    .maximumSize(10000)
    .build(key -> function(key));

// 根据缓存的权重来进行驱逐（权重只是用于确定缓存大小，不会用于决定该缓存是否被驱逐）
LoadingCache<String, Object> cache1 = Caffeine.newBuilder()
    .maximumWeight(10000)
    .weigher(key -> function1(key))
    .build(key -> function(key));
maximumWeight与maximumSize不可以同时使用。

2.基于时间的过期方式
// 基于固定的到期策略进行退出
LoadingCache<String, Object> cache = Caffeine.newBuilder()
    .expireAfterAccess(5, TimeUnit.MINUTES)
    .build(key -> function(key));
LoadingCache<String, Object> cache1 = Caffeine.newBuilder()
    .expireAfterWrite(10, TimeUnit.MINUTES)
    .build(key -> function(key));

// 基于不同的到期策略进行退出
LoadingCache<String, Object> cache2 = Caffeine.newBuilder()
    .expireAfter(new Expiry<String, Object>() {
        @Override
        public long expireAfterCreate(String key, Object value, long currentTime) {
            return TimeUnit.SECONDS.toNanos(seconds);
        }

        @Override
        public long expireAfterUpdate(@Nonnull String s, @Nonnull Object o, long l, long l1) {
            return 0;
        }

        @Override
        public long expireAfterRead(@Nonnull String s, @Nonnull Object o, long l, long l1) {
            return 0;
        }
    }).build(key -> function(key));

Caffeine提供了三种定时驱逐策略：
expireAfterAccess(long, TimeUnit):在最后一次访问或者写入后开始计时，在指定的时间后过期。假如一直有请求访问该key，那么这个缓存将一直不会过期。
expireAfterWrite(long, TimeUnit): 在最后一次写入缓存后开始计时，在指定的时间后过期。
expireAfter(Expiry): 自定义策略，过期时间由Expiry实现独自计算。
缓存的删除策略使用的是惰性删除和定时删除。这两个删除策略的时间复杂度都是O(1)。

3. 基于引用的过期方式
Java中四种引用类型

引用类型	  被垃圾回收时间	  用途	        生存时间
强引用     Strong          Reference	从来不会	对象的一般状态	JVM停止运行时终止
软引用     Soft            Reference	在内存不足时	对象缓存	内存不足时终止
弱引用     Weak            Reference	在垃圾回收时	对象缓存	gc运行后终止
虚引用     Phantom         Reference	从来不会	可以用虚引用来跟踪对象被垃圾回收器回收的活动，当一个虚引用关联的对象被垃圾收集器回收之前会收到一条系统通知	JVM停止运行时终止
// 当key和value都没有引用时驱逐缓存
LoadingCache<String, Object> cache = Caffeine.newBuilder()
    .weakKeys()
    .weakValues()
    .build(key -> function(key));

// 当垃圾收集器需要释放内存时驱逐
LoadingCache<String, Object> cache1 = Caffeine.newBuilder()
    .softValues()
    .build(key -> function(key));
注意：AsyncLoadingCache不支持弱引用和软引用。

Caffeine.weakKeys()： 使用弱引用存储key。如果没有其他地方对该key有强引用，那么该缓存就会被垃圾回收器回收。由于垃圾回收器只依赖于身份(identity)相等，因此这会导致整个缓存使用身份 (==) 相等来比较 key，而不是使用 equals()。

Caffeine.weakValues() ：使用弱引用存储value。如果没有其他地方对该value有强引用，那么该缓存就会被垃圾回收器回收。由于垃圾回收器只依赖于身份(identity)相等，因此这会导致整个缓存使用身份 (==) 相等来比较 key，而不是使用 equals()。

Caffeine.softValues() ：使用软引用存储value。当内存满了过后，软引用的对象以将使用最近最少使用(least-recently-used ) 的方式进行垃圾回收。由于使用软引用是需要等到内存满了才进行回收，所以我们通常建议给缓存配置一个使用内存的最大值。 softValues() 将使用身份相等(identity) (==) 而不是equals() 来比较值。

Caffeine.weakValues()和Caffeine.softValues()不可以一起使用。
```

### 3 caffeine加强

#### 特点
- 结合配置文件和配置类灵活配置缓存
- 提供常用方法工具类 CacheUtil
- 与caffeine共存，互为补充
- spring boot auto config自动扫描配置

#### 使用要求
- 0.1版本仅支持spring boot项目
- JDK1.8+
- 配置文件限定只能使用路径`resources/config/cache.yml`

#### 使用方法
##### 配置文件示例
```yaml
cache:
  caffeine-plus:
    # 需要配置true启用缓存，默认为false
    enabled: true
    # 全局配置
    cacheName: beanCache,beanCache2
    spec: maximumSize=500,expireAfterWrite=60s
    # 自定义配置，cacheName相同会覆盖全局配置
    configs:
      - cacheName: sessionCache
        spec: maximumSize=200
      - cacheName: userCache
        spec: maximumSize=200
```
cacheName 为缓存bean名称  
spec 为缓存初始化参数，参数名同[caffeine](https://github.com/ben-manes/caffeine)框架参数
> **Caffeine常用配置说明：**
> 
> initialCapacity=[integer]: 初始的缓存空间大小
> 
> maximumSize=[long]: 缓存的最大条数
> 
> maximumWeight=[long]: 缓存的最大权重
> 
> expireAfterAccess=[duration]: 最后一次写入或访问后经过固定时间过期
> 
> expireAfterWrite=[duration]: 最后一次写入后经过固定时间过期
> 
> refreshAfterWrite=[duration]: 创建缓存或者最近一次更新缓存后经过固定的时间间隔，刷新缓存
> 
> weakKeys: 打开key的弱引用
> 
> weakValues：打开value的弱引用
> 
> softValues：打开value的软引用
> 
> recordStats：开发统计功能
> 
> **注意：**
> 
> expireAfterWrite和expireAfterAccess同时存在时，以expireAfterWrite为准。
> 
> maximumSize和maximumWeight不可以同时使用
> 
> weakValues和softValues不可以同时使用

##### 注解使用
cache方面的注解主要有以下5个：

- @Cacheable 触发缓存入口（这里一般放在创建和获取的方法上，@Cacheable注解会先查询是否已经有缓存，有会使用缓存，没有则会执行方法并缓存）
- @CacheEvict 触发缓存的eviction（用于删除的方法上）
- @CachePut 更新缓存且不影响方法执行（用于修改的方法上，该注解下的方法始终会被执行）
- @Caching 将多个缓存组合在一个方法上（该注解可以允许一个方法同时设置多个注解）
- @CacheConfig 在类级别设置一些缓存相关的共同配置（与其它缓存配合使用）

**说一下@Cacheable 和 @CachePut的区别：**
- @Cacheable：它的注解的方法是否被执行取决于Cacheable中的条件，方法很多时候都可能不被执行。
- @CachePut：这个注解不会影响方法的执行，也就是说无论它配置的条件是什么，方法都会被执行，更多的时候是被用到修改上。

##### 工具类使用
下边提供常用方法示例，其他方法可参考项目源码。
```java
@SpringBootTest
@RunWith(SpringRunner.class)
@Slf4j
public class CacheTest {

    @Autowired
    private CacheUtil cacheUtil;

    @Autowired
    private ConfigSystemInfoService configSystemInfoService;

    @Test
    public void testExpireCache() {

        // 查询数据库
        log.info(configSystemInfoServiceImpl.selectByCode("001").getValue());

        // 查询缓存, 验证注解缓存生效
        log.info(configSystemInfoServiceImpl.selectByCode("001").getValue());

        // 主动使用缓存
        cacheUtil.putCache("beanCache", "sex", "female");
        log.info("{}", cacheUtil.getCacheValue("beanCache", "sex"));

        // 主动更新缓存
        cacheUtil.putCache("beanCache", "sex", "male");
        log.info("{}", cacheUtil.getCacheValue("beanCache", "sex"));

        // 睡眠时间大于缓存有效时间
        try {
            Thread.sleep(8000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        // 查询数据库，验证缓存失效
        log.info(configSystemInfoServiceImpl.selectByCode("001").getValue());

        // 缓存超时，查询结果为null
        log.info("{}", cacheUtil.getCacheValue("beanCache", "sex"));

        // 新增缓存，查询正常
        cacheUtil.putCache("beanCache", "sex", "male");
        log.info("{}", cacheUtil.getCacheValue("beanCache", "sex"));
    }

}
```




