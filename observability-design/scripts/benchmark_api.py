import argparse
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# 默认请求地址
DEFAULT_URL = "http://10.77.56.50:8080/test/single?start=2025-01-20%2000%3A00%3A00&end=2026-01-20%2000%3A00%3A00&uid=139635618&hbaseType=0"

def make_request(url, request_id):
    """发送单个请求并记录耗时"""
    start_time = time.time()
    status = "UNKNOWN"
    code = 0
    try:
        # 设置超时时间为 10 秒
        with urllib.request.urlopen(url, timeout=10) as response:
            code = response.getcode()
            # 读取响应内容确保请求完整结束
            response.read()
            if 200 <= code < 300:
                status = "SUCCESS"
            else:
                status = "FAILURE"
    except urllib.error.HTTPError as e:
        code = e.code
        status = "FAILURE"
    except Exception as e:
        status = f"ERROR: {str(e)}"
        code = -1
    
    duration = time.time() - start_time
    return status, code, duration

def run_benchmark(url, concurrency, total_requests):
    """运行压测"""
    print(f"Starting benchmark...")
    print(f"Target URL:     {url}")
    print(f"Concurrency:    {concurrency}")
    print(f"Total Requests: {total_requests}")
    print("-" * 60)

    success_count = 0
    failure_count = 0
    latencies = []
    lock = Lock()
    
    start_time = time.time()

    # 使用线程池并发执行
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(make_request, url, i) for i in range(total_requests)]
        
        for i, future in enumerate(futures):
            status, code, duration = future.result()
            with lock:
                if status == "SUCCESS":
                    success_count += 1
                else:
                    failure_count += 1
                    # 如果失败，打印第一个错误信息以便排查
                    if failure_count == 1:
                        print(f"\n[First Failure Info] Code: {code}, Status: {status}")

                latencies.append(duration)
                
            # 每完成 10% 打印一次进度
            if total_requests >= 10 and (i + 1) % (total_requests // 10) == 0:
                print(f"Progress: {i + 1}/{total_requests} requests completed...", end='\r')

    total_time = time.time() - start_time
    print("\n" + "-" * 60)
    
    # 计算统计指标
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    # QPS = 成功请求数 / 总耗时 (或者 总请求数 / 总耗时，通常压测看有效QPS)
    qps = success_count / total_time if total_time > 0 else 0

    print("Benchmark Results:")
    print(f"Total Time:     {total_time:.2f} s")
    print(f"Total Requests: {total_requests}")
    print(f"Successful:     {success_count}")
    print(f"Failed:         {failure_count}")
    print(f"QPS (Success):  {qps:.2f} req/s")
    print(f"Avg Latency:    {avg_latency*1000:.2f} ms")
    print(f"Min Latency:    {min_latency*1000:.2f} ms")
    print(f"Max Latency:    {max_latency*1000:.2f} ms")
    print("-" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="API Concurrent Benchmark Tool")
    
    # 定义命令行参数
    parser.add_argument("-c", "--concurrency", type=int, default=10, help="并发线程数 (默认: 10)")
    parser.add_argument("-n", "--number", type=int, default=100, help="总请求数 (默认: 100)")
    parser.add_argument("-u", "--url", type=str, default=DEFAULT_URL, help="目标 URL")
    
    args = parser.parse_args()
    
    run_benchmark(args.url, args.concurrency, args.number)
