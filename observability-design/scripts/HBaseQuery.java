import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.util.Bytes;

import java.io.IOException;

public class HBaseQuery {

    // 请替换为实际的 Zookeeper 地址列表，例如 "10.0.0.1,10.0.0.2,10.0.0.3"
    private static final String ZK_QUORUM = "your-zk-host1,your-zk-host2"; 
    
    // 用户提供的 path
    private static final String ZK_PARENT = "/hbase/pf_common"; 
    private static final String TABLE_NAME = "hydra_contact_log_copy";
    private static final String TARGET_UID = "139635618";

    public static void main(String[] args) {
        Configuration config = HBaseConfiguration.create();
        config.set("hbase.zookeeper.quorum", ZK_QUORUM);
        config.set("zookeeper.znode.parent", ZK_PARENT);

        try (Connection connection = ConnectionFactory.createConnection(config)) {
            Table table = connection.getTable(TableName.valueOf(TABLE_NAME));
            
            System.out.println("Querying table: " + TABLE_NAME);
            
            // 假设 RowKey 以 UID 开头 (Prefix Scan)
            // 如果 UID 只是 RowKey 的一部分而不是前缀，或者存储在列值中，需要修改查询策略
            Scan scan = new Scan();
            scan.setRowPrefixFilter(Bytes.toBytes(TARGET_UID));
            
            try (ResultScanner scanner = table.getScanner(scan)) {
                int count = 0;
                for (Result result : scanner) {
                    System.out.println("Found RowKey: " + Bytes.toString(result.getRow()));
                    // 遍历并打印所有列
                    result.listCells().forEach(cell -> {
                        String family = Bytes.toString(cell.getFamilyArray(), cell.getFamilyOffset(), cell.getFamilyLength());
                        String qualifier = Bytes.toString(cell.getQualifierArray(), cell.getQualifierOffset(), cell.getQualifierLength());
                        String value = Bytes.toString(cell.getValueArray(), cell.getValueOffset(), cell.getValueLength());
                        System.out.println("  " + family + ":" + qualifier + " = " + value);
                    });
                    System.out.println("----------------------------------------");
                    count++;
                }
                System.out.println("Total records found: " + count);
            }
            
        } catch (IOException e) {
            e.printStackTrace();
            System.err.println("Failed to connect to HBase. Please check your Zookeeper configuration.");
        }
    }
}
