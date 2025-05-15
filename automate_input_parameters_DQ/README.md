# 🤖 Automated Input Parameter Generator for Snowflake Procedures (DQ Testing)

This module dynamically constructs valid `CALL` statements for Snowflake **stored procedures** by generating input parameter values using a **Huggingface transformer model** trained on database schemas.
The goal is to **automate PyUnit functional testing** by intelligently populating SP parameters with realistic values fetched from the actual database via generated SQL queries.

---

## 🧩 Objective

> 🔍 **To dynamically generate test input values** for SP parameters by:

1. Extracting the database schema.
2. Feeding it (after preprocessing) into a Huggingface **T5 model** fine-tuned on text-to-SQL tasks.
3. Prompting the model using procedure name and input parameters.
4. Executing the generated query to retrieve test inputs.
5. Constructing a `CALL` statement using the retrieved values.

This enables **high-quality, realistic unit testing** of Snowflake procedures.

---

## 📁 Folder Structure

```bash
automate_input_parameters_Dq/
├── call_statements.json          # Output CALL statements (auto-generated)
├── convert_schema_format.py      # Cleans & formats schema for model input
├── execute_query.py              # Executes model-generated SQL on DB
├── filtered_schema.py            # Embedding-based schema chunk filtering
├── generate_query.py             # Uses LLM to generate SQL from input
├── main.py                       # Pipeline entry point for DQ testing
├── schema.txt                    # Preprocessed schema (model input format)
├── sp_exp_1.json                 # Input SP name + parameter config
└── requirements.txt              # Python dependencies
```

---

## 🚀 Workflow Overview

### Step 1: 🔍 Extract & Format Schema

* **Script:** `extract_schema.py` *(in `gen_ai_layer/`, assumed dependency)*
* Retrieves table/column metadata from the SQL Server DB.

### Step 2: 🧹 Clean Schema Format

* **Script:** `convert_schema_format.py`
* Converts raw schema into a natural language-style format suitable for LLM input.
* Output stored in `schema.txt`

---

### Step 3: 📄 Define SP & Parameters

* **Script:** `sp_exp_1.json`

```json
{
  "sp_name": "get_user_activity",
  "input_parameters": {
    "user_id": "INT",
    "activity_date": "DATE"
  }
}
```

---

### Step 4: 🔎 Filter Schema Context

* **Script:** `filtered_schema.py`
* Embeds schema lines using a sentence embedding model.
* Computes similarity between schema lines and procedure context.
* Selects top `N` relevant chunks to reduce LLM context length while maintaining accuracy.

---

### Step 5: 🧠 Generate SQL Query Using Huggingface Model

* **Script:** `generate_query.py`
* Loads a fine-tuned model like [`gaussalgo/T5-LM-Large-text2sql-spider`](https://huggingface.co/gaussalgo/T5-LM-Large-text2sql-spider)
* Uses:

  ```python
  AutoTokenizer.from_pretrained(...)
  AutoModelForSeq2SeqLM.from_pretrained(...)
  ```
* Dynamically generates a query based on filtered schema + SP input parameters.
* Example Prompt:

  ```
  Based on the schema, generate a query to get sample values for:
  Procedure: get_user_activity
  Parameters: user_id (INT), activity_date (DATE)
  ```

---

### Step 6: 🏃 Execute Generated Query

* **Script:** `execute_query.py`
* Executes the SQL on the **source SQL Server database**.
* Extracts one or more random rows from the result.
* These values will be used to construct the final `CALL` statement.

---

### Step 7: 🔨 Generate CALL Statement

* The parameter values are used to construct a valid Snowflake SP invocation:

```sql
CALL get_user_activity(12345, '2024-10-01');
```

* Output is saved in `call_statements.json` for downstream PyUnit or DQ testing.

---

## 📦 Installation

> This module can run standalone. Use the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## ▶️ How to Run

1. Make sure schema is extracted and converted to `schema.txt`.
2. Define your target procedure and inputs in `sp_exp_1.json`.
3. Run the full flow:

   ```bash
   python main.py
   ```

---

## 🛠️ Configuration

You can change:

* Number of schema lines to retrieve in `filtered_schema.py`
* Model name in `generate_query.py`
* DB connection details in `execute_query.py`

---

## 💡 Use Cases

* Auto-generate realistic unit test inputs without manual guesswork.
* Dynamically validate stored procedure logic during CI/CD.
* Use as a plug-in for PyUnit or Snowflake DQ validation suites.

---

## 📚 Dependencies

* `transformers` by Huggingface
* `sentence-transformers`
* `pyodbc` / `sqlalchemy` (for SQL Server access)
* `scikit-learn` (for cosine similarity)
* `pandas`, `json`, `tqdm`, etc.

---

## 🙌 Contribution Ideas

* Add support for **multiple procedures in batch**.
* Enhance filtering with additional heuristics (table relevance).
* Switch backend to Snowflake once metadata is ported.

---

.
