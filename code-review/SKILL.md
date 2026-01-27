---
name: code-review
description: Comprehensive Java code review focused on Alibaba Java Coding Guidelines, with emphasis on memory leaks, security vulnerabilities, performance issues, and code style problems. Use when Claude needs to review Java code changes before Git commits or merge requests.
---

# Code Review

## Quick Start

Review Java code changes systematically using the checklist below. For each review, check against four major categories: memory leaks, security vulnerabilities, performance issues, and code style.

## Review Categories

### 1. Memory Leaks (Critical)

Check these common patterns:

**Resource Management**
- Unclosed resources: `InputStream`, `OutputStream`, `Connection`, `Statement`, `ResultSet`, `File`, `Socket`
- Missing `try-with-resources` or `finally` blocks
- Unreleased database connections in exception paths
- Thread pools not shutdown on application exit
- Uncached buffers: `BufferedImage`, `ByteBuffer`, custom buffers

**Collection & Object References**
- Static `Collection`/`Map` that grows indefinitely
- Unbounded caches without eviction policy (e.g., `HashMap` used as cache)
- Listener/event handler lists not removed
- `ThreadLocal` not cleaned up
- Circular references in custom objects

**Concurrency Issues**
- Thread-safe collections used incorrectly
- Improper synchronization leading to thread leaks
- Executors without proper shutdown hooks

**Memory Hotspots**
- Large objects created in loops
- String concatenation in loops (use `StringBuilder`)
- Auto-boxing/unboxing in hot paths
- Excessive object allocation in frequently called methods

### 2. Security Vulnerabilities (Critical)

Check these security issues:

**SQL Injection**
- String concatenation in SQL queries: `"SELECT * FROM user WHERE id = " + id`
- Missing parameterized queries
- Dynamic SQL without validation

**Deserialization**
- Unsafe deserialization of untrusted data
- Missing `readObject()` validation
- `ObjectInputStream` without filtering

**XXE (XML External Entity)**
- `DocumentBuilder` without security features
- Unvalidated XML parsing
- External entity resolution enabled

**Path Traversal**
- Unvalidated file paths in `File()` operations
- Missing path normalization

**Authentication & Authorization**
- Hardcoded credentials (check for: `password=`, `pwd=`, `secret=`)
- Missing permission checks
- Session management issues

**Cross-Site Scripting (XSS)**
- Unsanitized output to HTML/JavaScript
- Missing encoding in response bodies

**Input Validation**
- Missing null checks
- No length validation on user input
- Regex without timeouts (ReDoS)

### 3. Performance Issues (High)

Check these performance patterns:

**Database Access**
- N+1 query problem (querying inside loops)
- Missing indexes on query conditions
- Fetching all columns when only few needed
- Large batch operations without batching
- Missing pagination on large datasets

**Caching**
- Missing cache on frequently accessed data
- Cache without TTL (time-to-live)
- Cache key collisions
- Double-checked locking issues

**Concurrency**
- Excessive synchronization contention
- Lock ordering issues (deadlock risk)
- Unsafe lazy initialization

**Algorithm & Data Structures**
- O(n²) algorithms where O(n log n) is possible
- `ArrayList` used for frequent insertions in middle
- Incorrect `equals()`/`hashCode()` implementation causing performance degradation

**Network & IO**
- Missing connection pooling
- Unnecessary network calls
- Large data transfers without compression

### 4. Code Style (Based on Alibaba Java Guidelines)

Check these style issues:

**Naming Conventions**
- Class names: PascalCase (e.g., `UserService`)
- Method/variable names: camelCase (e.g., `getUserById`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_COUNT`)
- Package names: lowercase (e.g., `com.qunar.service`)

**Code Structure**
- Line length: Avoid > 120 characters
- Method complexity: Cyclomatic complexity < 10
- Method length: Prefer < 50 lines
- Class length: Prefer < 500 lines
- Deep nesting: Avoid > 3 levels

**Best Practices**
- Magic numbers: Replace with named constants
- Exception handling: Don't catch `Exception` broadly, handle specific exceptions
- Null checks: Use `Objects.requireNonNull()` or Optional
- Logging: Don't concatenate strings in log calls (use parameterized logging)
- Comments: Explain "why", not "what"

**Design Patterns**
- Single Responsibility: Each class/method does one thing
- DRY: Don't repeat code, extract common logic
- SOLID principles: Open/closed, Liskov substitution, interface segregation, dependency inversion

## Review Process

1. **Understand the Context**
   - What does this code change do?
   - What are the business requirements?
   - Are there any special constraints or assumptions?

2. **Check Against Categories**
   - Go through each category: Memory, Security, Performance, Style
   - For each category, scan the code systematically
   - Mark issues with severity: **CRITICAL**, **HIGH**, **MEDIUM**, **LOW**

3. **Document Findings**
   - File path and line number
   - Category and severity
   - Description of the issue
   - Code snippet (if applicable)
   - Recommended fix with example

4. **Provide Summary**
   - Total issues found by category and severity
   - Overall assessment (Pass / Needs Revision / Rejected)
   - Priority fixes required before commit

## Issue Reporting Format

```
## [CRITICAL] Memory Leak - Unclosed InputStream

**Location**: `src/main/java/.../FileProcessor.java:45`

**Issue**:
The InputStream is not closed in the exception path, leading to resource leak.

**Code**:
```java
InputStream is = new FileInputStream(file);
process(is);  // May throw exception
is.close();
```

**Fix**:
Use try-with-resources:
```java
try (InputStream is = new FileInputStream(file)) {
    process(is);
}
```

**Reference**: Alibaba Java Guidelines - Resource Management
```

## Reference Materials

For detailed rules and examples, see:
- [ALI_JAVA_GUIDELINES.md](references/ALI_JAVA_GUIDELINES.md) - Complete Alibaba Java Coding Guidelines
- [MEMORY_CHECKLIST.md](references/MEMORY_CHECKLIST.md) - Detailed memory leak patterns
- [SECURITY_CHECKLIST.md](references/SECURITY_CHECKLIST.md) - Security vulnerability patterns

## Automation

For automated checks, run scripts:
- `scripts/check_style.py` - Basic style validation
- `scripts/find_memory_leaks.py` - Detect potential memory leak patterns

## Usage Notes

- This skill provides **guidance** and **checklist-based review**, not automated analysis
- Use in combination with existing CI/CD tools (SonarQube, SpotBugs, FindBugs)
- Focus on issues that require human judgment: business logic, edge cases, design patterns
- Always consider context: code that looks problematic may be intentional for performance or compatibility
