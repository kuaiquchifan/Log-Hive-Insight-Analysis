[![English](https://img.shields.io/badge/README-English-2ea44f?style=for-the-badge)](README.md)
[![中文](https://img.shields.io/badge/README-中文-ffb703?style=for-the-badge)](README_zh.md)

# TodoList App Usage Analysis Project

## Project Goals and Theme

This project focuses on user behavior analysis for a TodoList app. It simulates user, date, task and event-log data to create a complete event-stream dataset, builds an analytics data warehouse using Apache Hive + Hadoop, and supports product operations, user growth, and feature optimization.

## Key Business Questions

- User scale and activity: analyze total users, activity levels, and new vs. returning user composition.
- User profile and distribution: analyze user acquisition channels and geographic distribution.
- Task behavior analysis: analyze core actions such as task creation, completion, deletion, postponement, and features like priority, reminders, subtasks, and due dates.
- Feature usage analysis: count usage frequency and distribution of app features to identify major feature usage.
- Time and behavior trends: analyze how user actions change across dates and time-of-day, and examine behavioral chains between events.
- Business insights: extract actionable insights for operations, growth, and product optimization.

Project Focus and Features
Project contents:

```bash
Log-Hive-Insight-Analysis-v2/
├── 01_create_user_raw_data.ipynb                     # generate synthetic dim_user data
├── 02_create_date_raw_data.ipynb                     # generate dim_date data
├── 03_create_task_raw_data_v4.ipynb                  # generate dim_task and ods_todo_event_log data
├── 04_validate_all_raw_data.ipynb                    #  validate generated raw data
├── 05_create_hive_table.py                           # create Hive tables and load data on an Ubuntu VM
├── 06_validate_hive_table_data.py                    # validate Hive table data on the VM
├── 07_clean_and_aggregate_data.ipynb                 # clean, join and aggregate Hive parquet outputs into DWD-level tables
├── 08_aggregate_further_data.ipynb                   # deeper aggregations into DWS-level summary tables
├── 09_active_users_dashboard.py                      # active users dashboard visualization
├── 09_data_visualisation_v3.py                       # Dash app entry script for the visualization dashboard
├── 09_in-depth_analysis_of_feature_usage.py          # feature usage deep-dive visualizations
├── 09_task_completion_lifecycle_analysis_data_vis.py # task lifecycle visualization
├── 10_validate_aggregate_data.ipynb                  # validate DWD outputs
├── 11_validate_aggregate_further_data.ipynb          # validate DWS outputs
├── 12_parquet_convert_into_csv.ipynb                 # batch convert project Parquet files to CSV
├── requirements.txt 								                  # dependency list
└── README.md										                      # documentation
```

## Data Scale
- Users: 10,000
- Timeline: 2026-07-01 to 2026-08-29 (60 days)
- Tasks: 180,000
- Task events: 600,000

**Note**: The whole dataset is sourced from a Python simulation script.

## Data Objects
Core data in the project:
- dim_user
- dim_date
- dim_task
- ods_todo_event_log

## Directory Details


Brief descriptions of main files:

- 01_create_user_raw_data.ipynb
    - Generates the user dimension table dim_user.
    - Fields include registration time (new/old user), gender, province/city, user tier (free/standard/vip), user type (low/normal/high), age group, active flag, registration channel, etc. Outputs parquet.

- 02_create_date_raw_data.ipynb
    - Generates dim_date covering 2026-07-01 to 2026-08-29 
    - Fields include date string, year, month, day, week, weekday, is_weekend, holiday flags. Outputs parquet.

- 03_create_task_raw_data_v4.ipynb
    - Generates dim_task and raw event log ods_todo_event_log.
    - Reads user data and simulates many task creations, completions, deletions, etc., producing event logs for lifecycle and behavioral analysis.

- 04_validate_all_raw_data.ipynb
    - Validates raw data quality: 
    - include completeness, types, time ranges, duplicates, and reasonableness.

- 05_create_hive_table.py
    - Uses PyHive to create Hive tables and load data into Hive/HiveServer2 on an Ubuntu VM, including HDFS paths.
    - Runs MSCK REPAIR TABLE to discover/load partitions.

- 06_validate_hive_table_data.py
    - Uses PyHive to verify the Hive tables exist and contain data; 
    - validates row counts and schema.

- 07_clean_and_aggregate_data.ipynb
    - Reads parquet outputs exported from Hive on the VM.
    - Uses DuckDB to create a base view v_todo_event_raw, joins events with user and task dimensions, extracts key fields, timestamps, device attributes and parameters; cleans data into v_todo_event_raw_clean.
    Produces three core intermediate tables: dwd_todo_event_detail (event detail fact), dwd_task_lifecycle (task lifecycle detail), and dwd_user_active_detail (user active detail).

- 08_aggregate_further_data.ipynb
    - Builds higher-level summary tables from the DWD outputs, producing nine DWS-level aggregated tables 
    - such as:
    dws_user_active_1d (daily active users)
    dws_user_behavior_summary
    dws_task_summary_1d
    dws_event_type_summary_1d
    dws_hour_active_summary
    dws_channel_region_summary
    dws_new_old_user_summary
    dws_user_retain_summary
    dws_user_feature_usage_summary

- 09_active_users_dashboard.py
    - Visualization module for the active users dashboard.
    - Reads parquet file from output_aggregate_further_data and output_data, computes DAU/WAU/MAU, trends, new vs returning ratios, active frequency, retention, and channel distribution. Uses Plotly and Dash to build interactive KPIs and charts.

- 09_data_visualisation_v3.py
    - Dashboard main entry script that composes multiple analysis modules into a Dash web app and switches between pages.
    - Dynamically loads modules: user activity overview, task lifecycle analysis, and feature usage deep-dive. 
    - Uses Dash + Bootstrap for layout.


- 09_in-depth_analysis_of_feature_usage.py
    - Visual module analyzing feature penetration (reminders, subtasks, due dates) and their impact on completion rates across user segments.
    - Reads feature usage summary, task lifecycle, and user dimension tables; computes usage rates, trend charts, and completion rate comparisons between tasks with/without features, segmented by user groups.

- 09_task_completion_lifecycle_analysis_data_vis.py
    - Visual module for task completion and lifecycle analysis.
    - Reads daily task summaries, lifecycle detail, event detail, and event-type summaries to compute KPIs: total created, total completed, overdue counts, average completion rate, average completion time, and plots trend charts, priority breakdowns, completion time distributions, and lifecycle funnel charts.

- 10_validate_aggregate_data.ipynb
    - Validates the DWD-level output files in output_aggregate_data:
    00_v_todo_event_raw_clean.parquet
    01_dwd_todo_event_detail.parquet
    02_dwd_task_lifecycle.parquet
    03_dwd_user_active_detail.parquet

- 11_validate_aggregate_further_data.ipynb
    - Validates the nine higher-level DWS output tables in output_aggregate_further_data.

- 12_parquet_convert_into_csv.ipynb
    - Batch converts all project Parquet files to CSV for use in Excel, Tableau, Power BI, etc.

- output_data
    - Stores parquet intermediate data exported for Hive ingestion and analysis.

- reports/
    - Stores analysis reports and outputs.


---

## Runtime Environment
### Base requirements
- Python 3.11+
- pandas
- numpy
- Ubuntu 24 LTS (VM)
- Apache Hive 4.0.1
- Hadoop 3.3.6
- PostgreSQL 16（Hive Metastore）

### Key pip packages
  ```bash
  pandas==2.2.3
  pyarrow==25.0.0
  numpy==2.4.6
  plotly==6.3.1
  matplotlib==3.11.1
  seaborn==0.13.2
  PyHive==0.7.0
  dash==4.4.1
  duckdb==1.4.5
  Flask==3.1.3
  ```


### localhost setup steps
#### Clone the repo and open the folder:
```bash
git clone <repository-url>
cd Log-Hive-Insight-Analysis-v2\
```
#### Create and activate a conda env:
```bash
conda create -n <your-venv-name> python=3.11
conda activate <your-venv-name>
```

#### Install Python dependencies:
```bash
pip install -r requirement.txt
```

### Ubuntu VM setup steps
#### Install OpenJDK 8:
```bash
sudo apt install openjdk-8-jdk
```

Add environment vars in ~/.bashrc and source it:
```bash
nano ~/.bashrc
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=JAVA_HOME/bin:JAVAHOME/bin:PATH
source ~/.bashrc
```

#### Install Hadoop 3.3.6:
```bash
cd ~
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
tar -xzf hadoop-3.3.6.tar.gz
sudo mv ~/桌面/hadoop-3.3.6 /opt/
sudo chown -R USER:USER /opt/hadoop-3.3.6
```

Set and Activate Hadoop Environment Variables

```bash
nano ~/.bashrc
source ~/.bashrc
```

verify HDFS web UI at http://localhost:9870/.

#### Install Apache Hive 4.0.1:
```bash
cd ~
wget https://archive.apache.org/dist/hive/hive-4.0.1/apache-hive-4.0.1-bin.tar.gz
tar -xzf apache-hive-4.0.1-bin.tar.gz
sudo mv ~/桌面/apache-hive-4.0.1-bin /opt/
```

Set and Activate Apache Hive Environment Variables
```Shell
nano ~/.bashrc
source ~/.bashrc
```

#### Install PostgreSQL 16:
```bash
sudo apt install postgresql postgresql-contrib
```

#### Create Hive metastore database:
```bash
sudo -u postgres psql
CREATE DATABASE "hive";
```

#### Create hive user and grant privileges:
```bash
CREATE USER hive WITH PASSWORD 'hive';
GRANT ALL PRIVILEGES ON DATABASE hive TO hive;
GRANT USAGE, CREATE ON SCHEMA public TO hive;
ALTER DATABASE hive OWNER TO hive;
ALTER SCHEMA public OWNER TO hive;
\dn+
\du hive
```

#### Install PostgreSQL JDBC driver and copy into Hive lib:
```bash
sudo apt install libpostgresql-jdbc-java
sudo cp /usr/share/java/postgresql-42.7.2.jar $HIVE_HOME/lib/
```

## How to Use
### 1. Initialize data:
- Run in Jupyter:
    - 01_create_user_raw_data.ipynb
    - 02_create_date_raw_data.ipynb
    - 03_create_task_raw_data_v4.ipynb
    - Output: 10,000 users, 60-day timeline (2026-07-01 to 2026-08-29), 180k tasks, 600k task events.

### 2. Validate raw data:
- Run 04_validate_all_raw_data.ipynb

### 3. Create Hive tables on the VM:
- Run 05_create_hive_table.py

### 4. Start Hadoop on the VM:
Start HDFS：
```bash
start-dfs.sh
```

and then start YARN：
```bash
start-yarn.sh
```

### 5. Create HDFS directories:
```bash
hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -chmod g+w /user/hive/warehouse

hdfs dfs -mkdir -p /user/hive/todo_analytics/raw/
hdfs dfs -chmod g+w /user/hive/todo_analytics/raw/
```

### 6. Initialize Hive metastore schema:
```bash
$HIVE_HOME/bin/schematool \
  -dbType postgres \
  -initSchema \
  --verbose
```


### 7. Upload parquet files to HDFS

For example, if your local files are located in:

```bash
~/Desktop/output_data/
```
and then upload your local file to hdfs like below:
```bash
hdfs dfs -put ~/桌面/output_data/01_dim_user.parquet /user/hive/todo_analytics/raw/dim_user/
hdfs dfs -put ~/桌面/output_data/02_dim_date.parquet /user/hive/todo_analytics/raw/dim_date/
hdfs dfs -put ~/桌面/output_data/03_dim_task.parquet /user/hive/todo_analytics/raw/dim_task/
hdfs dfs -put ~/桌面/output_data/ods_todo_event_log /user/hive/todo_analytics/raw/
```

### 8. Start Apache Hive services:
Start Metastore:
```bash
$HIVE_HOME/bin/hive --service metastore
```
Start HiveServer2:
```bash
$HIVE_HOME/bin/hive --service hiveserver2
```
Check http://localhost:10002/.

### 9. Basic aggregation:
- Run 07_clean_and_aggregate_data.ipynb

### 10. Deeper aggregation:
- Run 08_aggregate_further_data.ipynb

### 11. Data Visualization:
- Run the Dash app from project root:
```bash
python 09_data_visualisation_v3.py
```

## License
This project is open-source under the **Apache 2.0** License.

## Author & Acknowledgements
Author: Junliang Li   
Email: 940747544@qq.com