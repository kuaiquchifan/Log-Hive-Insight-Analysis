from pyhive import hive

def execute_sql(cursor, sql):
    sql = sql.strip()
    if not sql:
        return

    print(f"\nExecuting:\n{sql}")
    cursor.execute(sql)

    # 如果是 SELECT 语句，取出结果并打印
    try:
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(row)
            print(f"Result rows: {len(rows)}")
    except Exception:
        pass

    print("✓ Done")


def main():
    # 连接 HiveServer2
    conn = hive.Connection(
        host="192.168.71.128",
        port=10000,
        username="lee",
        database="default"
    )

    cursor = conn.cursor()

    try:
        # ==========================================================
        # 1. 创建数据库
        # ==========================================================

        # 切换数据库
        execute_sql(
            cursor,
            """
            USE todo_analytics
            """
        )

        # ==========================================================
        # 2. 用户维度
        # ==========================================================

        execute_sql(
            cursor,
            """
            SELECT 'dim_user' AS table_name, COUNT(*) AS row_count
            FROM dim_user

            UNION ALL

            SELECT 'dim_date', COUNT(*)
            FROM dim_date

            UNION ALL

            SELECT 'dim_task', COUNT(*)
            FROM dim_task

            UNION ALL

            SELECT 'ods_todo_event_log', COUNT(*)
            FROM ods_todo_event_log
            """
        )


    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()