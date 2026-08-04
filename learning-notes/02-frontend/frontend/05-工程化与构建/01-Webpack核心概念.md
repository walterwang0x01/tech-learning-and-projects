# Webpack 核心概念
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 核心概念

```javascript
// webpack.config.js
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  // 入口
  entry: './src/index.js',

  // 输出
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash:8].js',
    clean: true,
  },

  // 模式
  mode: 'production', // 'development' | 'production'

  // Loader（处理非JS文件）
  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        exclude: /node_modules/,
        use: 'babel-loader',
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader'],
      },
      {
        test: /\.scss$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader', 'sass-loader'],
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        type: 'asset',
        parser: { dataUrlCondition: { maxSize: 8 * 1024 } },
      },
    ],
  },

  // 插件
  plugins: [
    new HtmlWebpackPlugin({ template: './public/index.html' }),
    new MiniCssExtractPlugin({ filename: 'css/[name].[contenthash:8].css' }),
  ],

  // 解析
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx'],
    alias: { '@': path.resolve(__dirname, 'src') },
  },
};
```

## 2. 代码分割

```javascript
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    },
  },
};

// 动态导入（自动代码分割）
const module = await import(/* webpackChunkName: "lodash" */ 'lodash');
```

## 3. Tree Shaking

```javascript
// 生产模式自动启用
// 要求：使用 ES Module（import/export）
// package.json 中标记无副作用
{
  "sideEffects": false,
  // 或指定有副作用的文件
  "sideEffects": ["*.css", "*.scss"]
}
```

## 4. HMR 热更新

```javascript
// 开发服务器配置
module.exports = {
  devServer: {
    hot: true,
    port: 3000,
    open: true,
    proxy: {
      '/api': { target: 'http://localhost:8080', changeOrigin: true },
    },
  },
};
```

## 5. 性能优化

```javascript
module.exports = {
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({ parallel: true }),
      new CssMinimizerPlugin(),
    ],
    splitChunks: { chunks: 'all' },
    runtimeChunk: 'single',
  },
  // 缓存
  cache: { type: 'filesystem' },
};
```
## 🎬 推荐视频资源

- [freeCodeCamp - Webpack Full Course](https://www.youtube.com/watch?v=MpGLUVbqoYQ) — Webpack完整课程
- [Fireship - Webpack in 100 Seconds](https://www.youtube.com/watch?v=5IG4UmULyoA) — Webpack快速了解
