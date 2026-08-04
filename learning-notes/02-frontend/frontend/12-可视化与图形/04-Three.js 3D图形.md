# Three.js 3D 图形
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 基本概念

```javascript
import * as THREE from 'three';

// 场景
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf0f0f0);

// 相机（透视相机）
const camera = new THREE.PerspectiveCamera(
  75,                                    // 视角
  window.innerWidth / window.innerHeight, // 宽高比
  0.1,                                   // 近裁剪面
  1000                                   // 远裁剪面
);
camera.position.set(0, 5, 10);
camera.lookAt(0, 0, 0);

// 渲染器
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);
```

## 2. 几何体与材质

```javascript
// 立方体
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x3498db });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// 球体
const sphere = new THREE.Mesh(
  new THREE.SphereGeometry(0.5, 32, 32),
  new THREE.MeshStandardMaterial({ color: 0xe74c3c, metalness: 0.3, roughness: 0.7 })
);
sphere.position.set(2, 0, 0);
scene.add(sphere);

// 平面
const plane = new THREE.Mesh(
  new THREE.PlaneGeometry(20, 20),
  new THREE.MeshStandardMaterial({ color: 0xcccccc })
);
plane.rotation.x = -Math.PI / 2;
plane.position.y = -1;
scene.add(plane);
```

## 3. 光照

```javascript
// 环境光（均匀照亮所有物体）
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

// 平行光（模拟太阳光）
const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 5);
directionalLight.castShadow = true;
scene.add(directionalLight);

// 点光源
const pointLight = new THREE.PointLight(0xff6600, 1, 100);
pointLight.position.set(0, 5, 0);
scene.add(pointLight);
```

## 4. 动画循环

```javascript
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const controls = new OrbitControls(camera, renderer.domElement);

function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  controls.update();
  renderer.render(scene, camera);
}
animate();

// 响应式
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

## 5. 模型加载

```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

const loader = new GLTFLoader();
loader.load('/models/scene.gltf', (gltf) => {
  scene.add(gltf.scene);
  // 播放动画
  const mixer = new THREE.AnimationMixer(gltf.scene);
  gltf.animations.forEach(clip => mixer.clipAction(clip).play());
});
```

## 6. Three.js 2025-2026 版本演进与 WebGPU

<!-- version-check: Three.js r180/r183, checked 2026-05-15 -->

> 🔄 更新于 2026-05-15

Three.js 在 2025-2026 年跨越了重要门槛：WebGPU 在所有主流浏览器上可用，NPM 周下载量达 270 万（是 Babylon.js 的 270 倍）。来源：[Three.js 2026 What Changed](https://www.utsubo.com/blog/threejs-2026-what-changed)

### 6.1 WebGPU 生产就绪

<!-- 修复于 2026-05-15: 修正 Three.js 版本表。npm 当前发布 0.180.0（cdnjs 同步），r183 已发布（论坛确认 Clock 已废弃），r184/r185 在 milestone 规划中 -->

| 版本 | 时间 | 关键变化 |
|------|------|---------|
| r170 | 2025-08 | WebGPU 模块移至 addons，GLTFLoader 支持 |
| r171 | 2025-09 | 零配置 WebGPU 导入，React Three Fiber 集成 |
| r180 | 2025-11 | npm 当前最新（0.180.0），纹理绑定改进，深度纹理修复 |
| r182 | 2025-12 | WebGPU 稳定性提升 |
| r183 | 2026-01 | TSL 持续完善，`Clock` 废弃，推荐 `Timer` |
| r184/r185 | 2026 上半年 | TSL 节点图统一 GLSL/WGSL 编译（规划中） |

> 待确认：r183 后的版本目前在 milestone 中规划（GitHub `mrdoob/three.js/milestone/98`），实际 npm 发布以 [npm three](https://www.npmjs.com/package/three) 和 [cdnjs](https://cdnjs.com/libraries/three.js/) 为准。

```javascript
// r171+ 零配置 WebGPU（自动回退到 WebGL 2）
import { WebGPURenderer } from 'three/webgpu';

const renderer = new WebGPURenderer();
await renderer.init(); // WebGPU 需要异步初始化
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// 其余代码与 WebGLRenderer 完全一致
renderer.render(scene, camera);
```

### 6.2 WebGPU vs WebGL 对比

| 特性 | WebGL | WebGPU |
|------|-------|--------|
| 计算着色器 | ❌ | ✅ GPU 通用计算 |
| 资源管理 | 隐式 | 显式控制 GPU 内存 |
| Draw Call 密集场景 | 一般 | 最高 10x 提升 |
| 浏览器支持 | 全部 | Chrome/Edge/Firefox/Safari 26+ |
| API 设计 | 基于 OpenGL | 现代 GPU 原生设计 |

### 6.3 WebGPU 浏览器支持（2026）

| 浏览器 | WebGPU 支持 |
|--------|------------|
| Chrome / Edge | v113+（2023） |
| Firefox | v141+（Windows），v145+（macOS ARM） |
| Safari | v26+（2025-09，含 iOS/iPadOS/visionOS） |

Safari 26 是最后一个支持 WebGPU 的主流浏览器，至此 WebGPU 可以面向所有用户发布。
