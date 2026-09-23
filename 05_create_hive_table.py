from pyhive import hive


def execute_sql(cursor, sql):
    """执行一条 Hive SQL"""
    sql = sql.strip()
    if not sql:
        return

    print(f"\nExecuting:\n{sql}")
    cursor.execute(sql)
    print("✓ Done")


def main():
    # 连接 HiveServer2
    conn = hive.Connection(
        host="<your-vm-ip>",
        port=10000,
        username="your-vm-username",
        database="default"
    )

    cursor = conn.cursor()

    try:
        # ==========================================================
        # 1. 创建数据库
        # ==========================================================

        execute_sql(
            cursor,
            """
            CREATE DATABASE IF NOT EXISTS todo_analytics
            """
        )

        # 切换数据库
        execute_sql(
            cursor,
            """
            USE todo_analytics
            """
        )
        # 删除旧数据表
        for sql in [
            "DROP TABLE IF EXISTS dim_user",
            "DROP TABLE IF EXISTS dim_date",
            "DROP TABLE IF EXISTS dim_task",
            "DROP TABLE IF EXISTS ods_todo_event_log",
        ]:
            execute_sql(cursor, sql)

        # ==========================================================
        # 2. 用户维度
        # ==========================================================

        execute_sql(
            cursor,
            """
            CREATE EXTERNAL TABLE IF NOT EXISTS dim_user (
                user_id STRING,
                register_time STRING,
                user_group STRING,
                user_level STRING,
                user_type STRING,
                gender STRING,
                age_group STRING,
                province STRING,
                city STRING,
                is_active BOOLEAN,
                register_channel STRING
            )
            STORED AS PARQUET
            LOCATION '/user/hive/todo_analytics/raw/dim_user'
            """

        )

        # ==========================================================
        # 3. 日期维度
        # ==========================================================

        execute_sql(
            cursor,
            """
            CREATE EXTERNAL TABLE IF NOT EXISTS dim_date (
                date_key STRING,
                date_str STRING,
                year INT,
                month INT,
                day INT,
                week_of_year INT,
                day_of_week INT,
                is_weekend INT,
                is_holiday INT
            )
            STORED AS PARQUET
            LOCATION '/user/hive/todo_analytics/raw/dim_date'
            """
        )

        # ==========================================================
        # 4. 任务维度
        # ==========================================================

        execute_sql(
            cursor,
            """
            CREATE EXTERNAL TABLE IF NOT EXISTS dim_task (
                task_id STRING,
                user_id STRING,
                list_id STRING,
                task_title STRING,
                priority STRING,
                due_date STRING,
                create_time STRING,
                complete_time STRING,
                is_completed BOOLEAN,
                has_subtask BOOLEAN,
                has_reminder BOOLEAN,
                task_status STRING
            )
            STORED AS PARQUET
            LOCATION '/user/hive/todo_analytics/raw/dim_task'
            """
        )

        # ==========================================================
        # 5. Todo 事件日志
        # ==========================================================

        execute_sql(
            cursor,
            """
            CREATE EXTERNAL TABLE IF NOT EXISTS ods_todo_event_log (
                log_id STRING,
                user_id STRING,
                session_id STRING,
                event_time STRING,
                event_type STRING,
                task_id STRING,
                list_id STRING,
                attributes STRING,
                device_type STRING,
                os STRING,
                app_version STRING,
                network_type STRING
            )
            PARTITIONED BY (
                event_date STRING
            )
            STORED AS PARQUET
            LOCATION '/user/hive/todo_analytics/raw/ods_todo_event_log'
            """
        )

        # ==========================================================
        # 6. 自动发现 event_date 分区
        # ==========================================================

        execute_sql(
            cursor,
            """
            MSCK REPAIR TABLE ods_todo_event_log
            """
        )

        # ==========================================================
        # 7. 查看表
        # ==========================================================

        cursor.execute("SHOW TABLES")

        print("\n========== TABLES ==========")

        for row in cursor.fetchall():
            print(row[0])

        # ==========================================================
        # 8. 查看 partitions
        # ==========================================================

        cursor.execute(
            "SHOW PARTITIONS ods_todo_event_log"
        )

        print("\n========== PARTITIONS ==========")

        partitions = cursor.fetchall()

        for row in partitions:
            print(row[0])

        print("\n✓ Hive tables created successfully.")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()