import json
import random
from datetime import datetime, timedelta

def generate_logs(date_str, num_logs=1000):
    # Step 1: Prepare Simulated Data
    # Generate simulated log files for specified dates
    events = ['app_launch', 'view_page', 'add_to_cart', 'purchase']
    log_entries = []
    
    for _ in range(num_logs):
        log_entry = {
            "user_id": f"user_{random.randint(1, 100)}",
            "event_time": (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(seconds=random.randint(0, 86399))).isoformat(),
            "event_type": random.choice(events),
            "attributes": {
                "page_id": f"page_{random.randint(1, 20)}" if random.random() > 0.3 else None,
                "product_id": f"prod_{random.randint(1, 50)}" if random.random() > 0.5 else None
            }
        }
        log_entries.append(json.dumps(log_entry))


    # Assuming log files are stored in the HDFS directory `/user/hive/warehouse/logs/dt=<date>`
    # Here we first generate locally
    file_path = f"app_logs_{date_str}.log"
    with open(file_path, 'w') as f:
        f.write('\n'.join(log_entries))
    
    print(f"Generated log file: {file_path}")
    return file_path

if __name__ == "__main__":
    # Generate yesterday's log
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    generate_logs(yesterday)