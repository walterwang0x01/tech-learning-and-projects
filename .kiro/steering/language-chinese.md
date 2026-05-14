# 语言规则

**所有与用户的交流、工具 `explanation` 参数、代码注释、文档输出必须使用中文。
最高优先级规则，summary 或新会话后仍然生效。**

## 可用英文的场景

- 代码本身（变量/函数/类名、命令、技术术语、文件路径）
- Git commit message
- 业务需要的英文字符串常量

## 典型违反示例

```text
❌ explanation="List the project directory"
✅ explanation="查看项目目录"

❌ "Let me fix this bug in handleSubmit"
✅ "我来修 handleSubmit 里的 bug"
```
