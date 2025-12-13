import subprocess
import os
from generate_logs import generate_logs

def load_logs_to_hive(log_file, date_str):
    # Upload local log files to HDFS and load them into Hive
    
    # Check if the file exists; if not, create it.
    if not os.path.exists(log_file):
        print(f"Log file {log_file} not found. Generating...")
        generate_logs(date_str)
    
    # Solution 1: Directly use LOAD DATA LOCAL (load from local)
    print(f"Loading data from local file: {log_file}")
    load_sql = f"LOAD DATA LOCAL INPATH '{os.path.abspath(log_file)}' INTO TABLE app_logs PARTITION (dt='{date_str}')"
    
    subprocess.run(f'hive -e "{load_sql}"', shell=True, check=True)
    print(f"✓ Data loaded successfully from {log_file}")

if __name__ == "__main__":
    from datetime import datetime, timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    log_file = f"app_logs_{yesterday}.log"
    load_logs_to_hive(log_file, yesterday)