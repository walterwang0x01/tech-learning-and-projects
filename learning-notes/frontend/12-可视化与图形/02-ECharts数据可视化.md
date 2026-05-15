# ECharts 数据可视化
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 基本使用

```javascript
import * as echarts from 'echarts';

const chart = echarts.init(document.getElementById('chart'));

chart.setOption({
  title: { text: '销售数据' },
  tooltip: { trigger: 'axis' },
  legend: { data: ['销量', '利润'] },
  xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月'] },
  yAxis: { type: 'value' },
  series: [
    { name: '销量', type: 'bar', data: [120, 200, 150, 80, 70] },
    { name: '利润', type: 'line', data: [50, 80, 60, 30, 25] },
  ],
});

// 响应式
window.addEventListener('resize', () => chart.resize());
```

## 2. 常用图表

```javascript
// 饼图
{
  series: [{
    type: 'pie',
    radius: ['40%', '70%'], // 环形图
    data: [
      { value: 1048, name: '搜索引擎' },
      { value: 735, name: '直接访问' },
      { value: 580, name: '邮件营销' },
    ],
  }],
}

// 散点图
{
  xAxis: { type: 'value' },
  yAxis: { type: 'value' },
  series: [{
    type: 'scatter',
    symbolSize: (data) => Math.sqrt(data[2]) * 5,
    data: [[10, 8, 100], [20, 15, 200], [30, 25, 300]],
  }],
}
```

## 3. React/Vue 集成

> ⚠️ **注意**：`echarts-for-react`（hustcc/echarts-for-react）已在 npm 标记为 deprecated（最后版本 3.0.2，2025-03-05），不再维护。新项目推荐以下替代方案。
>
> <!-- 修复于 2026-05-15: echarts-for-react 已被 npm 标记为 deprecated，添加替代方案 -->

```jsx
// 方案 1：直接使用 echarts（推荐，无封装层）
import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

function Chart({ data }) {
  const ref = useRef(null);

  useEffect(() => {
    const chart = echarts.init(ref.current);
    chart.setOption({
      xAxis: { type: 'category', data: data.map(d => d.name) },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: data.map(d => d.value) }],
    });

    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.dispose();
    };
  }, [data]);

  return <div ref={ref} style={{ width: '100%', height: 400 }} />;
}

// 方案 2：使用 @hugocxl/react-echarts（活跃维护，hooks 风格 API）
// import { ReactEChart } from '@hugocxl/react-echarts';
```

```vue
<!-- Vue：使用 vue-echarts（ecomfe 官方维护） -->
<script setup>
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent]);

const option = {
  xAxis: { type: 'category', data: ['A', 'B', 'C'] },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: [120, 200, 150] }],
};
</script>

<template>
  <v-chart :option="option" autoresize style="height: 400px" />
</template>
```

<!-- version-check: echarts 6.0.0, vue-echarts 7.x, @hugocxl/react-echarts 1.x, checked 2026-05-15 -->

## 4. 大数据量优化

```javascript
chart.setOption({
  dataset: { source: largeData },
  series: [{
    type: 'scatter',
    large: true,           // 开启大数据量优化
    largeThreshold: 2000,  // 阈值
    progressive: 400,      // 渐进渲染
    progressiveThreshold: 3000,
  }],
});
```

## 5. ECharts 6.0 版本演进

<!-- version-check: ECharts 6.0, checked 2026-04-23 -->

> 🔄 更新于 2026-04-23

Apache ECharts 6.0 于 2025-08-07 正式发布，是 ECharts 12 年来最大的版本升级，带来 12 项重大改进。来源：[ECharts 6 Features](https://echarts.apache.org/handbook/en/basics/release-note/v6-feature/)

### 5.1 三大核心维度

**更专业的视觉呈现**：
- **全新默认主题**：基于 Design Token 重构颜色和间距，70%+ 开发者使用默认主题
- **动态主题切换**：运行时无缝切换主题，无需重新初始化
- **暗色模式支持**：自动适配系统暗色/亮色模式

**扩展数据表达边界**：
- **Chord 弦图**：可视化复杂关系和分布
- **Beeswarm 蜂群图**：智能展开重叠数据点为蜂窝布局
- **散点抖动（Jitter）**：为密集散点图添加抖动提升可读性
- **断轴（Broken Axis）**：轻松展示数量级差异大的数据
- **增强 K 线图**：改进标签能力和更多开箱即用的交易图表

**释放组合自由度**：
- **矩阵坐标系**：像表格一样自由组合图表类型和组件
- **增强自定义系列**：支持 npm 发布和动态注册，实现代码复用
- **新增自定义图表**：小提琴图、等高线图、阶梯图、柱状范围图、折线范围图
- **坐标轴标签优化**：更智能的默认布局，防止溢出和重叠

### 5.2 从 v5 迁移

```javascript
// v5 → v6 大部分 API 向后兼容
// 主要 Breaking Changes：
// 1. 默认主题变化（可用 v5.js 主题文件恢复旧样式）
// 2. 部分废弃 API 移除

// 安装 v6
// npm install echarts@6

// 如需保持 v5 主题风格
import v5Theme from 'echarts/theme/v5';
echarts.registerTheme('v5', v5Theme);
const chart = echarts.init(dom, 'v5');
```

### 5.3 暗色模式示例

```javascript
// 自动跟随系统暗色模式
const chart = echarts.init(dom, 'dark');

// 动态切换主题
chart.setOption({}, { replaceMerge: ['series'] });
```
