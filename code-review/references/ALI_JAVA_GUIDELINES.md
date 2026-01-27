# Alibaba Java Coding Guidelines - Quick Reference

Summary of key rules from Alibaba Java Coding Guidelines for code review.

## 1. Naming Conventions

- [Class names](#): PascalCase, e.g., `UserService`, `OrderController`
- [Method/variable names](#): camelCase, e.g., `getUserById`, `userName`
- [Constants](#): All uppercase with underscores, e.g., `MAX_RETRY_COUNT`
- [Booleans](#): Start with `is/has/can/should`, e.g., `isSuccess`, `hasPermission`
- [Exceptions](#): End with `Exception`, e.g., `BusinessException`
- [Test classes](#): End with `Test`, e.g., `UserServiceTest`

## 2. OOP Principles

- [Avoid using Boolean in database](#): Use `TINYINT(1)` or `BIT(1)` instead
- [Avoid returning collections as null](#): Return empty collections instead
- [Avoid modifying method parameters](#): Parameters should be treated as final
- [Use constructor for required fields](#): Use builder/setters for optional fields
- [Avoid `new String("abc")`](#): Direct assignment is more efficient

## 3. Collection Processing

- [Don't convert Collection to Array just to iterate](#): Use enhanced for-loop directly
- [Use `isEmpty()` instead of `size() == 0`](#): More readable and consistent
- [Initialize collection with expected size](#): `new ArrayList<>(expectedSize)` avoids resizing
- [SubList warnings](#): SubList is view, modifying original affects subList
- [HashMap iteration](#): Use `entrySet()` instead of `keySet()` when you need both key and value
- [Don't return mutable static collections](#): Wrap with `Collections.unmodifiableXXX()`

## 4. Concurrency

- [Avoid using `synchronized` on String](#): String literals are interned, different locks may be used
- [Prefer `ConcurrentHashMap`](#): Instead of `Collections.synchronizedMap(new HashMap())`
- [Thread pools](#): Always provide meaningful names for debugging
- [Volatile](#): Only ensures visibility, doesn't guarantee atomicity
- [Lock](#): Always unlock in `finally` block

## 5. Control Flow

- [Avoid complex conditions](#): Extract to named methods
- [Avoid deep nesting](#): Early return to reduce nesting levels
- [Magic numbers](#): Define as constants
- [Switch statements](#): Must have `default` case, add `// fall through` for intentional fall-through

## 6. Exception Handling

- [Don't catch `Exception` broadly](#): Catch specific exceptions
- [Don't swallow exceptions](#): At least log them
- [Don't use `e.printStackTrace()`](#): Use logger
- [Don't return null in catch](#): Throw exception or return default value
- [Try-catch in transaction](#): Don't let exceptions cross transaction boundaries
- [Finally block](#): Never use `return` in `finally` block

## 7. Logging

- [Avoid string concatenation in logs](#): Use parameterized logging
  - ❌ `log.info("User: " + user + " logged in")`
  - ✅ `log.info("User: {} logged in", user)`
- [Log exceptions correctly](#): `log.error("Message", exception)` instead of `log.error("Message: " + exception)`
- [Use appropriate levels](#): ERROR for exceptions, WARN for recoverable issues, INFO for normal operations
- [Don't log sensitive data](#): Passwords, tokens, PII

## 8. Database

- [Close resources](#): Use try-with-resources for Connection, Statement, ResultSet
- [Don't use `SELECT *`](#): Specify columns explicitly
- [Avoid N+1 queries](#): Use JOIN or batch queries
- [Use batch operations](#): For multiple inserts/updates
- [Transaction boundaries](#): Keep transactions short

## 9. IO & Resource Management

- [Use try-with-resources](#): For all AutoCloseable resources
- [Buffer IO operations](#): Use `BufferedInputStream`, `BufferedOutputStream`
- [Character encoding](#): Always specify encoding explicitly (UTF-8)
- [Close streams in correct order](#): Reverse order of opening

## 10. Security

- [Avoid SQL injection](#): Use parameterized queries
- [Validate input](#): Never trust user input
- [Don't log passwords](#): Even in errors
- [Avoid deserialization of untrusted data](#): Validate and whitelist
- [Path traversal](#): Validate and normalize file paths
- [XSS prevention](#): Encode user input before rendering to HTML

## 11. Performance

- [Avoid auto-boxing/unboxing](#): Especially in loops
- [Use `StringBuilder`](#): For string concatenation in loops
- [String comparison](#): Use `equals()` not `==` (except for `intern()` strings)
- [BigDecimal comparison](#): Use `compareTo()` not `equals()` for precision
- [Date handling](#): Use `Instant`, `LocalDateTime` not `Date`
- [Avoid excessive object creation](#): Especially in hot paths

## 12. JSON Processing

- [Never return null](#): Return empty collections or use `@JsonSerialize(nullsUsing = NullSerializer.class)`
- [Field naming](#): Use `@JsonProperty` for different naming
- [Ignore unknown properties](#): `@JsonIgnoreProperties(ignoreUnknown = true)`

## 13. Comments

- [Explain "why", not "what"](1): Code should be self-documenting
- [Javadoc](#): Required for public APIs
- [Outdated comments](#): Worse than no comments
- [TODO/FIXME](#): Include owner and date

## Code Review Checklist Based on Guidelines

### Must-Fix Before Commit (Critical)

- Unclosed resources (IO, DB, Network)
- SQL injection vulnerabilities
- Null pointer exceptions (unvalidated nulls)
- Dead code or commented code blocks
- Hardcoded credentials or secrets

### Should-Fix (High)

- Broad exception catching
- Missing input validation
- Magic numbers without constants
- Empty catch blocks
- Performance issues (N+1, missing indexes)

### Nice-to-Have (Medium)

- Inconsistent naming
- Missing Javadoc for public methods
- Complex methods (> 50 lines)
- Deep nesting (> 3 levels)
- Missing logging

## Common Anti-Patterns

```java
// ❌ Bad: Unclosed resource
InputStream is = new FileInputStream(file);
process(is);

// ✅ Good: try-with-resources
try (InputStream is = new FileInputStream(file)) {
    process(is);
}

// ❌ Bad: SQL injection
"SELECT * FROM user WHERE id = " + id

// ✅ Good: Parameterized query
"SELECT * FROM user WHERE id = ?"

// ❌ Bad: String concatenation in log
log.info("Processing user: " + user.getName());

// ✅ Good: Parameterized logging
log.info("Processing user: {}", user.getName());

// ❌ Bad: Auto-boxing in loop
List<Integer> list = new ArrayList<>();
for (int i = 0; i < 1000; i++) {
    list.add(i);  // Auto-boxes every iteration
}

// ✅ Good: Primitive collection (if applicable) or handle differently
IntStream.range(0, 1000).boxed().collect(Collectors.toList());

// ❌ Bad: Return null
public List<User> getUsers() {
    if (empty) {
        return null;
    }
    return users;
}

// ✅ Good: Return empty collection
public List<User> getUsers() {
    if (empty) {
        return Collections.emptyList();
    }
    return users;
}
```
