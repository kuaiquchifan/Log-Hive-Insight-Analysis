from pyhive import hive

def analyze_logs():
    # Execute Data Analysis Query
    conn = hive.Connection(host='localhost', port=10000)
    cursor = conn.cursor()
    
    # Data Query Content
    queries = {
        "Total number of users": "SELECT COUNT(DISTINCT user_id) FROM app_logs",
        "Event Type Distribution": "SELECT event_type, COUNT(*) FROM app_logs GROUP BY event_type",
        "Popular Pages": "SELECT attributes.page_id, COUNT(*) FROM app_logs WHERE attributes.page_id IS NOT NULL GROUP BY attributes.page_id LIMIT 10"
    }
    
    for name, sql in queries.items():
        print(f"\n{name}:")
        cursor.execute(sql)
        for row in cursor.fetchall():
            print(row)
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    analyze_logs()