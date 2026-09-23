[![English](https://img.shields.io/badge/README-English-2ea44f?style=for-the-badge)](README.md)
[![中文](https://img.shields.io/badge/README-中文-ffb703?style=for-the-badge)](README_zh.md)

# TodoList App Usage Analysis Project

## 项目目标与主题

本项目围绕待办事项 Todolist App用户行为分析展开，通过模拟生成用户、日期、任务及操作日志数据，构建完整的事件流数据，并使用 Apache Hive + Hadoop 搭建分析数据仓库，为产品运营、用户增长和功能优化提供数据分析基础。

## 项目重点关注以下业务问题：

- 用户规模与活跃情况：分析用户总体规模、活跃程度以及新老用户结构。
- 用户画像与分布：分析用户来源渠道、地区分布等特征。
- 任务行为分析：分析任务创建、完成、删除、延期等核心行为，以及任务优先级、提醒、子任务和截止日期等功能的使用情况。
- 功能使用分析：统计 App 各类功能的使用频次和事件分布，识别用户主要使用的功能。
- 时间与行为趋势：分析用户操作在不同日期、时段的变化趋势，并进一步观察任务事件之间的行为链路。
- 业务洞察：基于维度分析挖掘用户使用习惯、任务完成情况和产品功能使用特征，为产品运营、增长分析和功能优化提供数据支持。

## 项目结构和功能特性

```bash
Log-Hive-Insight-Analysis-v2/
├── 01_create_user_raw_data.ipynb                     # 生成合成的用户维表数据
├── 02_create_date_raw_data.ipynb                     # 生成“日期维度表”的数据
├── 03_create_task_raw_data_v4.ipynb                  # 生成“任务维度表”和“待办事件日志表”的数据
├── 04_validate_all_raw_data.ipynb                    # 检查前面生成的原始数据是否正确、齐全、合理
├── 05_create_hive_table.py                           # 对Ubuntu虚拟机里面的PostgreSQL的hive表进行数据表创建和数据输入
├── 06_validate_hive_table_data.py                    # 对Ubuntu虚拟机里面的Hive数据验证是否已经落库且数量正确
├── 07_clean_and_aggregate_data.ipynb                 # 对来自Ubuntu虚拟机里面的apache hive的数据，把原始用户、日期、任务和事件数据进行“清洗 + 关联 + 聚合”，生成一系列便于分析的中间表（DWD 层）
├── 08_aggregate_further_data.ipynb                   # 这是在前面 DWD 层(07_clean_and_aggregate_data.ipynb的输出结果)基础上继续做“更深一层的汇总分析”，它把清洗后的事件数据和任务数据再加工成一批按用户、按日、按功能维度统计的指标表。
├── 09_active_users_dashboard.py                      # 这是展示“活跃用户仪表盘”可视化模块的脚本。
├── 09_data_visualisation_v3.py                       # 这是整个dash数据可视化看板的“的入口脚本”。
├── 09_in-depth_analysis_of_feature_usage.py          # 这是“功能使用深度分析”的可视化脚本。
├── 09_task_completion_lifecycle_analysis_data_vis.py # 这是“任务完成与生命周期分析”的可视化脚本，
├── 10_validate_aggregate_data.ipynb                  # 校验聚合后的中间表数据是否正确”
├── 11_validate_aggregate_further_data.ipynb          # 校验更高层聚合的结果是否正常”，
├── 12_parquet_convert_into_csv.ipynb                 # 把项目中生成所有的 Parquet 数据文件批量转换成 CSV 文件
├── requirements.txt 								                  # 环境依赖信息
└── README.md										                      # 解释文档
```

## 数据规模：
用户：10000名
时间线：2026-07-01 至 2026-08-29（60天）
任务：18 万个
任务行为事件：60 万个

**注意**：整个数据集都来源于python模拟脚本

## 数据分析对象

项目中的核心数据来源包括：

* 用户维度数据 `dim_user`
* 日期维度数据 `dim_date`
* 任务维度数据 `dim_task`
* 网络事件日志数据 `ods_todo_event_log`
---

## 目录详细说明

本项目主要文件说明如下：

- 01_create_user_raw_data.ipynb
  - 生成用户维度数据`dim_user`
  - 包括，生成“老用户/新用户”注册时间、性别、地区（省/市）、用户等级（free/standard/vip）、用户类型（low/normal/high）、年龄段、是否活跃、注册渠道等字段；输出并保存为parquet文件。

- 02_create_date_raw_data.ipynb
  - 生成日期维度数据`dim_date`
  - 生成 2026-07-01 至 2026-08-29 的时间维度，供分析使用，包括日期字符串、年份、月份、日、周数、星期几、是否周末、是否节假日等。输出并保存为parquet文件。

- 03_create_task_raw_data_v4.ipynb
  - 生成任务维度数据`dim_task`和事件日志`ods_todo_event_log`的原始数据
  - 它读取前面生成的用户数据，然后模拟大量的任务创建、完成、删除等行为，并且生成对应的事件日志，用于后续分析任务生命周期、用户活跃度、事件流转和运营指标。

- 04_validate_all_raw_data.ipynb
  - 验证各类原始数据质量
  - 检查字段完整性、数据类型、时间范围、重复值、合理性等

- 05_create_hive_table.py
  - 使用pyhive对Ubuntu虚拟机里面的PostgreSQL和Apache Hive/HiveServer2 的hive表进行数据表创建和数据输入，包括 dim_user、dim_date、dim_task 和 ods_todo_event_log。并且指定了HDFS路径。
  - 执行 MSCK REPAIR TABLE 来自动发现并加载分区信息

- 06_validate_hive_table_data.py
  - 使用pyhive对Ubuntu虚拟机里面的PostgreSQL和Apache Hive/HiveServer2 的hive表，校验是否已正确创建并包含数据
  - 验证主表行数和表结构

- 07_clean_and_aggregate_data.ipynb
  - 对来自Ubuntu虚拟机里面的apache hive的数据，保存为parquet文件。
  - 使用 DuckDB 直接读取 Parquet 文件，再建立一个基础视图 v_todo_event_raw，把事件日志与用户维度、任务维度做关联，然后提取出关键字段、时间字段、设备属性和动作参数；随后做了清理，生成 v_todo_event_raw_clean，再进一步输出三个核心中间表：dwd_todo_event_detail（事件明细事实表）、dwd_task_lifecycle（任务生命周期明细）、dwd_user_active_detail（用户活跃明细）。

- 08_aggregate_further_data.ipynb
  - 在前面 DWD 层基础上继续做“更深一层的汇总分析”，它把清洗后的事件数据和任务数据再加工成一批按用户、按日、按功能维度统计的指标表。具体来说，它生成了 9 张更细的汇总表。
  - 例如：
    - dws_user_active_1d（用户日活）、
    - dws_user_behavior_summary（用户行为汇总）、
    - dws_task_summary_1d（任务每日汇总）、
    - dws_event_type_summary_1d（事件类型每日汇总）、
    - dws_hour_active_summary（按小时活跃分布）、
    - dws_channel_region_summary（渠道+区域汇总）、
    - dws_new_old_user_summary（新老用户统计）、
    - dws_user_retain_summary（留存分析）、
    - dws_user_feature_usage_summary（功能渗透率）。

- 09_active_users_dashboard.py
  - 这个文件是一个“活跃用户仪表盘”的可视化模块脚本，主要用于从前面的汇总数据中读取日活、用户行为、留存和渠道分布等指标，然后把它们展示成图表和 KPI 卡片，帮助快速看懂用户活跃趋势和新老用户结构。
  - 它先读取 output_aggregate_further_data 和 output_data 下的 Parquet 文件，再计算 DAU/WAU/MAU、用户活跃趋势、新老用户占比、活跃用户频次、留存率和渠道分布等内容，并通过 Plotly 和 Dash 生成交互式页面，用于前端展示。

- 09_data_visualisation_v3.py
  - 这个文件是整个看板的“入口脚本”，它负责把多个分析模块整合到一个 Dash Web 页面里，并通过按钮切换不同的分析页面。
  - 它会动态加载三个模块：用户规模与活跃看板、任务完成与生命周期分析、功能使用深度分析
  - 然后用 Dash 和 Bootstrap 组装顶部导航和主内容区，默认打开用户活跃概览页面，点击不同按钮后切换到任务生命周期或功能使用分析页面。

- 09_in-depth_analysis_of_feature_usage.py
  - 这个文件是“功能使用深度分析”的可视化模块脚本，主要用于分析提醒、子任务和截止日期等功能的使用率，以及这些功能对任务完成率和不同用户分群的影响。
  - 它读取三类数据：功能使用汇总表、任务生命周期表和用户维度表，然后计算最近日期的提醒使用率、子任务使用率、截止日期设置率，并把这些指标做成趋势图；
  - 同时还比较“启用功能”和“未启用功能”两类任务的完成率差异，以及不同用户分群（如新老用户、等级分群等）的功能使用差异，最终以图表的形式展示出功能渗透和贡献效果。

- 09_task_completion_lifecycle_analysis_data_vis.py
  - 这个文件是“任务完成与生命周期分析”的可视化脚本，它主要对任务的整体完成情况、生命周期变化和优先级差异进行分析。
  - 它读取任务每日汇总表、任务生命周期明细表、事件明细表和事件类型汇总表，然后计算总创建数、总完成数、逾期数、平均完成率、平均完成时长等 KPI。
  - 并绘制任务创建/完成趋势图、整体完成率仪表盘、按优先级的任务统计图、完成时长分布图以及任务生命周期漏斗图，帮助看懂任务是如何从创建到完成、延期或删除的。

- 10_validate_aggregate_data.ipynb
  - 这个文件的作用是“校验聚合后的中间表数据是否正确”，它读取的是 output_aggregate_data 目录下四张关键结果表：00_v_todo_event_raw_clean.parquet、01_dwd_todo_event_detail.parquet、02_dwd_task_lifecycle.parquet 和 03_dwd_user_active_detail.parquet

- 11_validate_aggregate_further_data.ipynb
  - 这个文件的作用是“校验更高层汇总结果是否正常”，它会读取 output_aggregate_further_data 目录下的 9 张汇总表，包括用户日活、用户行为汇总、任务每日汇总、事件类型每日汇总、按小时活跃分布、渠道与区域汇总、新老用户统计、留存统计和功能使用率汇总，
- 12_parquet_convert_into_csv.ipynb
  - 这个文件的作用是把项目中生成所有的 Parquet 数据文件批量转换成 CSV 文件，方便后续在 Excel、Tableau、Power BI 或其他工具中直接查看和导入。
- output_data/
  - 存放 Parquet 等中间数据文件
  - 供后续 Hive 导入和分析使用
- reports/
  - 保存分析报告和结果输出

---


## 项目运行环境
### 基础依赖
- Python 3.11+
- pandas
- numpy
- Ubuntu 24 LTS (虚拟机)
- Apache Hive 4.0.1
- Hadoop 3.3.6
- PostgreSQL 16（作为 Hive Metastore）

### 主要使用的pip包
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

### 物理机的环境配置步骤
#### 下载项目并且打开文件夹

```bash
git clone <repository-url>
cd Log-Hive-Insight-Analysis-v2\
```

#### 在miniconda创建并激活虚拟环境

```bash
conda create -n <your-venv-name> python=3.11
conda activate <your-venv-name>
```

#### 安装依赖
```bash
pip install -r requirement.txt
```

### 虚拟机的环境配置步骤
#### 安装OpenJDK 8

下载并安装openjdk 8的包

```bash
sudo apt install openjdk-8-jdk
```

设置并生效环境变量

```bash
nano ~/.bashrc
source ~/.bashrc
```

在文件末尾加入：

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=JAVA_HOME/bin:JAVAHOME/bin:PATH
```

#### 安装 Hadoop 3.3.6

切换到根目录，下载Hadoop压缩包

```bash
cd ~
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
```

在桌面解压

```bash
tar -xzf hadoop-3.3.6.tar.gz
```

把桌面的解压文件夹移动到opt里面

```bash
sudo mv ~/桌面/hadoop-3.3.6  /opt/
```

设置文件夹归属

```bash
sudo chown -R USER:USER:USER /opt/hadoop-3.3.6
```

检查一下权限

```bash
ls -ld /opt/hadoop-3.3.6
```

设置并生效Hadoop环境变量

```bash
nano ~/.bashrc
source ~/.bashrc
```

顺便，去浏览器查看
http://localhost:9870/
观察是否正常active


#### 安装 Apache Hive 4.0.1

切换到根目录，下载Apache Hive 4.0.1压缩包

```Shell
cd ~
wget https://archive.apache.org/dist/hive/hive-4.0.1/apache-hive-4.0.1-bin.tar.gz
```

在桌面解压

```Shell
tar -xzf apache-hive-4.0.1-bin.tar.gz
```

把桌面的解压文件夹移动到opt里面

```Shell
sudo mv ~/桌面/apache-hive-4.0.1-bin /opt/
```

设置并生效hive环境变量

```Shell
nano ~/.bashrc
source ~/.bashrc
```

#### 安装PostgreSQL 16
```bash
sudo apt install postgresql postgresql-contrib
``` 
#### 创建PostgreSQL数据库
```bash
sudo -u postgres psql
CREATE DATABASE "hive";
```
#### 创建数据库用户hive并授权
```bash
CREATE USER hive WITH PASSWORD 'hive';
GRANT ALL PRIVILEGES ON DATABASE hive TO hive;
GRANT USAGE, CREATE ON SCHEMA public TO hive;
ALTER DATABASE hive OWNER TO hive;
ALTER SCHEMA public OWNER TO hive;
\dn+
\du hive
```

#### 安装 PostgreSQL JDBC 驱动
```bash
sudo apt install libpostgresql-jdbc-java
sudo cp /usr/share/java/postgresql-42.7.2.jar $HIVE_HOME/lib/
```


## 项目使用方法

### 1. 初始化数据：

* 在 Jupyter 中打开并分别运行 
  * `01_create_user_raw_data.ipynb`
  * `02_create_date_raw_data.ipynb`
  * `03_create_task_raw_data_v4.ipynb`

* 输出：
  * 用户：10000名
  * 时间线：2026-07-01 至 2026-08-29（60天）
  * 任务：18 万个
  * 任务行为事件：60 万个

### 2. 检查原始数据是否有误
* 在 Jupyter 中打开并分别运行 `04_validate_all_raw_data.ipynb`

### 3. 对虚拟机的apache hive创建hive table
* 运行 `05_create_hive_table.py`

### 4. 在虚拟机上，启动 Hadoop
启动 HDFS：
```bash
start-dfs.sh
```

然后启动 YARN：
```bash
start-yarn.sh
```

### 5. 创建hdfs文件夹

```bash
hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -chmod g+w /user/hive/warehouse

hdfs dfs -mkdir -p /user/hive/todo_analytics/raw/
hdfs dfs -chmod g+w /user/hive/todo_analytics/raw/

```

### 6. 初始化metastore的数据库
```bash
$HIVE_HOME/bin/schematool \
-dbType postgres \
-initSchema \
--verbose
```

### 7. 上传Parquet到虚拟机的hdfs中

例如你的本地文件如果在：

```bash
~/桌面/output_data/
```

那么：

```bash
hdfs dfs -put ~/桌面/output_data/01_dim_user.parquet /user/hive/todo_analytics/raw/dim_user/ 
hdfs dfs -put ~/桌面/output_data/02_dim_date.parquet /user/hive/todo_analytics/raw/dim_date/
hdfs dfs -put ~/桌面/output_data/03_dim_task.parquet /user/hive/todo_analytics/raw/dim_task/
hdfs dfs -put ~/桌面/output_data/ods_todo_event_log /user/hive/todo_analytics/raw/

```

### 8. 启动apache hive
首先，启动Metastore
```bash
$HIVE_HOME/bin/hive --service metastore
```

然后，启动HiveServer2
```bash
$HIVE_HOME/bin/hive --service hiveserver2
```

去浏览器查看
http://localhost:10002/ 
观察是否正常


### 9. 基础数据聚合：

* 运行 `07_clean_and_aggregate_data.ipynb`

### 10. 深层次数据聚合：

* 运行 `08_aggregate_further_data.ipynb`

### 11. 数据可视化：

* 在项目根目录运行 dash 脚本：
  ```Python
    python 09_data_visualisation_v3.py
  ```

## 许可协议

本项目为开源项目，遵循 **Apache 2.0** 许可协议。

## 作者与致谢

Author: Junliang Li
Email: 940747544@qq.com
