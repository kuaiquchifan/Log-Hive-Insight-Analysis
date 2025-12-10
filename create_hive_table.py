from sqlalchemy import create_engine, text

def create_logs_table():
    # Create a Hive table to store log data
    engine = create_engine('hive://localhost:10000/default')
    
    # Modified to JSON format table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS app_logs (
        user_id STRING,
        event_time STRING,
        event_type STRING,
        attributes STRUCT<page_id:STRING, product_id:STRING>
    )
    PARTITIONED BY (dt STRING)
    ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
    STORED AS TEXTFILE
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        print("Table created successfully")

if __name__ == "__main__":
    create_logs_table()