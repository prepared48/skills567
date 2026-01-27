# 日志设计最佳实践

## 日志级别规范

### ERROR
- **使用场景**：系统错误、不可恢复的异常、数据不一致
- **示例**：
  - 数据库连接失败
  - 外部服务调用超时且重试失败
  - 关键业务逻辑异常导致流程中断
  - 数据校验失败导致数据不一致

### WARN
- **使用场景**：异常但可恢复、降级、重试、潜在问题
- **示例**：
  - 外部服务调用失败但有降级方案
  - 缓存失效回源数据库
  - 配置项缺失使用默认值
  - 资源使用率接近阈值

### INFO
- **使用场景**：关键业务节点、外部调用、重要状态变更
- **示例**：
  - 接口请求入口和出口
  - 订单状态变更
  - 用户登录/登出
  - 定时任务执行
  - RPC/HTTP调用

### DEBUG
- **使用场景**：详细的调试信息、中间变量、详细流程
- **注意**：生产环境应关闭DEBUG日志

## 日志内容规范

### 必须包含的信息
1. **时间戳**：精确到毫秒
2. **日志级别**：ERROR/WARN/INFO/DEBUG
3. **线程信息**：线程名或线程ID
4. **类名和方法名**：便于定位代码位置
5. **业务标识**：
   - 请求ID（traceId）：用于链路追踪
   - 用户ID（userId）：用于用户行为分析
   - 订单ID/业务ID：用于业务问题排查

### 日志格式示例

```
2026-01-19 10:30:45.123 [http-nio-8080-exec-1] INFO  c.q.u.q.c.MemberController - [traceId=abc123][userId=12345] 查询会员权益开始, request={level=GOLD, type=DISCOUNT}
2026-01-19 10:30:45.234 [http-nio-8080-exec-1] INFO  c.q.u.q.s.MemberService - [traceId=abc123][userId=12345] 调用权益计算服务, params={...}
2026-01-19 10:30:45.456 [http-nio-8080-exec-1] INFO  c.q.u.q.c.MemberController - [traceId=abc123][userId=12345] 查询会员权益完成, response={...}, cost=333ms
```

## 日志埋点位置

### 1. 接口入口和出口
```java
@RestController
public class MemberController {

    @GetMapping("/member/privilege")
    public Response getPrivilege(Request request) {
        log.info("[traceId={}][userId={}] 查询会员权益开始, request={}",
            traceId, userId, request);

        try {
            Response response = memberService.getPrivilege(request);
            log.info("[traceId={}][userId={}] 查询会员权益完成, response={}, cost={}ms",
                traceId, userId, response, cost);
            return response;
        } catch (Exception e) {
            log.error("[traceId={}][userId={}] 查询会员权益失败, request={}",
                traceId, userId, request, e);
            throw e;
        }
    }
}
```

### 2. 外部服务调用
```java
public class ExternalServiceClient {

    public Result callExternalService(Request request) {
        log.info("[traceId={}] 调用外部服务开始, service=, request={}",
            traceId, serviceName, request);

        long startTime = System.currentTimeMillis();
        try {
            Result result = doCall(request);
            long cost = System.currentTimeMillis() - startTime;
            log.info("[traceId={}] 调用外部服务成功, service={}, cost={}ms, result={}",
                traceId, serviceName, cost, result);
            return result;
        } catch (Exception e) {
            long cost = System.currentTimeMillis() - startTime;
            log.error("[traceId={}] 调用外部服务失败, service={}, cost={}ms, request={}",
                traceId, serviceName, cost, request, e);
            throw e;
        }
    }
}
```

### 3. 数据库操作
```java
public class MemberDao {

    public Member queryById(Long id) {
        log.info("[traceId={}] 查询会员信息, id={}", traceId, id);

        try {
            Member member = sqlSession.selectOne("queryById", id);
            log.info("[traceId={}] 查询会员信息成功, id={}, member={}",
                traceId, id, member);
            return member;
        } catch (Exception e) {
            log.error("[traceId={}] 查询会员信息失败, id={}", traceId, id, e);
            throw e;
        }
    }
}
```

### 4. 关键业务逻辑
```java
public class OrderService {

    public void processOrder(Order order) {
        log.info("[traceId={}][orderId={}] 订单处理开始, order={}",
            traceId, order.getId(), order);

        // 库存检查
        log.info("[traceId={}][orderId={}] 检查库存", traceId, order.getId());
        checkInventory(order);

        // 扣减库存
        log.info("[traceId={}][orderId={}] 扣减库存", traceId, order.getId());
        deductInventory(order);

        // 创建订单
        log.info("[traceId={}][orderId={}] 创建订单", traceId, order.getId());
        createOrder(order);

        // 发送消息
        log.info("[traceId={}][orderId={}] 发送订单消息", traceId, order.getId());
        sendMessage(order);

        log.info("[traceId={}][orderId={}] 订单处理完成", traceId, order.getId());
    }
}
```

### 5. 异常处理
```java
try {
    // 业务逻辑
} catch (BusinessException e) {
    // 业务异常：记录WARN级别，包含业务上下文
    log.warn("[traceId={}][userId={}] 业务异常, errorCode={}, message={}, context={}",
        traceId, userId, e.getErrorCode(), e.getMessage(), context);
    throw e;
} catch (Exception e) {
    // 系统异常：记录ERROR级别，包含完整堆栈
    log.error("[traceId={}][userId={}] 系统异常, context={}",
        traceId, userId, context, e);
    throw e;
}
```

## 日志性能优化

### 1. 避免字符串拼接
```java
// 错误：每次都会拼接字符串
log.debug("User " + userId + " request " + request);

// 正确：使用占位符，只有日志级别开启时才会格式化
log.debug("User {} request {}", userId, request);
```

### 2. 大对象日志
```java
// 错误：直接打印大对象，可能导致OOM
log.info("Response: {}", largeResponse);

// 正确：只打印关键字段
log.info("Response: id={}, status={}, size={}",
    largeResponse.getId(), largeResponse.getStatus(), largeResponse.getSize());
```

### 3. 日志采样
```java
// 高频日志采样：每100次打印一次
if (counter.incrementAndGet() % 100 == 0) {
    log.info("High frequency log: {}", data);
}
```

### 4. 异步日志
```xml
<!-- logback.xml -->
<appender name="ASYNC" class="ch.qos.logback.classic.AsyncAppender">
    <queueSize>512</queueSize>
    <discardingThreshold>0</discardingThreshold>
    <appender-ref ref="FILE" />
</appender>
```

## 敏感信息脱敏

### 需要脱敏的信息
- 用户密码
- 手机号
- 身份证号
- 银行卡号
- 地址信息
- Token/密钥

### 脱敏示例
```java
public class SensitiveDataUtil {

    // 手机号脱敏：138****5678
    public static String maskPhone(String phone) {
        if (phone == null || phone.length() != 11) {
            return phone;
        }
        return phone.substring(0, 3) + "****" + phone.substring(7);
    }

    // 身份证脱敏：110101********1234
    public static String maskIdCard(String idCard) {
        if (idCard == null || idCard.length() < 8) {
            return idCard;
        }
        return idCard.substring(0, 6) + "********" + idCard.substring(idCard.length() - 4);
    }
}

// 使用
log.info("User login: phone={}", SensitiveDataUtil.maskPhone(phone));
```

## 日志存储和查询

### 日志文件分割
```xml
<!-- logback.xml -->
<appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
    <file>logs/app.log</file>
    <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
        <!-- 按天分割 -->
        <fileNamePattern>logs/app.%d{yyyy-MM-dd}.log</fileNamePattern>
        <!-- 保留30天 -->
        <maxHistory>30</maxHistory>
    </rollingPolicy>
</appender>
```

### 日志查询建议
- 使用ELK（Elasticsearch + Logstash + Kibana）进行日志收集和查询
- 使用traceId进行全链路日志查询
- 建立日志索引：时间、用户ID、订单ID、错误码等
- 定期清理过期日志，避免磁盘占满

## 常见问题

### 1. 日志过多导致磁盘占满
- 合理设置日志级别（生产环境使用INFO）
- 配置日志文件大小和保留天数
- 高频日志使用采样
- 定期清理过期日志

### 2. 日志影响性能
- 使用异步日志
- 避免在循环中打印日志
- 大对象只打印关键字段
- 使用占位符而非字符串拼接

### 3. 日志难以排查问题
- 添加traceId进行链路追踪
- 记录完整的业务上下文
- 异常日志包含完整堆栈
- 关键节点都要有日志
