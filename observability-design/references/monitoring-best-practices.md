# 监控设计最佳实践

## 监控指标分类

### 1. 业务指标（Business Metrics）
衡量业务健康度和KPI的指标

**常见业务指标：**
- **订单相关**：订单量、订单金额、订单转化率、取消率
- **用户相关**：活跃用户数、新增用户数、用户留存率
- **会员相关**：会员注册数、会员等级分布、权益使用率
- **交易相关**：支付成功率、退款率、客单价

**示例：**
```java
// 订单创建成功
QMonitor.recordOne("order.create.success");
QMonitor.recordOne("order.create.amount", order.getAmount());

// 会员权益使用
QMonitor.recordOne("privilege.use.count", Map.of(
    "level", member.getLevel(),
    "type", privilege.getType()
));
```

### 2. 性能指标（Performance Metrics）
衡量系统响应速度和吞吐量的指标

**常见性能指标：**
- **QPS（Queries Per Second）**：每秒请求数
- **响应时间（RT）**：接口响应时间
- **响应时间分位值**：P50、P90、P95、P99
- **并发数**：同时处理的请求数
- **吞吐量**：单位时间处理的数据量

**示例：**
```java
long startTime = System.currentTimeMillis();
try {
    Result result = service.process(request);
    long cost = System.currentTimeMillis() - startTime;

    // 记录接口耗时
    QMonitor.recordOne("api.process.cost", cost);

    // 记录QPS
    QMonitor.recordOne("api.process.qps");

    return result;
} catch (Exception e) {
    long cost = System.currentTimeMillis() - startTime;
    QMonitor.recordOne("api.process.cost", cost);
    throw e;
}
```

### 3. 错误指标（Error Metrics）
衡量系统稳定性和可靠性的指标

**常见错误指标：**
- **错误率**：失败请求占总请求的比例
- **异常次数**：各类异常的发生次数
- **超时次数**：请求超时的次数
- **降级次数**：服务降级的次数

**示例：**
```java
try {
    Result result = service.process(request);
    QMonitor.recordOne("api.process.success");
    return result;
} catch (TimeoutException e) {
    QMonitor.recordOne("api.process.timeout");
    throw e;
} catch (BusinessException e) {
    QMonitor.recordOne("api.process.business_error", Map.of(
        "errorCode", e.getErrorCode()
    ));
    throw e;
} catch (Exception e) {
    QMonitor.recordOne("api.process.system_error");
    throw e;
}
```

### 4. 资源指标（Resource Metrics）
衡量系统资源使用情况的指标

**常见资源指标：**
- **CPU使用率**：应用CPU占用百分比
- **内存使用率**：JVM堆内存使用情况
- **线程数**：活跃线程数、线程池队列长度
- **连接池**：数据库连接池、Redis连接池使用率
- **磁盘IO**：磁盘读写速率
- **网络IO**：网络流量

**示例：**
```java
// 线程池监控
ThreadPoolExecutor executor = ...;
QMonitor.recordOne("threadpool.active", executor.getActiveCount());
QMonitor.recordOne("threadpool.queue", executor.getQueue().size());
QMonitor.recordOne("threadpool.completed", executor.getCompletedTaskCount());

// 连接池监控
DataSource dataSource = ...;
QMonitor.recordOne("datasource.active", dataSource.getNumActive());
QMonitor.recordOne("datasource.idle", dataSource.getNumIdle());
```

### 5. 依赖指标（Dependency Metrics）
衡量外部依赖健康度的指标

**常见依赖指标：**
- **RPC调用成功率**：Dubbo服务调用成功率
- **HTTP调用成功率**：外部HTTP接口调用成功率
- **数据库查询耗时**：SQL执行时间
- **缓存命中率**：Redis缓存命中率
- **消息队列延迟**：QMQ消息消费延迟

**示例：**
```java
// Dubbo调用监控
try {
    long startTime = System.currentTimeMillis();
    Result result = dubboService.call(request);
    long cost = System.currentTimeMillis() - startTime;

    QMonitor.recordOne("dubbo.call.success", Map.of(
        "service", serviceName,
        "method", methodName
    ));
    QMonitor.recordOne("dubbo.call.cost", cost, Map.of(
        "service", serviceName
    ));

    return result;
} catch (Exception e) {
    QMonitor.recordOne("dubbo.call.fail", Map.of(
        "service", serviceName,
        "method", methodName
    ));
    throw e;
}

// 缓存命中率监控
String value = cache.get(key);
if (value != null) {
    QMonitor.recordOne("cache.hit");
} else {
    QMonitor.recordOne("cache.miss");
    value = loadFromDB(key);
    cache.put(key, value);
}
```

## 监控维度设计

### 1. 接口维度
按接口/方法维度统计指标

```java
QMonitor.recordOne("api.cost", cost, Map.of(
    "interface", "/member/privilege",
    "method", "GET"
));
```

### 2. 用户维度
按用户/租户维度统计指标

```java
QMonitor.recordOne("privilege.use", Map.of(
    "userId", userId,
    "level", memberLevel
));
```

### 3. 环境维度
按环境维度统计指标（生产/预发布）

```java
QMonitor.recordOne("order.create", Map.of(
    "env", environment  // prod, beta, test
));
```

### 4. 错误类型维度
按错误类型维度统计指标

```java
QMonitor.recordOne("api.error", Map.of(
    "errorType", e.getClass().getSimpleName(),
    "errorCode", errorCode
));
```

### 5. 业务属性维度
按业务属性维度统计指标

```java
QMonitor.recordOne("order.create", Map.of(
    "orderType", order.getType(),      // 订单类型
    "payMethod", order.getPayMethod(), // 支付方式
    "channel", order.getChannel()      // 渠道
));
```

## 监控埋点位置

### 1. Controller层
```java
@RestController
public class MemberController {

    @GetMapping("/member/privilege")
    public Response getPrivilege(Request request) {
        long startTime = System.currentTimeMillis();

        // 记录请求QPS
        QMonitor.recordOne("member.privilege.qps");

        try {
            Response response = memberService.getPrivilege(request);
            long cost = System.currentTimeMillis() - startTime;

            // 记录成功和耗时
            QMonitor.recordOne("member.privilege.success");
            QMonitor.recordOne("member.privilege.cost", cost);

            // 记录响应时间分位值
            if (cost > 1000) {
                QMonitor.recordOne("member.privilege.slow");
            }

            return response;
        } catch (Exception e) {
            long cost = System.currentTimeMillis() - startTime;

            // 记录失败和耗时
            QMonitor.recordOne("member.privilege.fail");
            QMonitor.recordOne("member.privilege.cost", cost);

            throw e;
        }
    }
}
```

### 2. Service层
```java
@Service
public class MemberService {

    public Privilege calculatePrivilege(Member member) {
        // 记录业务指标
        QMonitor.recordOne("privilege.calculate", Map.of(
            "level", member.getLevel(),
            "type", member.getType()
        ));

        Privilege privilege = doCalculate(member);

        // 记录权益金额
        QMonitor.recordOne("privilege.amount", privilege.getAmount());

        return privilege;
    }
}
```

### 3. DAO层
```java
@Repository
public class MemberDao {

    public Member queryById(Long id) {
        long startTime = System.currentTimeMillis();

        try {
            Member member = sqlSession.selectOne("queryById", id);
            long cost = System.currentTimeMillis() - startTime;

            // 记录数据库查询耗时
            QMonitor.recordOne("db.query.cost", cost, Map.of(
                "table", "member",
                "operation", "select"
            ));

            // 慢查询监控
            if (cost > 100) {
                QMonitor.recordOne("db.query.slow", Map.of(
                    "table", "member",
                    "cost", cost
                ));
            }

            return member;
        } catch (Exception e) {
            QMonitor.recordOne("db.query.fail", Map.of(
                "table", "member"
            ));
            throw e;
        }
    }
}
```

### 4. 外部调用
```java
public class ExternalServiceClient {

    public Result callService(Request request) {
        long startTime = System.currentTimeMillis();

        try {
            Result result = doCall(request);
            long cost = System.currentTimeMillis() - startTime;

            // 记录调用成功和耗时
            QMonitor.recordOne("external.call.success", Map.of(
                "service", serviceName
            ));
            QMonitor.recordOne("external.call.cost", cost, Map.of(
                "service", serviceName
            ));

            return result;
        } catch (TimeoutException e) {
            // 记录超时
            QMonitor.recordOne("external.call.timeout", Map.of(
                "service", serviceName
            ));
            throw e;
        } catch (Exception e) {
            // 记录失败
            QMonitor.recordOne("external.call.fail", Map.of(
                "service", serviceName
            ));
            throw e;
        }
    }
}
```

## 监控大盘设计

### 1. 核心业务大盘
- **订单量趋势**：实时订单量、同比/环比
- **订单金额趋势**：实时订单金额、同比/环比
- **转化率**：各环节转化率
- **用户活跃度**：DAU/MAU趋势

### 2. 接口性能大盘
- **QPS趋势**：各接口QPS实时监控
- **响应时间**：P50/P90/P99响应时间
- **错误率**：各接口错误率
- **慢接口Top10**：响应时间最长的接口

### 3. 系统资源大盘
- **CPU使用率**：应用CPU占用趋势
- **内存使用率**：JVM堆内存使用趋势
- **线程数**：活跃线程数趋势
- **GC情况**：GC次数和耗时

### 4. 依赖健康度大盘
- **数据库**：连接数、慢查询、错误率
- **缓存**：命中率、连接数、错误率
- **RPC**：调用成功率、耗时、超时率
- **消息队列**：消息堆积、消费延迟

## 监控性能优化

### 1. 减少监控埋点
```java
// 错误：每次循环都埋点
for (Item item : items) {
    process(item);
    QMonitor.recordOne("item.process");  // 高频埋点
}

// 正确：批量埋点
int count = 0;
for (Item item : items) {
    process(item);
    count++;
}
QMonitor.recordOne("item.process", count);
```

### 2. 异步上报
```java
// 使用异步方式上报监控数据
ExecutorService executor = Executors.newSingleThreadExecutor();
executor.submit(() -> {
    QMonitor.recordOne("heavy.metric", data);
});
```

### 3. 采样上报
```java
// 高频监控采样：每100次上报一次
if (counter.incrementAndGet() % 100 == 0) {
    QMonitor.recordOne("high.frequency.metric", data);
}
```

## 监控告警联动

监控指标应该与报警规则联动，当指标异常时及时触发报警。详见 [alerting-best-practices.md](alerting-best-practices.md)。

## 常见问题

### 1. 监控数据过多导致存储压力
- 合理设置监控维度，避免维度爆炸
- 高频监控使用采样
- 定期清理过期监控数据
- 使用时序数据库存储监控数据

### 2. 监控影响性能
- 使用异步上报
- 减少不必要的监控埋点
- 批量上报监控数据

### 3. 监控数据不准确
- 确保监控埋点位置正确
- 注意异常情况也要埋点
- 定期校验监控数据准确性
