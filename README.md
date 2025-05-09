# Stored Procedure Migration Pipeline

## Overview

The **Migration Pipeline** provides a fully automated system for migrating SQL Server stored procedures to **Snowflake**, covering every critical step from script extraction to conversion, testing, and data quality validation. Designed for reliability and extensibility, this pipeline ensures a smooth transition between platforms with minimal manual intervention.

---
## Pipeline Architecture
![Pipeline Workflow](SP_final_pipeline.jpeg)

---

## Workflow Stages

### 1. **Generate SQL Scripts**
- **Tool**: `SQLServerScripter`
- **Function**: Extracts stored procedures from SQL Server using PowerShell automation.
- **Output**: Raw SQL scripts.
- **Script**: [`generate_scripts.py`](helper_scripts/generate_scripts.py)

### 2. **Convert SQL Scripts**
- **Tool**: `SnowConvertRunner`
- **Function**: Transforms extracted SQL into Snowflake-compatible scripts using SnowConvert.
- **Output**: Converted `.sql` files.
- **Script**: [`convert_scripts.py`](helper_scripts/convert_scripts.py)

### 3. **Process Converted Scripts**
- **Tool**: `ScScriptProcessor`
- **Function**: Cleans, formats, and prepares scripts for testing and deployment.
- **Output**: Finalized Snowflake-ready SQL.
- **Script**: [`process_sc_script.py`](helper_scripts/process_sc_script.py)

### 4. **Run Unit Tests**
- **Tool**: `TestStoredProcedure`
- **Function**: Validates converted procedures using PyUnit tests and sample inputs.
- **Output**: Pass/fail status for functional correctness.
- **Script**: [`py_test.py`](helper_scripts/py_test.py)

### 5. **Quality Assurance Testing**
- **Tool**: `DatabaseProcedureExecutor`
- **Function**: Compares execution results between SQL Server and Snowflake.
- **Output**: HTML report with detected data differences.
- **Script**: [`qt_test.py`](helper_scripts/qt_test.py)

### 6. **Run the Pipeline**
- **Command**: `python main.py`
- **Function**: Sequentially runs all stages of the migration process.

---

## Key Components

| Component                   | Responsibility                                           | Source Code                                      |
|----------------------------|-----------------------------------------------------------|--------------------------------------------------|
| `SQLServerScripter`         | Extract SQL Server procedures using PowerShell            | [generate_scripts.py](helper_scripts/generate_scripts.py) |
| `SnowConvertRunner`         | Apply SnowConvert transformation to SQL files             | [convert_scripts.py](helper_scripts/convert_scripts.py)   |
| `ScScriptProcessor`         | Sanitize and format Snowflake SQL for deployment          | [process_sc_script.py](helper_scripts/process_sc_script.py) |
| `TestStoredProcedure`       | Run unit tests on Snowflake scripts                       | [py_test.py](helper_scripts/py_test.py)         |
| `DatabaseProcedureExecutor` | Perform end-to-end validation and output comparison       | [qt_test.py](helper_scripts/qt_test.py)         |

---

## Configuration

Set the following variables in your config before executing the pipeline:

| Parameter               | Description                                           |
|------------------------|-------------------------------------------------------|
| `output_dir`           | Folder to save extracted SQL scripts                  |
| `input_path`           | Path to the folder with raw SQL scripts               |
| `converted_path`       | Directory to save Snowflake-compatible scripts        |
| `processed_input`      | Folder with scripts ready for testing                 |
| `processed_output`     | Destination folder for finalized scripts              |
| `schema_name` *(opt)*  | Target Snowflake schema (if applicable)               |
| `log_file`             | Path to save log output from pipeline execution       |
| `html_report_path`     | Location to store data quality comparison reports     |

---

## Usage

To execute the full migration pipeline, simply run:

```bash
python main.py
```

Ensure all configuration paths are correctly defined in your settings or script.

---

##  Folder Structure and Descriptions

### 📂 `Dq_analysis/`
- `data_quality_report.html` – HTML dashboard comparing output differences  
 ![Data Quality Comparison Dashboard](Dq_analysis/Data%20Quality%20comparison%20Dashboard.png)
- `SP_name_differences.csv` – Differences found in stored procedure outputs  
- `dq_data.json` – Input JSON containing execution parameters  

### 📂 `gen_ai_layer/`
- `generate_sp_exp.py` – Documents the logic of stored procedures  
- `generate_sql_query.py` – Converts user queries to SQL  
- `generate_test_case.py` – Auto-generates test cases for stored procedures 
![Generated Test Cases for Stored Procedure](gen_ai_layer/SP_Created_Test_cases.png) 
- `extract_schema.py` – Extracts DB schema metadata  
- `spapp_modelfile` – Ollama model file for stored procedure explanations  
- `sqapp_modelfile` – Ollama model file for SQL query generation  

### 📂 `input_parameters_PyUnit/`
- `convert_schema_format.py` – Schema formatting for AI query generation  
- `filtered_schema.py` – Filters schema to relevant segments  
- `generate_query.py` – Uses schema and input to generate queries  
- `execute_query.py` – Executes queries on SQL Server to fetch input values  
- `sp_exp_1.json` – Stored procedure explanation file  
- `call_statements.json` – Stored procedure call statements for testing  

### 📂 `py_tests/`
- `py_data.json` – Input parameters for PyUnit stored procedure testing  
- `py_results.html` – HTML dashboard with PyUnit test results  
 ![Output Report of PyUnit Testing](py_tests/SP_PyUnit_Output_dashboard.png)

---

## 💡 Best Practices

- Always back up your SQL Server procedures before migration.
- Test Snowflake scripts in a sandbox environment before production deployment.
- Customize `dq_data.json` and `py_data.json` to fine-tune your validation.
- Ensure consistent schema naming across SQL Server and Snowflake.
- Regularly update the SnowConvert CLI for latest syntax support.

---

## ✅ Final Notes

This pipeline offers a robust framework for SP migration from SQL Server to Snowflake with AI-assisted testing and validation. Modular components allow for easy debugging, reuse, and enhancement.

