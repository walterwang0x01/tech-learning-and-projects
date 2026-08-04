# Gradle 构建系统
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. build.gradle.kts 基础

```kotlin
// app/build.gradle.kts
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.hilt)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.example.app"
    compileSdk = 36  // Android 16

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 26
        targetSdk = 36  // Android 16
        versionCode = 1
        versionName = "1.0.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    // Kotlin 2.0+ 不再需要 composeOptions，Compose Compiler 已集成到 Kotlin 插件中

    kotlin { jvmToolchain(21) }  // 推荐 JDK 21
}
```

## 2. Version Catalog

```toml
# gradle/libs.versions.toml
[versions]
agp = "9.0.1"
kotlin = "2.3.20"
compose-bom = "2026.03.00"
hilt = "2.57"
room = "2.8.4"
ktor = "3.1.1"

[libraries]
# Compose
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui = { group = "androidx.compose.ui", name = "ui" }
compose-material3 = { group = "androidx.compose.material3", name = "material3" }
compose-navigation = { group = "androidx.navigation", name = "navigation-compose", version = "2.9.7" }

# Hilt
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler = { group = "com.google.dagger", name = "hilt-compiler", version.ref = "hilt" }

# Room
room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
room-compiler = { group = "androidx.room", name = "room-compiler", version.ref = "room" }
room-ktx = { group = "androidx.room", name = "room-ktx", version.ref = "room" }

[bundles]
compose = ["compose-ui", "compose-material3", "compose-navigation"]
room = ["room-runtime", "room-ktx"]

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
ksp = { id = "com.google.devtools.ksp", version = "2.3.20-1.0.31" }
compose-compiler = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
```

## 3. Build Variants

```kotlin
android {
    buildTypes {
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
            buildConfigField("String", "API_URL", "\"https://dev-api.example.com\"")
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            buildConfigField("String", "API_URL", "\"https://api.example.com\"")
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }

    flavorDimensions += "environment"
    productFlavors {
        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
            buildConfigField("String", "ENV", "\"staging\"")
        }
        create("production") {
            dimension = "environment"
            buildConfigField("String", "ENV", "\"production\"")
        }
    }
}
```

## 4. 自定义 Gradle Task

```kotlin
// 打印 APK 大小
tasks.register("printApkSize") {
    doLast {
        val apkDir = layout.buildDirectory.dir("outputs/apk/release").get().asFile
        apkDir.listFiles()?.filter { it.extension == "apk" }?.forEach {
            println("${it.name}: ${it.length() / 1024 / 1024}MB")
        }
    }
}

// 复制 APK 到指定目录
tasks.register<Copy>("copyRelease") {
    from(layout.buildDirectory.dir("outputs/apk/release"))
    into("${rootProject.projectDir}/release")
    include("*.apk")
    rename { "app-v${android.defaultConfig.versionName}.apk" }
}
```

## 5. 构建加速

```properties
# gradle.properties
org.gradle.jvmargs=-Xmx4g -XX:+UseParallelGC
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
kotlin.incremental=true
```


## 6. AGP 9.0 与 Gradle 9 版本演进

<!-- version-check: AGP 9.0.1, Gradle 9.1, checked 2026-04-21 -->

> 🔄 更新于 2026-04-21

### 版本对比

| 组件 | 旧版本 | 新版本 | 关键变化 |
|------|--------|--------|----------|
| AGP | 8.2.2 | **9.0.1** | 要求 Gradle 9+、JDK 17+、Kotlin 2.0+ |
| Gradle | 8.x | **9.1** | Configuration Cache 默认启用、Kotlin DSL 推荐 |
| Kotlin | 1.9.22 | **2.3.20** | K2 编译器、Compose Compiler 内置 |
| compileSdk | 34 | **36** | Android 16 API |
| KSP | 1.9.22-1.0.17 | **2.3.20-1.0.31** | 对齐 Kotlin 版本 |

### AGP 9.0 核心变化

```kotlin
// 1. Compose Compiler 不再需要单独配置
// Kotlin 2.0+ 将 Compose Compiler 集成到 Kotlin 插件中
plugins {
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.compose.compiler)  // 新增：Compose Compiler 插件
}

// 2. 不再需要 composeOptions 块
// ❌ 旧写法（AGP 8.x + Kotlin 1.9）
// composeOptions {
//     kotlinCompilerExtensionVersion = "1.5.8"
// }

// ✅ 新写法（AGP 9.0 + Kotlin 2.3）
// 无需任何配置，Compose Compiler 版本自动与 Kotlin 版本对齐
```

### Gradle 9 构建加速

```properties
# gradle.properties（2026 推荐配置）
org.gradle.jvmargs=-Xmx4g -XX:+UseParallelGC
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
# Gradle 9 默认启用 Configuration Cache
# Kotlin 增量编译默认启用
```

> 来源：[AGP 9.0 Release Notes](https://developer.android.com/build/releases/agp-9-0-0-release-notes)
