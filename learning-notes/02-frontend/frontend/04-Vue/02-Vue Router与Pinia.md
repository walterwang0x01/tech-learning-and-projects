# Vue Router 与 Pinia
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Vue Router 配置

```javascript
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('./views/Home.vue') },
    { path: '/about', component: () => import('./views/About.vue') },
    {
      path: '/users',
      component: () => import('./views/Users.vue'),
      children: [
        { path: ':id', component: () => import('./views/UserDetail.vue'), props: true },
      ],
    },
    { path: '/:pathMatch(.*)*', component: () => import('./views/NotFound.vue') },
  ],
});

// 导航守卫
router.beforeEach((to, from) => {
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } };
  }
});

export default router;
```

## 2. 路由使用

```vue
<script setup>
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();     // 当前路由信息
const router = useRouter();   // 路由实例

// 路径参数
const userId = route.params.id;

// 查询参数
const page = route.query.page;

// 编程式导航
router.push('/users');
router.push({ name: 'user', params: { id: 1 } });
router.replace('/home');
router.go(-1);
</script>

<template>
  <RouterLink to="/">首页</RouterLink>
  <RouterLink :to="{ name: 'user', params: { id: 1 } }">用户</RouterLink>
  <RouterView /> <!-- 路由出口 -->
</template>
```

## 3. Pinia 状态管理

```javascript
// stores/counter.js
import { defineStore } from 'pinia';

export const useCounterStore = defineStore('counter', () => {
  // State
  const count = ref(0);
  const name = ref('张三');

  // Getters（computed）
  const doubleCount = computed(() => count.value * 2);

  // Actions
  function increment() { count.value++; }
  async function fetchCount() {
    const res = await fetch('/api/count');
    const data = await res.json();
    count.value = data.count;
  }

  return { count, name, doubleCount, increment, fetchCount };
});
```

```vue
<!-- 组件中使用 -->
<script setup>
import { useCounterStore } from '@/stores/counter';
import { storeToRefs } from 'pinia';

const store = useCounterStore();

// storeToRefs 保持响应式（解构 state 和 getters）
const { count, doubleCount } = storeToRefs(store);

// actions 直接解构
const { increment, fetchCount } = store;

// 批量修改
store.$patch({ count: 10, name: '李四' });

// 重置
store.$reset();

// 订阅变化
store.$subscribe((mutation, state) => {
  localStorage.setItem('counter', JSON.stringify(state));
});
</script>
```

## 4. Pinia 插件

```javascript
// 持久化插件
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

// Store 中启用持久化
export const useUserStore = defineStore('user', () => {
  const token = ref('');
  const user = ref(null);
  return { token, user };
}, {
  persist: {
    key: 'user-store',
    storage: localStorage,
    pick: ['token'], // 只持久化 token
  },
});
```
