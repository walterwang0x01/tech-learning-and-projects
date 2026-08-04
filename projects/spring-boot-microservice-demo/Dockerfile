# 多阶段构建 Dockerfile
FROM maven:3.9-eclipse-temurin-17 AS build

WORKDIR /app

# 复制 pom 文件
COPY pom.xml .
COPY common-lib/pom.xml ./common-lib/
COPY user-service/pom.xml ./user-service/

# 下载依赖
RUN mvn dependency:go-offline -B

# 复制源代码
COPY . .

# 构建应用
RUN mvn clean package -DskipTests

# 运行阶段
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# 复制构建产物
COPY --from=build /app/user-service/target/user-service-*.jar app.jar

# 创建非 root 用户
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

EXPOSE 8081

ENTRYPOINT ["java", "-jar", "app.jar"]

