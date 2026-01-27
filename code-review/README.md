# Code Review Skill 使用说明

## 简介

此 skill 用于 Java 代码审查，重点关注：
- **内存泄漏** (Memory Leaks)
- **安全漏洞** (Security Vulnerabilities)
- **性能问题** (Performance Issues)
- **代码风格** (Code Style)

基于阿里巴巴 Java 开发手册和最佳实践。

## 使用方法

### 方式 1: 在对话中调用

当需要审查代码时，直接说：

```
/code-review
请审查这个文件: src/main/java/xxx.java
```

或

```
/code-review
请审查这次提交的变更
```

### 方式 2: 自动化脚本

在提交前运行脚本进行快速检查：

```bash
# 检查内存泄漏问题
python skills/code-review/scripts/find_memory_leaks.py src/main/java

# 检查代码风格问题
python skills/code-review/scripts/check_style.py src/main/java
```

### 方式 3: 配置 Git Hook

在项目 `.git/hooks/pre-commit` 中添加：

```bash
#!/bin/bash

echo "Running code review before commit..."

# 检查内存泄漏
python ~/.claude/skills/code-review/scripts/find_memory_leaks.py src/main/java

# 检查代码风格
python ~/.claude/skills/code-review/scripts/check_style.py src/main/java

echo "Code review check completed."
```

## 审查流程

1. **理解上下文** - 了解代码变更的目的和业务需求
2. **检查问题** - 按照清单系统检查四类问题
3. **记录发现** - 按标准格式记录问题和修复建议
4. **提供总结** - 给出总体评估和建议

## 问题严重级别

- **CRITICAL** - 必须修复，否则可能导致严重后果
- **HIGH** - 强烈建议修复，可能影响系统稳定性
- **MEDIUM** - 建议修复，提高代码质量
- **LOW** - 可选修复，改善代码可维护性

## 常见问题示例

### 内存泄漏

```java
// ❌ BAD: InputStream 未关闭
InputStream is = new FileInputStream(file);
process(is);

// ✅ GOOD: 使用 try-with-resources
try (InputStream is = new FileInputStream(file)) {
    process(is);
}
```

### 安全漏洞

```java
// ❌ BAD: SQL 注入
String sql = "SELECT * FROM user WHERE id = " + id;

// ✅ GOOD: 参数化查询
String sql = "SELECT * FROM user WHERE id = ?";
```

### 性能问题

```java
// ❌ BAD: N+1 查询
for (User user : users) {
    List<Order> orders = orderService.getOrders(user.getId());
}

// ✅ GOOD: 批量查询
List<Order> orders = orderService.getOrders(userIds);
```

### 代码风格

```java
// ❌ BAD: 魔法数字
if (count > 100) { }

// ✅ GOOD: 使用常量
private static final int MAX_COUNT = 100;
if (count > MAX_COUNT) { }
```

## 参考文档

详细的检查清单和规则：

- [ALI_JAVA_GUIDELINES.md](references/ALI_JAVA_GUIDELINES.md) - 阿里巴巴 Java 开发手册速查
- [MEMORY_CHECKLIST.md](references/MEMORY_CHECKLIST.md) - 内存泄漏详细检查清单
- [SECURITY_CHECKLIST.md](references/SECURITY_CHECKLIST.md) - 安全漏洞详细检查清单

## 工具集成

建议结合以下工具使用：

- **SonarQube** - 代码质量和安全规则
- **SpotBugs** - Bug 检测
- **FindBugs** - 静态分析
- **OWASP Dependency-Check** - 依赖漏洞检查

## 贡献

如需添加新的检查规则或改进现有规则，请：

1. 在 `references/` 中添加详细文档
2. 在 `scripts/` 中添加或更新检查脚本
3. 更新 `SKILL.md` 中的相关说明

## License

MIT License
