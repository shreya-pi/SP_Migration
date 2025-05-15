# 🛠️ Helper Scripts – SP\_Migration

This directory contains the core helper scripts essential for **Stored Procedure (SP)** migration, validation, and testing during the SQL Server to Snowflake pipeline transition.

Each script is modular and targets a specific step in the migration lifecycle—from metadata management to conversion, post-processing, and testing.

---

## 📁 Folder Structure

```bash
helper_scripts/
├── convert_scripts.py        
├── create_metadata_table.py  
├── extract_procedures.py     
├── generate_scripts.py       
├── log.py                    
├── process_sc_script.py      
├── py_test.py                
└── qt_test.py                
```

---

## 📜 Script Descriptions

### 🔄 `convert_scripts.py`

* **Purpose:** Acts as a wrapper around **SnowConvert CLI**.
* Converts `.sql` stored procedure files into **Snowflake-compatible scripts**.
* Handles:

  * CLI execution
  * Logging
  * Directory management
* **Dependencies:** Requires SnowConvert to be installed and available in the environment.

---

### 📊 `create_metadata_table.py`

* **Purpose:** Initializes and populates a **Snowflake metadata table** with all stored procedure details.
* Captures:

  * Procedure definitions
  * Source metadata (DB, schema, name)
  * Flags for conversion
  * Target DDL columns for Snowflake
  * Load timestamps, parameters, errors, and deployment status
* Creates table if not exists:

  ```sql
  CREATE TABLE IF NOT EXISTS <target_table> (
      SOURCE                STRING,
      DBNAME                STRING,
      SCHEMA_NAME           STRING,
      PROCEDURE_NAME        STRING,
      PROCEDURE_DEFINITION  STRING,
      CONVERSION_FLAG       BOOLEAN,
      LOAD_TIMESTAMP        TIMESTAMP_NTZ(9),
      SNOWFLAKE_DBNAME      STRING,
      SNOWFLAKE_SCHEMA_NAME STRING,
      SNOWFLAKE_DDL         STRING,
      PARAMETERS            STRING,
      IS_DEPLOYED           BOOLEAN,
      ERRORS                STRING
  );
  ```

---

### 🧠 `extract_procedures.py`

* **Purpose:** Selectively extracts stored procedures based on `CONVERSION_FLAG = TRUE` from the metadata table.
* Writes each procedure to a `.sql` file.
* **Use case:** Preferred when migrating only a subset of approved/converted SPs.
* **Replaces:** A more targeted alternative to `generate_scripts.py`.

---

### ⚡ `generate_scripts.py`

* **Purpose:** Extracts **all** stored procedure definitions from SQL Server using PowerShell and saves them as `.sql` files.
* Acts as a **bulk extraction** utility.
* **Use case:** Full migration where no filtering by flag is needed.
* **Replaced by:** `extract_procedures.py` when conditional extraction is required.

---

### 🧾 `log.py`

* **Purpose:** Centralized **logging utility** used across scripts.
* Handles:

  * Timestamped logs
  * Standardized formatting
  * Log file creation and rotation
* Helps in tracking conversion, errors, and test runs.

---

### 🧹 `process_sc_script.py`

* **Purpose:** Performs post-processing on converted Snowflake SQL files.
* Responsibilities:

  * Remove unwanted syntax
  * Reformat procedure headers and parameters
  * Adjust SQL style to match Snowflake compatibility
* **Use case:** Cleans up output from `convert_scripts.py`.

---

### 🧪 `py_test.py`

* **Purpose:** Automates **unit testing** for converted stored procedures.
* Highlights:

  * Dynamically detects and initializes procedure parameters with `NULL`
  * Executes the procedure using `CALL` statements
  * Logs and stores results in a tracking table on Snowflake
* **Benefit:** Ensures logical correctness post-migration.

---

### 🔁 `qt_test.py`

* **Purpose:** Performs **quality testing** by comparing execution results of SQL Server and Snowflake versions of the same procedure.
* Responsibilities:

  * Run procedure in both environments
  * Capture and compare outputs
  * Identify any mismatches for investigation
* **Use case:** End-to-end functional validation.

---

## 🧩 Recommended Script Flow

```text
[generate_scripts.py] OR [extract_procedures.py]
            ↓
    [convert_scripts.py]
            ↓
   [process_sc_script.py]
            ↓
      [create_metadata_table.py]
            ↓
        [py_test.py]
            ↓
         [qt_test.py]
```

---

## 🔗 External Dependencies

* **SnowConvert CLI** for SQL Server → Snowflake conversion.
* **Snowflake Python Connector** or **SQLAlchemy** for DB interactions.
* **PowerShell** (for `generate_scripts.py` only).
* **Python 3.8+**

