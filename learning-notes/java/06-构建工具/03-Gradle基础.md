# Gradle基础与应用
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Gradle基础

### 1.1 Gradle简介

Gradle是一个基于Apache Ant和Apache Maven概念的项目自动化构建工具。它使用基于Groovy或Kotlin的特定领域语言(DSL)来声明项目设置，而不是传统的XML。

**Gradle的特点：**
- 基于Groovy/Kotlin DSL，配置简洁
- 支持增量构建，构建速度快
- 强大的依赖管理
- 支持多项目构建
- 与Maven和Ivy仓库兼容
- 支持多种语言和平台（Java、Kotlin、Android、C++等）

### 1.2 Gradle与Maven的对比

| 特性 | Gradle | Maven |
|------|--------|-------|
| 配置文件 | build.gradle (Groovy/Kotlin) | pom.xml (XML) |
| 构建速度 | 快（增量构建） | 较慢 |
| 灵活性 | 高 | 中 |
| 学习曲线 | 中等 | 简单 |
| 插件生态 | 丰富 | 丰富 |

### 1.3 安装Gradle

**方式一：使用包管理器**
```bash
# macOS
brew install gradle

# Ubuntu/Debian
sudo apt install gradle

# Windows (使用Chocolatey)
choco install gradle
```

**方式二：手动安装**
1. 下载Gradle：https://gradle.org/releases/
2. 解压到指定目录
3. 配置环境变量：
   ```bash
   # Windows
   GRADLE_HOME=C:\gradle
   PATH=%GRADLE_HOME%\bin;%PATH%
   
   # Linux/macOS
   export GRADLE_HOME=/opt/gradle
   export PATH=$GRADLE_HOME/bin:$PATH
   ```

**验证安装：**
```bash
gradle -v
```

### 1.4 Gradle Wrapper

Gradle Wrapper是Gradle推荐的使用方式，它确保项目使用特定版本的Gradle，避免版本不一致问题。

**生成Wrapper：**
```bash
gradle wrapper --gradle-version 7.6
```

**Wrapper文件：**
- `gradlew` / `gradlew.bat`: 执行脚本
- `gradle/wrapper/gradle-wrapper.jar`: Wrapper实现
- `gradle/wrapper/gradle-wrapper.properties`: Wrapper配置

**使用Wrapper：**
```bash
# Linux/macOS
./gradlew build

# Windows
gradlew.bat build
```

## 2. 项目结构

### 2.1 标准项目结构

```
project/
├── build.gradle          # 构建脚本
├── settings.gradle      # 项目设置
├── gradle.properties    # Gradle属性配置
├── src/
│   ├── main/
│   │   ├── java/        # Java源代码
│   │   └── resources/   # 资源文件
│   └── test/
│       ├── java/        # 测试代码
│       └── resources/   # 测试资源
└── build/               # 构建输出目录
```

### 2.2 build.gradle文件

**Java项目示例：**
```groovy
plugins {
    id 'java'
    id 'application'
}

group = 'com.example'
version = '1.0.0'

java {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}

repositories {
    mavenCentral()
    maven { url 'https://maven.aliyun.com/repository/public' }
}

dependencies {
    implementation 'org.springframework:spring-core:5.3.21'
    testImplementation 'junit:junit:4.13.2'
}

application {
    mainClass = 'com.example.Main'
}
```

### 2.3 settings.gradle文件

```groovy
rootProject.name = 'my-project'

// 多项目构建
include 'module1', 'module2'
```

## 3. 依赖管理

### 3.1 依赖配置

Gradle使用配置（Configuration）来管理依赖：

- `implementation`: 编译和运行时依赖（推荐）
- `compileOnly`: 仅编译时依赖
- `runtimeOnly`: 仅运行时依赖
- `testImplementation`: 测试编译和运行时依赖
- `testCompileOnly`: 测试仅编译时依赖
- `testRuntimeOnly`: 测试仅运行时依赖

**示例：**
```groovy
dependencies {
    // 编译和运行时依赖
    implementation 'com.google.guava:guava:31.1-jre'
    
    // 仅编译时依赖
    compileOnly 'org.projectlombok:lombok:1.18.24'
    
    // 仅运行时依赖
    runtimeOnly 'mysql:mysql-connector-java:8.0.29'
    
    // 测试依赖
    testImplementation 'junit:junit:4.13.2'
}
```

### 3.2 仓库配置

**常用仓库：**
```groovy
repositories {
    // Maven中央仓库
    mavenCentral()
    
    // 阿里云镜像（推荐）
    maven { url 'https://maven.aliyun.com/repository/public' }
    
    // 本地仓库
    mavenLocal()
    
    // 自定义仓库
    maven {
        url 'https://repo.example.com/repository'
        credentials {
            username = 'user'
            password = 'password'
        }
    }
    
    // Ivy仓库
    ivy {
        url 'https://repo.example.com/ivy'
    }
}
```

### 3.3 依赖版本管理

**方式一：直接指定版本**
```groovy
dependencies {
    implementation 'org.springframework:spring-core:5.3.21'
}
```

**方式二：使用变量管理版本**
```groovy
ext {
    springVersion = '5.3.21'
}

dependencies {
    implementation "org.springframework:spring-core:${springVersion}"
}
```

**方式三：使用版本目录（Gradle 7.0+）**
```groovy
// settings.gradle
dependencyResolutionManagement {
    versionCatalogs {
        libs {
            library('spring-core', 'org.springframework', 'spring-core').version('5.3.21')
        }
    }
}

// build.gradle
dependencies {
    implementation libs.spring.core
}
```

### 3.4 依赖排除

```groovy
dependencies {
    implementation('org.springframework:spring-core:5.3.21') {
        exclude group: 'commons-logging', module: 'commons-logging'
    }
}
```

### 3.5 依赖冲突解决

```groovy
configurations.all {
    resolutionStrategy {
        // 强制使用指定版本
        force 'com.google.guava:guava:31.1-jre'
        
        // 优先使用指定版本
        preferProjectModules()
        
        // 失败时策略
        failOnVersionConflict()
    }
}
```

## 4. 任务（Tasks）

### 4.1 内置任务

Gradle提供了许多内置任务：

- `gradle build`: 构建项目
- `gradle clean`: 清理构建目录
- `gradle test`: 运行测试
- `gradle jar`: 打包JAR文件
- `gradle run`: 运行应用程序

### 4.2 自定义任务

```groovy
task hello {
    doLast {
        println 'Hello, Gradle!'
    }
}

task copyFiles(type: Copy) {
    from 'src/main/resources'
    into 'build/resources'
}

task compileJava {
    dependsOn 'clean'
    doLast {
        println 'Compiling Java...'
    }
}
```

### 4.3 任务依赖

```groovy
task taskA {
    doLast {
        println 'Task A'
    }
}

task taskB {
    dependsOn taskA
    doLast {
        println 'Task B'
    }
}
```

### 4.4 任务配置

```groovy
task myTask {
    description = 'My custom task'
    group = 'custom'
    
    doFirst {
        println 'Before execution'
    }
    
    doLast {
        println 'After execution'
    }
}
```

## 5. 插件

### 5.1 应用插件

**方式一：使用plugins块（推荐）**
```groovy
plugins {
    id 'java'
    id 'application'
    id 'org.springframework.boot' version '2.7.0'
}
```

**方式二：使用apply**
```groovy
apply plugin: 'java'
apply plugin: 'application'
```

### 5.2 常用插件

**Java插件：**
```groovy
plugins {
    id 'java'
}

java {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}
```

**Application插件：**
```groovy
plugins {
    id 'application'
}

application {
    mainClass = 'com.example.Main'
}
```

**Spring Boot插件：**
```groovy
plugins {
    id 'org.springframework.boot' version '2.7.0'
    id 'io.spring.dependency-management' version '1.0.11.RELEASE'
}
```

## 6. 多项目构建

### 6.1 项目结构

```
root/
├── build.gradle
├── settings.gradle
├── module1/
│   └── build.gradle
└── module2/
    └── build.gradle
```

### 6.2 settings.gradle配置

```groovy
rootProject.name = 'multi-project'

include 'module1', 'module2'
```

### 6.3 根项目build.gradle

```groovy
subprojects {
    apply plugin: 'java'
    
    repositories {
        mavenCentral()
    }
    
    dependencies {
        // 所有子项目的公共依赖
    }
}
```

### 6.4 子项目依赖

```groovy
// module1/build.gradle
dependencies {
    implementation project(':module2')
}
```

## 7. 构建优化

### 7.1 增量构建

Gradle支持增量构建，只重新构建发生变化的部分，提高构建速度。

### 7.2 并行构建

```groovy
// gradle.properties
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.daemon=true
```

### 7.3 构建缓存

```groovy
// gradle.properties
org.gradle.caching=true
```

### 7.4 性能优化建议

1. 使用Gradle Daemon
2. 启用构建缓存
3. 使用并行构建
4. 避免不必要的任务执行
5. 优化依赖解析

## 8. 常用命令

```bash
# 查看帮助
gradle help

# 查看所有任务
gradle tasks

# 构建项目
gradle build

# 清理构建
gradle clean

# 运行测试
gradle test

# 查看依赖
gradle dependencies

# 查看依赖树
gradle dependencies --configuration compileClasspath

# 刷新依赖
gradle --refresh-dependencies build

# 查看项目信息
gradle projects

# 执行特定任务
gradle taskName
```

## 9. 与Maven的迁移

### 9.1 从Maven迁移到Gradle

**使用Gradle的Maven导入工具：**
```bash
gradle init --type pom
```

**手动迁移要点：**
1. 将`pom.xml`中的依赖转换为`build.gradle`格式
2. 配置仓库
3. 配置插件
4. 迁移构建脚本

### 9.2 兼容Maven仓库

Gradle完全兼容Maven仓库，可以直接使用Maven中央仓库和私有仓库。

## 10. 最佳实践

1. **使用Gradle Wrapper**：确保团队使用相同版本的Gradle
2. **使用版本目录**：统一管理依赖版本
3. **合理使用配置**：区分implementation、compileOnly等
4. **启用构建缓存**：提高构建速度
5. **使用并行构建**：充分利用多核CPU
6. **定期更新依赖**：保持依赖版本最新
7. **使用插件**：利用社区插件提高效率
8. **优化构建脚本**：避免不必要的任务执行

## 总结

Gradle是一个功能强大的构建工具，相比Maven具有更好的灵活性和性能。掌握Gradle的基础知识，能够帮助你更好地管理Java项目。在实际使用中，建议：

1. 从简单的单项目开始
2. 逐步学习多项目构建
3. 熟悉常用插件和任务
4. 优化构建性能
5. 遵循最佳实践

## 11. Gradle 版本演进

> 🔄 更新于 2026-04-18

<!-- version-check: Gradle 9.5.1 (2026-05-12), Gradle 8.14.5 (维护分支), checked 2026-05-31 -->

### Gradle 8.x → 9.x 重要变化

| 版本 | 关键变化 |
|------|---------|
| **Gradle 8.x** | Kotlin DSL 成为默认、版本目录（Version Catalog）正式发布、配置缓存改进 |
| **Gradle 9.x** | Spring Boot 4.0 支持、构建性能进一步优化、废弃 API 清理 |

> 🔄 更新于 2026-05-31
>
> **Gradle 9.x 版本线动态**（截至 2026-05）：
>
> | 版本 | 发布日期 | 关键变化 |
> |------|---------|---------|
> | 9.3.0 | 2026-01-16 | 测试报告改进（嵌套/参数化/套件测试的 HTML 报告）、TestKit 流式 API |
> | 9.4.0 | 2026-03-04 | 支持非 class 测试（直接执行 Cucumber feature / 自定义测试引擎）、更丰富的测试元数据 |
> | 9.5.0 | 2026-04-28 | — |
> | **9.5.1** | **2026-05-12** | **当前最新稳定版**：错误与报告中加入 task provenance（快速定位失败任务来源）、客户端 JVM 与 daemon 不兼容时日志更清晰 |
> | 8.14.5 | 2026-05-07 | 8.x 维护分支补丁（仍需 Java 8-21 兼容的遗留项目） |
>
> Gradle 9.0 起，配置缓存（Configuration Cache）成为首选执行模式，并升级到 Kotlin 2 + Groovy 4。Kotlin 2.4（KMP/AGP 9.0）项目需要 Gradle 9.4.1+。
>
> 来源：[Gradle Releases](https://gradle.org/releases/) | [Gradle 9.5.1 Release Notes](https://docs.gradle.org/current/release-notes) | [What's new in Gradle 9](https://gradle.org/whats-new/gradle-9)

### Kotlin DSL（推荐）

Gradle 8+ 推荐使用 Kotlin DSL（`.gradle.kts`）替代 Groovy DSL：

```kotlin
// build.gradle.kts（Kotlin DSL，推荐）
plugins {
    java
    id("org.springframework.boot") version "4.0.0"
    id("io.spring.dependency-management") version "1.1.7"
}

group = "com.example"
version = "1.0.0"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

### 版本目录（Version Catalog）

```toml
# gradle/libs.versions.toml（推荐的依赖版本管理方式）
[versions]
spring-boot = "4.0.0"
junit = "5.11.0"

[libraries]
spring-boot-starter-web = { module = "org.springframework.boot:spring-boot-starter-web", version.ref = "spring-boot" }
junit-jupiter = { module = "org.junit.jupiter:junit-jupiter", version.ref = "junit" }

[plugins]
spring-boot = { id = "org.springframework.boot", version.ref = "spring-boot" }
```

```kotlin
// build.gradle.kts 中引用
dependencies {
    implementation(libs.spring.boot.starter.web)
    testImplementation(libs.junit.jupiter)
}
```

> 来源：[Gradle 官方文档](https://docs.gradle.org/current/userguide/userguide.html)
