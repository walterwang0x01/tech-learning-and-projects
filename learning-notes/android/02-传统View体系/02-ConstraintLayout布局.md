# ConstraintLayout 布局
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 基本约束

```xml
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <ImageView
        android:id="@+id/avatar"
        android:layout_width="48dp"
        android:layout_height="48dp"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent"
        android:layout_margin="16dp" />

    <TextView
        android:id="@+id/tvName"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        app:layout_constraintStart_toEndOf="@id/avatar"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="@id/avatar"
        android:layout_marginStart="12dp" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

## 2. Chain（链）

```xml
<!-- 水平链：三个按钮均匀分布 -->
<Button android:id="@+id/btn1"
    app:layout_constraintStart_toStartOf="parent"
    app:layout_constraintEnd_toStartOf="@id/btn2"
    app:layout_constraintHorizontal_chainStyle="spread" />

<Button android:id="@+id/btn2"
    app:layout_constraintStart_toEndOf="@id/btn1"
    app:layout_constraintEnd_toStartOf="@id/btn3" />

<Button android:id="@+id/btn3"
    app:layout_constraintStart_toEndOf="@id/btn2"
    app:layout_constraintEnd_toEndOf="parent" />

<!-- chainStyle: spread / spread_inside / packed -->
```

## 3. Guideline（辅助线）

```xml
<!-- 水平辅助线：距顶部 30% -->
<androidx.constraintlayout.widget.Guideline
    android:id="@+id/guideline"
    android:orientation="horizontal"
    app:layout_constraintGuide_percent="0.3" />

<TextView
    app:layout_constraintTop_toBottomOf="@id/guideline"
    app:layout_constraintStart_toStartOf="parent" />
```

## 4. Barrier（屏障）

```xml
<!-- Barrier 根据多个 View 的边界动态定位 -->
<TextView android:id="@+id/label1" android:text="用户名" ... />
<TextView android:id="@+id/label2" android:text="电子邮箱地址" ... />

<androidx.constraintlayout.widget.Barrier
    android:id="@+id/barrier"
    app:barrierDirection="end"
    app:constraint_referenced_ids="label1,label2" />

<EditText
    app:layout_constraintStart_toEndOf="@id/barrier"
    android:layout_marginStart="8dp" ... />
```

## 5. Flow（流式布局）

```xml
<androidx.constraintlayout.helper.widget.Flow
    android:layout_width="0dp"
    android:layout_height="wrap_content"
    app:layout_constraintStart_toStartOf="parent"
    app:layout_constraintEnd_toEndOf="parent"
    app:flow_wrapMode="chain"
    app:flow_horizontalGap="8dp"
    app:flow_verticalGap="8dp"
    app:constraint_referenced_ids="chip1,chip2,chip3,chip4,chip5" />
```

## 6. MotionLayout

```xml
<!-- res/xml/motion_scene.xml -->
<MotionScene>
    <Transition
        app:constraintSetStart="@id/start"
        app:constraintSetEnd="@id/end"
        app:duration="300">
        <OnSwipe
            app:dragDirection="dragUp"
            app:touchAnchorId="@id/header"
            app:touchAnchorSide="bottom" />
    </Transition>

    <ConstraintSet android:id="@+id/start">
        <Constraint android:id="@id/header"
            android:layout_height="200dp"
            app:layout_constraintTop_toTopOf="parent" />
    </ConstraintSet>

    <ConstraintSet android:id="@+id/end">
        <Constraint android:id="@id/header"
            android:layout_height="56dp"
            app:layout_constraintTop_toTopOf="parent" />
    </ConstraintSet>
</MotionScene>
```

```kotlin
// 代码中控制 MotionLayout
class CollapsingFragment : Fragment(R.layout.fragment_collapsing) {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val motionLayout = binding.motionLayout
        motionLayout.setTransitionListener(object : MotionLayout.TransitionListener {
            override fun onTransitionCompleted(layout: MotionLayout, currentId: Int) {
                if (currentId == R.id.end) { /* 折叠完成 */ }
            }
            override fun onTransitionChange(layout: MotionLayout, s: Int, e: Int, p: Float) {}
            override fun onTransitionStarted(layout: MotionLayout, s: Int, e: Int) {}
            override fun onTransitionTrigger(layout: MotionLayout, t: Int, p: Boolean, pr: Float) {}
        })
    }
}
```

## 7. 2026 版本演进

<!-- version-check: ConstraintLayout 2.2.1, ConstraintLayout-compose 1.1.1 stable, checked 2026-05-31 -->

> 🔄 更新于 2026-05-04（2026-05-31 校准 ConstraintLayout Compose 版本）

### 7.1 ConstraintLayout 2.2.1（2025-02-26）

ConstraintLayout 最新稳定版为 **2.2.1**，修复了 constraintlayout-core 库的二进制兼容性问题。2.2.0 是自 2.1.0 以来的首个大版本更新，与底层 constraintlayout-core 库对齐。

来源：[AndroidX ConstraintLayout Releases](https://developer.android.com/jetpack/androidx/releases/constraintlayout)

```kotlin
// 推荐依赖版本（2026）
dependencies {
    implementation("androidx.constraintlayout:constraintlayout:2.2.1")
    // Compose 版本（已发布 1.1.1 稳定版）
    implementation("androidx.constraintlayout:constraintlayout-compose:1.1.1")
    // <!-- 修复于 2026-05-31: 原文写 1.1.0-alpha14 并称"仍在 alpha"，实测 androidx maven 已发布 1.1.1 stable -->
}
```

### 7.2 ConstraintLayout 在 2026 年的定位

随着 Jetpack Compose 成为 Android UI 开发的推荐方案，ConstraintLayout 的使用场景在收窄，但在以下场景仍然不可替代：

| 场景 | 推荐方案 |
|------|---------|
| 新项目 UI | Compose `Row`/`Column`/`Box` 组合 |
| 复杂相对定位 | ConstraintLayout（XML 或 Compose 版） |
| MotionLayout 动画 | ConstraintLayout MotionLayout（Compose 版仍在实验阶段） |
| 已有 XML 布局维护 | ConstraintLayout 2.2.1 |
| 性能敏感的扁平布局 | ConstraintLayout（单层布局减少测量次数） |

> ⚠️ ConstraintLayout Compose 版（1.1.1）的 MotionLayout API 仍标记为实验性（`@ExperimentalMotionApi`），生产环境建议谨慎使用。
