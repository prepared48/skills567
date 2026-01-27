import happybase
import sys
import socket
import time
import struct

def check_port(host, port, timeout=3):
    """检查端口是否开放"""
    print(f"Checking connectivity to {host}:{port}...", end=' ', flush=True)
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        print("OK")
        return True
    except socket.error as e:
        print(f"Failed: {e}")
        return False

def query_hbase(host, table_name, uid, timeout=10000):
    """
    使用 HappyBase (Thrift) 查询 HBase
    注意：需要 HBase 开启 Thrift Server
    """
    # 1. 基础网络检查
    if not check_port(host, 9090):
        print("Error: Cannot connect to HBase Thrift Server port (9090).")
        print("Please check if the Thrift Server is running on the target host and the firewall allows access.")
        return

    connection = None
    try:
        print(f"Initializing HappyBase connection to {host}:9090 (timeout={timeout}ms)...", flush=True)
        connection = happybase.Connection(host, port=9090, timeout=timeout, autoconnect=False)
        
        print("Opening connection...", flush=True)
        connection.open()
        print("Connection established.", flush=True)

        # 2. 验证连接并检查表是否存在
        print("Listing tables to verify connection...", flush=True)
        tables = connection.tables()
        # print(f"Available tables: {[t.decode('utf-8') for t in tables]}", flush=True)
        
        if table_name.encode() not in tables:
            print(f"Error: Table '{table_name}' not found in HBase.", flush=True)
            return

        table = connection.table(table_name)

        # 3. 构建 RowKey 前缀
        # 根据 Java 代码逻辑：Bytes.setInt(startRow, uid, 0)
        # RowKey 是 4字节的 Big-Endian 整数
        try:
            uid_int = int(uid)
            row_prefix = struct.pack('>I', uid_int)
            print(f"Searching in table '{table_name}' for UID '{uid}' (Binary RowKey: {row_prefix.hex()})...", flush=True)
        except ValueError:
            print(f"Warning: UID '{uid}' is not an integer. Falling back to string prefix.", flush=True)
            row_prefix = uid.encode()

        # 策略 1: Prefix Scan
        print("Strategy 1: Scanning with RowKey prefix...", flush=True)
        count = 0
        start_time = time.time()
        
        scanner = table.scan(row_prefix=row_prefix)
        
        try:
            for key, data in scanner:
                # 解析 RowKey
                try:
                    # 尝试解析前4字节为 UID，后4字节为时间戳
                    if len(key) >= 8:
                        r_uid = struct.unpack('>I', key[0:4])[0]
                        r_time = struct.unpack('>I', key[4:8])[0]
                        key_display = f"UID={r_uid}, TimeBucket={r_time} (Hex: {key.hex()})"
                    else:
                        key_display = key.hex()
                except:
                    key_display = key.hex()

                print(f"\nFound RowKey: {key_display}", flush=True)
                for col, val in data.items():
                    # 尝试解码 value，如果失败则显示 hex
                    try:
                        val_display = val.decode('utf-8')
                    except:
                        val_display = f"Hex:{val.hex()}"
                    print(f"  {col.decode('utf-8', 'ignore')}: {val_display}", flush=True)
                count += 1
                if count % 10 == 0:
                    print(f"Found {count} records so far...", flush=True)
        except Exception as e:
            print(f"\nError during scan: {e}", flush=True)
            print("Tip: If you see TTransportException, try editing the script to use 'transport=\"framed\"' in happybase.Connection")

        duration = time.time() - start_time
        print(f"\nTotal records found with prefix scan: {count} (Time: {duration:.2f}s)", flush=True)

    except Exception as e:
        print(f"\nCritical Error: {e}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        if connection:
            try:
                connection.close()
                print("Connection closed.", flush=True)
            except:
                pass


if __name__ == "__main__":
    # 配置信息
    # 用户提供的 path: /hbase/pf_common 通常用于 Zookeeper 连接 (Java/Native client)
    # HappyBase 使用 Thrift，需要指定 Thrift Server 的 IP
    HBASE_THRIFT_HOST = 'localhost' # 请替换为实际的 Thrift Server IP
    TABLE_NAME = 'hydra_contact_log_copy'
    TARGET_UID = '139635618'

    if len(sys.argv) > 1:
        HBASE_THRIFT_HOST = sys.argv[1]
    
    # 允许通过第二个参数指定表名
    if len(sys.argv) > 2:
        TABLE_NAME = sys.argv[2]
        
    # 允许通过第三个参数指定 UID
    if len(sys.argv) > 3:
        TARGET_UID = sys.argv[3]
    
    query_hbase(HBASE_THRIFT_HOST, TABLE_NAME, TARGET_UID)
