# Vue3 基础与组合式 API
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 模板语法

```vue
<template>
  <!-- 文本插值 -->
  <p>{{ message }}</p>

  <!-- 属性绑定 -->
  <div :class="{ active: isActive }" :style="{ color: textColor }">
    <img :src="imageUrl" :alt="imageAlt">
  </div>

  <!-- 条件渲染 -->
  <div v-if="type === 'A'">A</div>
  <div v-else-if="type === 'B'">B</div>
  <div v-else>Other</div>
  <div v-show="isVisible">v-show 只切换 display</div>

  <!-- 列表渲染 -->
  <ul>
    <li v-for="(item, index) in items" :key="item.id">
      {{ index }}: {{ item.name }}
    </li>
  </ul>

  <!-- 事件处理 -->
  <button @click="increment">+1</button>
  <button @click.prevent="handleSubmit">提交</button>
  <input @keyup.enter="search">

  <!-- 双向绑定 -->
  <input v-model="name">
  <input v-model.trim="name">
  <input v-model.number="age" type="number">
</template>
```

## 2. 组合式 API（setup）

```vue
<script setup>
import { ref, reactive, computed, watch, watchEffect, onMounted, onUnmounted } from 'vue';

// ref（基本类型响应式）
const count = ref(0);
const increment = () => count.value++;

// reactive（对象响应式）
const state = reactive({
  name: '张三',
  age: 25,
  address: { city: '北京' },
});

// computed（计算属性）
const doubleCount = computed(() => count.value * 2);

// 可写计算属性
const fullName = computed({
  get: () => `${state.firstName} ${state.lastName}`,
  set: (val) => {
    const [first, last] = val.split(' ');
    state.firstName = first;
    state.lastName = last;
  },
});

// watch（侦听器）
watch(count, (newVal, oldVal) => {
  console.log(`count: ${oldVal} → ${newVal}`);
});

// 侦听多个源
watch([count, () => state.name], ([newCount, newName]) => {
  console.log(newCount, newName);
});

// 深度侦听
watch(() => state.address, (newAddr) => {
  console.log('地址变化:', newAddr);
}, { deep: true });

// watchEffect（自动收集依赖）
watchEffect(() => {
  console.log(`count is ${count.value}, name is ${state.name}`);
});

// 生命周期
onMounted(() => { console.log('组件挂载'); });
onUnmounted(() => { console.log('组件卸载'); });
</script>
```

## 3. 组件通信

```vue
<!-- 父组件 -->
<template>
  <Child :title="title" :count="count" @update="handleUpdate" />
</template>

<!-- 子组件 Child.vue -->
<script setup>
// Props
const props = defineProps({
  title: { type: String, required: true },
  count: { type: Number, default: 0 },
});

// Emits
const emit = defineEmits(['update']);
const handleClick = () => emit('update', { id: 1, value: 'new' });

// v-model 双向绑定
const model = defineModel(); // Vue 3.4+

// provide / inject（跨层级通信）
import { provide, inject } from 'vue';

// 祖先组件
provide('theme', ref('dark'));

// 后代组件
const theme = inject('theme', 'light'); // 第二个参数是默认值
</script>
```

## 4. 模板引用

```vue
<script setup>
import { ref, onMounted } from 'vue';

const inputRef = ref(null);

onMounted(() => {
  inputRef.value?.focus();
});
</script>

<template>
  <input ref="inputRef" />
</template>
```

## 5. Composables（组合式函数）

```javascript
// composables/useMouse.js
import { ref, onMounted, onUnmounted } from 'vue';

export function useMouse() {
  const x = ref(0);
  const y = ref(0);

  const update = (e) => {
    x.value = e.pageX;
    y.value = e.pageY;
  };

  onMounted(() => window.addEventListener('mousemove', update));
  onUnmounted(() => window.removeEventListener('mousemove', update));

  return { x, y };
}

// composables/useFetch.js
import { ref, watchEffect } from 'vue';

export function useFetch(url) {
  const data = ref(null);
  const error = ref(null);
  const loading = ref(true);

  watchEffect(async () => {
    loading.value = true;
    try {
      const res = await fetch(url.value || url);
      data.value = await res.json();
    } catch (e) {
      error.value = e;
    } finally {
      loading.value = false;
    }
  });

  return { data, error, loading };
}

// 使用
const { x, y } = useMouse();
const { data, loading } = useFetch('/api/users');
```

## 6. Vue 3.5/3.6 新特性

> 🔄 更新于 2026-05-13

<!-- version-check: Vue 3.5.33 (stable), Vue 3.6 (beta), checked 2026-05-13 -->

<!-- 修复于 2026-05-13: Vue 3.5.28 → 3.5.33，eosl.date 确认 -->

**Vue 3.5**（当前稳定版 3.5.33）：性能优化、SSR 兼容性修复、HMR 改进。

**Vue 3.6**（Beta）：两个革命性特性：

### Vapor Mode（无虚拟 DOM 编译模式）

Vapor Mode 跳过 Virtual DOM diffing，直接编译为 DOM 操作，渲染性能提升 3-5x，接近 Solid.js 水平：

```vue
<!-- 使用 Vapor Mode 的组件（编译时自动优化，无需改代码） -->
<script setup>
import { ref } from 'vue';
const count = ref(0);
</script>

<template>
  <!-- Vapor Mode 下，这段模板直接编译为 DOM 操作，不经过 Virtual DOM -->
  <button @click="count++">{{ count }}</button>
</template>
```

### Alien Signals（新响应式引擎）

Vue 3.6 重构了响应式系统，采用 alien-signals 算法，响应式追踪和触发性能大幅提升。

来源：[Vue.js 2025 回顾与 2026 展望](https://vueschool.io/articles/news/vue-js-2025-in-review-and-a-peek-into-2026/)、[State of Vue & Vite 2026](https://laurentcazanove.com/blog/state-of-vue-vite-2026-amsterdam-recap)
## 🎬 推荐视频资源

- [freeCodeCamp - Vue 3 Full Course](https://www.youtube.com/watch?v=VeNfHj6MhgA) — Vue 3完整课程（6小时）
- [Traversy Media - Vue.js Crash Course](https://www.youtube.com/watch?v=qZXt1Aom3Cs) — Vue速成
- [Fireship - Vue.js in 100 Seconds](https://www.youtube.com/watch?v=nhBVL41-_Cw) — Vue快速了解
### 📺 B站（Bilibili）
- [尚硅谷 - Vue3完整教程](https://www.bilibili.com/video/BV1Za4y1r7KE) — Vue3完整中文教程
- [黑马程序员 - Vue3教程](https://www.bilibili.com/video/BV1HV4y1a7n4) — Vue3项目实战
- [coderwhy - Vue3+TS](https://www.bilibili.com/video/BV1WP4y187Tu) — Vue3+TypeScript深入

### 🌐 其他平台
- [Vue3官方中文文档](https://cn.vuejs.org/) — 官方中文文档
