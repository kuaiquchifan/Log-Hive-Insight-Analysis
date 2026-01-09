# LogHivePlatform — Mobile App Log ETL & Analytics Pipeline

A mobile app log generation, storage, and analysis system based on Apache Hive.

## Prerequisites
- Python 3.11+
- Apache Hive 3.1.3
- PostgreSQL 17.4 (for Metastore)
- Hadoop 3.3.6

## 1. Initialize PostgreSQL Metastore
```bash
psql -U postgres -f G:\myHiveAnalysis\init-postgres.sql
```

## 2. Generate Logs
```bash
python generate_logs.py
```

## 3. Create a Hive table
```bash
python create_hive_table.py
```

## 4. Loading data
```bash
python load_data_to_hive.py
```

## 5. Analyze data
```bash
python analyze_logs.py
```

Execute data analysis queries, including:  
- Total number of users  
- Event type distribution  
- Top 10 most popular pages

## License
This project is open source and available under the **Apache 2.0** License.

## Authors and Acknowledgments
Author: Junliang Li  
Email: 940747544@qq.com
