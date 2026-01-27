# Security Vulnerability Detection Checklist

Detailed checklist for identifying security vulnerabilities in Java code.

## 1. SQL Injection (Critical)

### Patterns

**String concatenation in SQL queries**

```java
// ❌ CRITICAL: SQL Injection
public User getUser(String id) {
    String sql = "SELECT * FROM user WHERE id = " + id;
    return jdbcTemplate.query(sql, userMapper);
}

// ✅ GOOD: Parameterized query
public User getUser(String id) {
    String sql = "SELECT * FROM user WHERE id = ?";
    return jdbcTemplate.query(sql, new Object[]{id}, userMapper);
}

// ✅ GOOD: Named parameters (MyBatis)
@Select("SELECT * FROM user WHERE id = #{id}")
User getUser(@Param("id") String id);
```

**Dynamic table/column names**

```java
// ❌ CRITICAL: SQL Injection in table name
public List<User> query(String tableName) {
    String sql = "SELECT * FROM " + tableName;  // Vulnerable!
    return jdbcTemplate.query(sql, userMapper);
}

// ✅ GOOD: Whitelist table names
public List<User> query(String tableName) {
    Set<String> allowedTables = Set.of("user", "order", "product");
    if (!allowedTables.contains(tableName.toLowerCase())) {
        throw new SecurityException("Invalid table name");
    }
    String sql = "SELECT * FROM " + tableName;  // Safe due to whitelist
    return jdbcTemplate.query(sql, userMapper);
}
```

### Checklist

- [ ] No string concatenation in SQL queries
- [ ] All user input is parameterized
- [ ] Dynamic table/column names are whitelisted
- [ ] Use JPA/Hibernate/MyBatis parameter binding
- [ ] No `Statement.execute(String)` with user input

## 2. Deserialization Vulnerabilities (Critical)

### Patterns

**Unsafe deserialization**

```java
// ❌ CRITICAL: Unsafe deserialization
public void process(byte[] data) throws Exception {
    ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));
    Object obj = ois.readObject();  // Can execute arbitrary code!
}

// ✅ GOOD: Use safe format
public void process(byte[] data) throws Exception {
    // Use JSON, XML, or other safe formats
    User user = objectMapper.readValue(data, User.class);
}

// ✅ GOOD: Validate and filter (if ObjectInputStream is required)
public void process(byte[] data) throws Exception {
    ObjectInputStreamFilter filter = new ObjectInputFilter() {
        @Override
        public Status checkInput(FilterInfo filterInfo) {
            if (filterInfo.depth() > 100) {
                return Status.REJECTED;
            }
            if (filterInfo.arrayLength() > 1000000) {
                return Status.REJECTED;
            }
            return Status.UNDECIDED;
        }
    };
    ObjectInputFilter.Config.setSerialFilter(filter);
    ObjectInputStream ois = new ObjectInputStream(...);
    Object obj = ois.readObject();
}
```

**XML external entities (XXE)**

```java
// ❌ CRITICAL: XXE vulnerability
public Document parseXml(String xml) throws Exception {
    DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
    DocumentBuilder builder = factory.newDocumentBuilder();
    return builder.parse(new InputSource(new StringReader(xml)));
}

// ✅ GOOD: Disable XXE
public Document parseXml(String xml) throws Exception {
    DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
    factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
    factory.setXIncludeAware(false);
    factory.setExpandEntityReferences(false);
    DocumentBuilder builder = factory.newDocumentBuilder();
    return builder.parse(new InputSource(new StringReader(xml)));
}
```

### Checklist

- [ ] No `ObjectInputStream.readObject()` without validation
- [ ] XML parsers have XXE protection disabled
- [ ] Use JSON instead of Java serialization when possible
- [ ] Implement ObjectInputFilter for deserialization
- [ ] Verify deserialized objects against schema

## 3. Path Traversal (Critical)

### Patterns

**Unvalidated file paths**

```java
// ❌ CRITICAL: Path traversal
public void readFile(String filename) throws IOException {
    File file = new File("/var/data/" + filename);  // Vulnerable to ../../
    return Files.readAllBytes(file.toPath());
}

// ✅ GOOD: Validate and normalize path
public void readFile(String filename) throws IOException {
    File file = new File("/var/data/").toPath()
            .resolve(filename)
            .normalize()
            .toFile();
    if (!file.toPath().startsWith("/var/data/")) {
        throw new SecurityException("Path traversal attempt");
    }
    return Files.readAllBytes(file.toPath());
}

// ✅ GOOD: Use canonical path check
public void readFile(String filename) throws IOException {
    File file = new File("/var/data/" + filename);
    String canonicalPath = file.getCanonicalPath();
    if (!canonicalPath.startsWith("/var/data/")) {
        throw new SecurityException("Invalid path");
    }
    return Files.readAllBytes(file.toPath());
}
```

### Checklist

- [ ] All file paths are validated
- [ ] All file paths are normalized
- [ ] All file paths are checked against expected directory
- [ ] No `../` in user-controlled paths
- [ ] Use `Path.resolve()` instead of string concatenation

## 4. Authentication & Authorization (Critical)

### Patterns

**Hardcoded credentials**

```java
// ❌ CRITICAL: Hardcoded credentials
public class DatabaseConfig {
    private static final String DB_PASSWORD = "admin123";
}

// ❌ CRITICAL: Credentials in code
String password = "pwd=secretpassword";

// ✅ GOOD: Use environment variables
public class DatabaseConfig {
    private static final String DB_PASSWORD = System.getenv("DB_PASSWORD");
}

// ✅ GOOD: Use configuration files (encrypted)
@Value("${db.password}")
private String dbPassword;
```

**Missing authorization**

```java
// ❌ BAD: No authorization check
public User getUser(String userId) {
    return userRepository.findById(userId);  // Anyone can get any user!
}

// ✅ GOOD: Check authorization
public User getUser(String userId, User currentUser) {
    if (!currentUser.hasPermission(userId)) {
        throw new AccessDeniedException("No permission");
    }
    return userRepository.findById(userId);
}

// ✅ GOOD: Use security annotations
@PreAuthorize("hasPermission(#userId, 'read')")
public User getUser(String userId) {
    return userRepository.findById(userId);
}
```

**Session fixation**

```java
// ❌ BAD: Session ID from URL
public void login(HttpServletRequest request) {
    String sessionId = request.getParameter("sessionId");
    request.getSession().setId(sessionId);  // Vulnerable!
}

// ✅ GOOD: Generate new session
public void login(HttpServletRequest request) {
    User user = authenticate(username, password);
    request.getSession(true);  // Invalidate old session
    request.getSession().setAttribute("user", user);
}
```

### Checklist

- [ ] No hardcoded passwords or API keys
- [ ] All sensitive methods have authorization checks
- [ ] Session IDs are regenerated on login
- [ ] Session IDs are not in URLs
- [ ] Multi-factor authentication for sensitive operations
- [ ] Password complexity requirements enforced

## 5. Cross-Site Scripting (XSS) (High)

### Patterns

**Unsanitized output**

```java
// ❌ HIGH: XSS vulnerability
@GetMapping("/hello")
public String hello(@RequestParam String name) {
    return "<h1>Hello, " + name + "</h1>";  // Reflected XSS
}

// ✅ GOOD: Escape output
@GetMapping("/hello")
public String hello(@RequestParam String name) {
    return "<h1>Hello, " + HtmlUtils.htmlEscape(name) + "</h1>";
}

// ✅ GOOD: Use template engine (Thymeleaf)
@GetMapping("/hello")
public String hello(Model model, @RequestParam String name) {
    model.addAttribute("name", name);  // Auto-escaped
    return "hello";
}

// ✅ GOOD: Use Content Security Policy headers
@GetMapping("/secure")
public String secure() {
    return "content";
}
// In controller or filter:
response.setHeader("Content-Security-Policy", "default-src 'self'");
```

### Checklist

- [ ] All user output is escaped
- [ ] All user input is validated
- [ ] Content Security Policy headers set
- [ ] Use template engines with auto-escaping
- [ ] No innerHTML with user content
- [ ] No eval() with user input

## 6. Input Validation (High)

### Patterns

**Missing validation**

```java
// ❌ BAD: No validation
public void process(String input) {
    int value = Integer.parseInt(input);  // Can throw NumberFormatException
}

// ✅ GOOD: Validate input
public void process(String input) {
    if (input == null || input.isEmpty() || input.length() > 100) {
        throw new ValidationException("Invalid input");
    }
    int value = Integer.parseInt(input);
}

// ✅ GOOD: Use validation annotations
public void process(@NotNull @Size(min = 1, max = 100) String input) {
    // Validated automatically
}
```

**Command injection**

```java
// ❌ CRITICAL: Command injection
public void execute(String command) {
    Runtime.getRuntime().exec("cmd /c " + command);  // Vulnerable!
}

// ✅ GOOD: Don't execute user commands directly
public void execute(String command) {
    Set<String> allowedCommands = Set.of("list", "status", "version");
    if (!allowedCommands.contains(command)) {
        throw new SecurityException("Invalid command");
    }
    Runtime.getRuntime().exec(getCommand(command));
}

// ✅ GOOD: Use ProcessBuilder with proper validation
public void execute(String command) {
    ProcessBuilder pb = new ProcessBuilder(getCommand(command));
    pb.redirectErrorStream(true);
    Process process = pb.start();
}
```

### Checklist

- [ ] All input validated for null
- [ ] All input validated for length
- [ ] All input validated for format (regex)
- [ ] No command execution with user input
- [ ] All file operations validate paths
- [ ] All SQL queries parameterized
- [ ] Regex patterns have timeouts (prevent ReDoS)

## 7. Sensitive Data Handling (Critical)

### Patterns

**Logging sensitive data**

```java
// ❌ CRITICAL: Logging password
public void login(String username, String password) {
    log.info("Login attempt: username=" + username + ", password=" + password);
}

// ✅ GOOD: Don't log passwords
public void login(String username, String password) {
    log.info("Login attempt: username={}", username);
    // Never log passwords
}

// ❌ BAD: Logging sensitive data in exception
try {
    paymentService.process(creditCard);
} catch (Exception e) {
    log.error("Payment failed: " + creditCard, e);  // Logs credit card!
}

// ✅ GOOD: Don't log sensitive data
try {
    paymentService.process(creditCard);
} catch (Exception e) {
    log.error("Payment failed for card: {}", maskCard(creditCard), e);
}
```

**Storing passwords in plain text**

```java
// ❌ CRITICAL: Plain text passwords
public class User {
    private String password;
}

// ✅ GOOD: Hash passwords
public class User {
    private String passwordHash;  // BCrypt, Argon2, or PBKDF2
}
```

### Checklist

- [ ] No passwords logged
- [ ] No credit card numbers logged
- [ ] No PII logged without consent
- [ ] All passwords hashed (not encrypted)
- [ ] Use strong hashing algorithms (BCrypt, Argon2)
- [ ] Sensitive data encrypted at rest
- [ ] HTTPS/TLS for sensitive data in transit

## 8. Insecure Dependencies (High)

### Patterns

**Outdated vulnerable libraries**

```bash
# Check for vulnerable dependencies
mvn dependency-check:check
# or
./gradle dependencyCheck

# Review results
# High/Critical vulnerabilities must be fixed
```

### Checklist

- [ ] All dependencies up to date
- [ ] No known vulnerabilities in dependencies (check with OWASP Dependency Check)
- [ ] All third-party libraries vetted
- [ ] No abandoned libraries in use

## 9. Cryptographic Issues (Critical)

### Patterns

**Weak encryption**

```java
// ❌ CRITICAL: Weak algorithm
Cipher cipher = Cipher.getInstance("DES");

// ✅ GOOD: Strong algorithm
Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");

// ❌ CRITICAL: ECB mode
Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");

// ✅ GOOD: GCM mode (authenticated encryption)
Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
```

**Weak random**

```java
// ❌ BAD: Predictable random
Random random = new Random();
int id = random.nextInt(1000000);

// ✅ GOOD: Cryptographically secure random
SecureRandom secureRandom = new SecureRandom();
int id = secureRandom.nextInt(1000000);
```

### Checklist

- [ ] Use AES-256 for encryption
- [ ] Use GCM or CBC mode with HMAC
- [ ] Use SecureRandom for cryptographic operations
- [ ] Never use MD5 or SHA-1 for passwords
- [ ] Never use ECB mode
- [ ] Use proper key management

## 10. Race Conditions (High)

### Patterns

**Check-then-act race**

```java
// ❌ BAD: TOCTOU race condition
public void transfer(String from, String to, BigDecimal amount) {
    if (accountService.getBalance(from).compareTo(amount) >= 0) {  // Check
        accountService.transfer(from, to, amount);  // Act
    }
}

// ✅ GOOD: Atomic operation
@Transactional
public void transfer(String from, String to, BigDecimal amount) {
    BigDecimal balance = accountService.getBalance(from);
    if (balance.compareTo(amount) >= 0) {
        accountService.deduct(from, amount);
        accountService.add(to, amount);
    }
}

// ✅ GOOD: Use database constraints
UPDATE account SET balance = balance - ? WHERE id = ? AND balance >= ?
```

### Checklist

- [ ] Critical operations in transactions
- [ ] Use database locks for concurrent access
- [ ] Use atomic operations when possible
- [ ] No check-then-act without synchronization

## Quick Scan Patterns

Grep for these patterns to find potential security issues:

```bash
# String concatenation in SQL
grep -rn "SELECT.*+" *.java
grep -rn "INSERT.*+" *.java
grep -rn "UPDATE.*+" *.java

# Hardcoded passwords
grep -rn "password=" *.java
grep -rn "pwd=" *.java
grep -rn "secret=" *.java

# Command execution
grep -rn "Runtime.getRuntime().exec" *.java
grep -rn "ProcessBuilder" *.java

# Unsafe deserialization
grep -rn "ObjectInputStream" *.java

# Logging sensitive data
grep -rn "log.*password" *.java
grep -rn "log.*creditCard" *.java
grep -rn "log.*token" *.java
```

## Security Tools

### Static Analysis

- **OWASP Dependency-Check**: Check for vulnerable dependencies
- **SpotBugs**: Find bugs and security issues
- **SonarQube**: Code quality with security rules
- **Checkmarx**: Commercial security scanner
- **Veracode**: Commercial security scanner

### Dynamic Analysis

- **OWASP ZAP**: Web application security scanner
- **Burp Suite**: Web application security testing
- **SQLMap**: Automated SQL injection testing

## Review Checklist for Each Change

For each code change, verify:

- [ ] No SQL injection vulnerabilities
- [ ] No command injection vulnerabilities
- [ ] No path traversal vulnerabilities
- [ ] All input validated and sanitized
- [ ] All output properly escaped
- [ ] No hardcoded credentials
- [ ] All sensitive data encrypted at rest
- [ ] All sensitive data in transit encrypted (TLS)
- [ ] Authentication required for sensitive operations
- [ ] Authorization checks in place
- [ ] No unsafe deserialization
- [ ] No XXE vulnerabilities
- [ ] Secure random numbers used
- [ ] Strong cryptographic algorithms used
- [ ] Dependencies up to date and secure
- [ ] Error messages don't leak sensitive information
