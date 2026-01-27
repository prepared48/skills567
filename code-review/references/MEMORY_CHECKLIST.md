# Memory Leak Detection Checklist

Detailed checklist for identifying memory leak patterns in Java code.

## 1. Resource Leaks

### 1.1 IO Resources

**Pattern**: File operations without proper cleanup

```java
// ❌ BAD
public void readFile(String path) {
    InputStream is = new FileInputStream(path);
    byte[] data = new byte[1024];
    is.read(data);
    // Exception may prevent close()
}

// ✅ GOOD
public void readFile(String path) {
    try (InputStream is = new FileInputStream(path)) {
        byte[] data = new byte[1024];
        is.read(data);
    }
}
```

**Checklist**:
- [ ] All `InputStream`, `OutputStream` wrapped in try-with-resources
- [ ] All `FileReader`, `FileWriter` wrapped in try-with-resources
- [ ] All `BufferedReader`, `BufferedWriter` wrapped in try-with-resources
- [ ] Exception paths properly close resources

### 1.2 Network Resources

**Pattern**: Sockets and HTTP connections not closed

```java
// ❌ BAD
public void sendData(String url, String data) {
    HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
    conn.setRequestMethod("POST");
    // Connection not closed
}

// ✅ GOOD
public void sendData(String url, String data) {
    HttpURLConnection conn = null;
    try {
        conn = (HttpURLConnection) new URL(url).openConnection();
        conn.setRequestMethod("POST");
    } finally {
        if (conn != null) {
            conn.disconnect();
        }
    }
}
```

**Checklist**:
- [ ] All `Socket` objects closed in finally
- [ ] All `HttpURLConnection` objects disconnected
- [ ] All `ServerSocket` objects closed
- [ ] Connection pools properly shutdown on application exit

### 1.3 Database Resources

**Pattern**: JDBC connections not closed

```java
// ❌ BAD
public User getUser(String id) {
    Connection conn = dataSource.getConnection();
    Statement stmt = conn.createStatement();
    ResultSet rs = stmt.executeQuery("SELECT * FROM user WHERE id = " + id);
    // Resources not closed

// ✅ GOOD
public User getUser(String id) {
    try (Connection conn = dataSource.getConnection();
         Statement stmt = conn.createStatement();
         ResultSet rs = stmt.executeQuery("SELECT * FROM user WHERE id = " + id)) {
        // Process results
    }
}
```

**Checklist**:
- [ ] All `Connection` objects closed
- [ ] All `Statement`, `PreparedStatement` objects closed
- [ ] All `ResultSet` objects closed
- [ ] Use try-with-resources for all JDBC operations

### 1.4 Thread Resources

**Pattern**: Thread pools not shutdown

```java
// ❌ BAD
public class Processor {
    private ExecutorService executor = Executors.newFixedThreadPool(10);
    // No shutdown method
}

// ✅ GOOD
public class Processor implements AutoCloseable {
    private final ExecutorService executor;

    public Processor() {
        this.executor = Executors.newFixedThreadPool(10);
    }

    @Override
    public void close() {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}
```

**Checklist**:
- [ ] All `ExecutorService` objects have shutdown logic
- [ ] All `ScheduledExecutorService` objects have shutdown logic
- [ ] Shutdown called in `@PreDestroy` or `@PreDestroy` methods
- [ ] Threads created with `new Thread()` are properly joined/terminated

### 1.5 Graphics & NIO Resources

**Pattern**: Buffers and graphics objects not released

```java
// ❌ BAD
public BufferedImage processImage(File file) {
    BufferedImage img = ImageIO.read(file);
    Graphics2D g = img.createGraphics();
    g.drawImage(...);
    // Graphics not disposed
    return img;
}

// ✅ GOOD
public BufferedImage processImage(File file) {
    BufferedImage img = ImageIO.read(file);
    Graphics2D g = img.createGraphics();
    try {
        g.drawImage(...);
        return img;
    } finally {
        g.dispose();
    }
}
```

**Checklist**:
- [ ] All `Graphics2D` objects disposed
- [ ] All `ByteBuffer` objects released (if direct buffers)
- [ ] All `Channel` objects (NIO) closed
- [ ] All `FileChannel` objects closed

## 2. Collection & Data Structure Leaks

### 2.1 Unbounded Collections

**Pattern**: Collections that grow indefinitely

```java
// ❌ BAD
public class Cache {
    private Map<String, Object> cache = new HashMap<>();
    // Cache grows forever
}

// ✅ GOOD
public class Cache {
    private final LoadingCache<String, Object> cache = CacheBuilder.newBuilder()
            .maximumSize(1000)
            .expireAfterWrite(10, TimeUnit.MINUTES)
            .build(CacheLoader.from(...));
}
```

**Checklist**:
- [ ] All static `Map`/`Collection` have size limits or eviction policy
- [ ] All caches have TTL (time-to-live)
- [ ] All caches have maximum size limits
- [ ] Consider using `WeakHashMap`, `Guava Cache`, `Caffeine`

### 2.2 Listener Lists

**Pattern**: Listeners added but never removed

```java
// ❌ BAD
public class EventSource {
    private List<EventListener> listeners = new ArrayList<>();

    public void addListener(EventListener listener) {
        listeners.add(listener);  // Never removed
    }
}

// ✅ GOOD
public class EventSource {
    private List<EventListener> listeners = new ArrayList<>();

    public void addListener(EventListener listener) {
        listeners.add(listener);
    }

    public void removeListener(EventListener listener) {
        listeners.remove(listener);  // Important!
    }

    // Or use WeakReference
    private List<WeakReference<EventListener>> listeners = new ArrayList<>();
}
```

**Checklist**:
- [ ] All listener lists have removal methods
- [ ] Listeners removed when no longer needed
- [ ] Consider `WeakReference` for long-lived listeners

### 2.3 ThreadLocal Issues

**Pattern**: ThreadLocal values not cleaned up

```java
// ❌ BAD
public class UserContext {
    private static final ThreadLocal<User> user = new ThreadLocal<>();
    // Value persists after request ends
}

// ✅ GOOD
public class UserContext implements Filter {
    private static final ThreadLocal<User> user = new ThreadLocal<>();

    public void doFilter(...) {
        try {
            user.set(getUserFromRequest());
            chain.doFilter(...);
        } finally {
            user.remove();  // Critical!
        }
    }
}
```

**Checklist**:
- [ ] All `ThreadLocal` values removed in `finally` blocks
- [ ] ThreadLocal cleanup done in servlet filters
- [ ] ThreadLocal cleanup done in filter/interceptor lifecycle methods

## 3. Common Leak Patterns

### 3.1 Static Fields

```java
// ❌ BAD: Static collection holds references forever
public class DataCache {
    private static Map<String, Object> cache = new HashMap<>();
}

// ✅ GOOD: Instance-level or bounded cache
public class DataCache {
    private final LoadingCache<String, Object> cache = CacheBuilder.newBuilder()
            .maximumSize(10000)
            .build(...);
}
```

### 3.2 Anonymous Inner Classes

```java
// ❌ BAD: Holds implicit reference to outer class
public class Outer {
    public void register() {
        Timer timer = new Timer();
        timer.schedule(new TimerTask() {  // Holds reference to Outer
            public void run() { /* uses Outer.this */ }
        }, 1000);
    }
}

// ✅ GOOD: Use static nested class or explicit reference
public class Outer {
    public void register() {
        final Outer outer = this;
        Timer timer = new Timer();
        timer.schedule(new TimerTask() {
            public void run() {
                outer.method();  // Explicit weak or bounded reference
            }
        }, 1000);
    }
}
```

### 3.3 Cached Objects

```java
// ❌ BAD: Caches without bounds
public class Cache {
    private Map<String, BigObject> cache = new HashMap<>();

    public void put(String key, BigObject obj) {
        cache.put(key, obj);  // Never evicted
    }
}

// ✅ GOOD: Bounded cache with eviction
public class Cache {
    private final Cache<String, BigObject> cache = Caffeine.newBuilder()
            .maximumSize(10000)
            .expireAfterAccess(1, TimeUnit.HOURS)
            .build();
}
```

## 4. Detection Tools

### Static Analysis

- **SpotBugs**: Detects unclosed resources, possible memory leaks
- **FindBugs**: Similar to SpotBugs, complementary rules
- **SonarQube**: Code quality including resource leaks
- **PMD**: Detects common coding issues

### Runtime Profiling

- **VisualVM**: Built into JDK, can detect memory leaks
- **JProfiler**: Commercial tool, excellent leak detection
- **YourKit**: Commercial tool, heap analysis
- **MAT (Memory Analyzer Tool)**: Eclipse plugin, deep analysis

### Heap Dump Analysis

```bash
# Generate heap dump
jmap -dump:format=b,file=heap.hprof <pid>

# Analyze with MAT
# Look for:
# 1. Dominator tree - which objects hold most memory
# 2. Histogram - object counts
# 3. Duplicates - similar objects with many instances
```

## 5. Quick Scan Patterns

Grep for these patterns to find potential leaks:

```bash
# Unclosed InputStream
grep -n "InputStream.*=" *.java | grep -v "try ("

# Unclosed FileOutputStream
grep -n "FileOutputStream.*=" *.java | grep -v "try ("

# Unclosed Connection
grep -n "Connection.*=" *.java | grep -v "try ("

# Static collections
grep -n "static.*Map\|static.*List\|static.*Set" *.java

# Unclosed ThreadLocal
grep -n "ThreadLocal" *.java | grep -v "remove()"
```

## Review Checklist for Each Change

For each code change, verify:

- [ ] All `AutoCloseable` resources use try-with-resources
- [ ] All `finally` blocks properly release resources
- [ ] All exception paths close resources
- [ ] All static collections have bounds or eviction
- [ ] All ThreadLocal values are removed
- [ ] All listener lists have removal methods
- [ ] All thread pools have shutdown hooks
- [ ] No anonymous inner classes holding references to outer class
- [ ] No unbounded caches
- [ ] Large objects not created in loops
