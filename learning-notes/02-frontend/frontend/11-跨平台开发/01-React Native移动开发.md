# React Native 移动开发
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 核心组件

```jsx
import { View, Text, Image, ScrollView, FlatList, TouchableOpacity, StyleSheet } from 'react-native';

function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Hello React Native</Text>
      <Image source={{ uri: 'https://example.com/image.jpg' }} style={styles.image} />
      <TouchableOpacity style={styles.button} onPress={() => alert('Pressed')}>
        <Text style={styles.buttonText}>点击我</Text>
      </TouchableOpacity>
    </View>
  );
}

// 样式（类似 CSS 的 Flexbox，但默认 flexDirection: 'column'）
const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fff' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 16 },
  image: { width: 200, height: 200, borderRadius: 8 },
  button: { backgroundColor: '#3498db', padding: 12, borderRadius: 8, alignItems: 'center' },
  buttonText: { color: '#fff', fontSize: 16 },
});
```

## 2. FlatList（高性能列表）

```jsx
import { FlatList, Text } from 'react-native';

<FlatList
  data={items}
  keyExtractor={(item) => item.id.toString()}
  renderItem={({ item }) => <ListItem item={item} />}
  onEndReached={loadMore}
  onEndReachedThreshold={0.5}
  refreshing={refreshing}
  onRefresh={handleRefresh}
  ListEmptyComponent={<Text>暂无数据</Text>}
/>
```

## 3. 导航（React Navigation）

```jsx
// React Navigation v7（2026 最新稳定版）
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Button } from 'react-native';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Detail" component={DetailScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// 导航操作
function HomeScreen({ navigation }) {
  return (
    <Button title="详情" onPress={() => navigation.navigate('Detail', { id: 1 })} />
  );
}

function DetailScreen({ route }) {
  const { id } = route.params;
}
```

## 4. Expo

```bash
# 快速创建项目
npx create-expo-app my-app
npx expo start

# Expo 优势：
# - 无需配置原生环境
# - 丰富的内置 API（相机、位置、通知等）
# - OTA 更新
# - Expo Go 即时预览
```

## 5. React Native 0.85 与 2026 版本演进

<!-- version-check: React Native 0.85, checked 2026-05-15 -->

> 🔄 更新于 2026-05-15

<!-- 修复于 2026-05-15: 补充 0.84 (Hermes V1 by Default) 演进信息 -->

### 版本演进

| 版本 | 发布时间 | 关键变化 |
|------|---------|---------|
| 0.76 | 2024-10 | New Architecture 成为默认 |
| 0.82 | 2025-10 | 完全移除 Legacy Architecture，首个纯新架构版本 |
| 0.83 | 2025-12 | React 19.2 集成，Android 包体积减少 ~3.8MB |
| 0.84 | 2026-02 | Hermes V1 成为默认 JS 引擎 |
| 0.85 | 2026-04 | Shared Animation Backend、Metro TLS、多 CDP 连接 |

### 0.85 核心新特性

**Shared Animation Backend（实验性）**

与 Software Mansion 合作开发的新动画引擎，统一了 Animated 和 Reanimated 的底层更新逻辑。现在可以用 `useNativeDriver: true` 驱动 Flexbox 和 position 属性动画：

```jsx
import { Animated, Button, View, useAnimatedValue } from 'react-native';

// 0.85 新特性：原生驱动的布局属性动画
function ExpandableBox() {
  const width = useAnimatedValue(100);

  const expand = () => {
    Animated.timing(width, {
      toValue: 300,
      duration: 500,
      useNativeDriver: true, // 之前布局属性不支持 native driver
    }).start();
  };

  return (
    <View style={{ flex: 1 }}>
      <Animated.View style={{ width, height: 100, backgroundColor: 'blue' }} />
      <Button title="展开" onPress={expand} />
    </View>
  );
}
```

**多 CDP 连接**

支持多个 Chrome DevTools Protocol 同时连接（React Native DevTools、VS Code、AI Agent），不再互相踢掉会话。

**Metro TLS 支持**

开发服务器支持 HTTPS，用于测试需要安全连接的 API：

```javascript
// metro.config.js
const fs = require('fs');
config.server.tls = {
  ca: fs.readFileSync('path/to/ca'),
  cert: fs.readFileSync('path/to/cert'),
  key: fs.readFileSync('path/to/key'),
};
```

### Breaking Changes

```
Jest Preset 迁移：
- preset: 'react-native'
+ preset: '@react-native/jest-preset'

Node.js 版本要求：
- 支持：v20 (>=20.19.4)、v22、v24+
- 不支持：v21、v23（已 EOL）

已移除 API：
- StyleSheet.absoluteFillObject → 使用 StyleSheet.absoluteFill
- AccessibilityInfo.setAccessibilityFocus → 使用 sendAccessibilityEvent
```

### 2026 年新项目建议

```bash
# 使用最新 CLI 创建项目（默认 New Architecture）
npx @react-native-community/cli@latest init MyProject --version latest

# 或使用 Expo SDK 56（包含 RN 0.85）
npx create-expo-app my-app
```

来源：[React Native 0.85 Blog](https://reactnative.dev/blog/2026/04/07/react-native-0.85) | [The State of React Native in 2026](https://www.ditto.com/blog/the-state-of-react-native-in-2026)
