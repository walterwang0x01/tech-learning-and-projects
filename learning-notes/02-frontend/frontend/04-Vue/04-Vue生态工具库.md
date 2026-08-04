# Vue 生态工具库
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Nuxt3（SSR/SSG）

> 🔄 更新于 2026-07-09：Nuxt 4 已稳定发布（当前 v4.4.8），Nuxt 3 将于 2026-07-31 EOL。新项目应使用 Nuxt 4。

<!-- version-check: Nuxt 4.4.8, checked 2026-07-09 -->
<!-- 修复于 2026-07-09: 4.4.3 → 4.4.8（npm 实测） -->

**Nuxt 4 核心变化**（相比 Nuxt 3）：
- Vue Router 5 集成
- 自定义数据获取实例
- 构建和运行时性能提升
- Nuxt 3 → 4 迁移：`npx nuxi upgrade --force`

来源：[Nuxt 4.3 发布公告](https://nuxt.com/blog/v4-3)、[State of Vue & Vite 2026](https://laurentcazanove.com/blog/state-of-vue-vite-2026-amsterdam-recap)

```javascript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@pinia/nuxt', '@nuxtjs/tailwindcss'],
  runtimeConfig: {
    apiSecret: '',
    public: { apiBase: '/api' },
  },
});

// pages/index.vue（文件系统路由）
<script setup>
const { data } = await useFetch('/api/users');
</script>

// server/api/hello.ts（服务端API）
export default defineEventHandler((event) => {
  return { message: 'Hello from Nuxt server' };
});

// 数据获取
const { data, pending, error, refresh } = await useFetch('/api/data');
const { data } = await useAsyncData('key', () => $fetch('/api/data'));
```

## 2. VueUse 工具集

```javascript
import {
  useMouse,           // 鼠标位置
  useLocalStorage,    // localStorage 响应式
  useDark,            // 暗色模式
  useDebounce,        // 防抖
  useThrottle,        // 节流
  useIntersectionObserver, // 元素可见性
  useClipboard,       // 剪贴板
  useEventListener,   // 事件监听（自动清理）
  useMediaQuery,      // 媒体查询
  useFetch,           // 数据获取
} from '@vueuse/core';

// 示例
const { x, y } = useMouse();
const isDark = useDark();
const stored = useLocalStorage('key', 'default');
const { copy, isSupported } = useClipboard();
const isMobile = useMediaQuery('(max-width: 768px)');
```

## 3. UI 组件库

```javascript
// Element Plus
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
app.use(ElementPlus);

// 按需导入（推荐）
import { ElButton, ElInput, ElTable } from 'element-plus';

// Ant Design Vue
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/reset.css';
app.use(Antd);
```

## 4. unplugin 自动导入

```javascript
// vite.config.ts
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router', 'pinia'],
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
});

// 无需手动 import，直接使用
// const count = ref(0);
// const router = useRouter();
```

## 5. Vitest 测试

```javascript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
  },
});

// Counter.test.ts
import { mount } from '@vue/test-utils';
import Counter from './Counter.vue';

describe('Counter', () => {
  it('increments count on click', async () => {
    const wrapper = mount(Counter);
    await wrapper.find('button').trigger('click');
    expect(wrapper.text()).toContain('1');
  });
});
```
