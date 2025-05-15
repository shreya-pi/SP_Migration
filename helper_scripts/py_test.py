import snowflake.connector
import unittest
import os
import io
import sys
import re
from datetime import datetime, timezone
from config import SNOWFLAKE_CONFIG
from .log import log_info,log_error


# Create the Snowflake table
# First, run this DDL once in your Snowflake console (or via a migration script):

# CREATE OR REPLACE TABLE TEST_RESULTS_LOG (
#   TEST_CASE_ID     STRING,
#   TEST_CASE_NAME   STRING,
#   PROCEDURE_NAME   STRING,
#   TEST_TIMESTAMP   TIMESTAMP_NTZ,
#   STATUS           STRING,
#   ERRORS           STRING
# );

test_case_id_counter = 0

# Global list to store test results
test_results = []

# Snowflake DDL target table
TARGET_TABLE = "TEST_RESULTS_LOG"
METADATA_TABLE = "PROCEDURES_METADATA"

def generate_html_report(results, output_file="py_tests/py_results.html"):
    """Generates a dynamic HTML file with test results."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stored Procedure Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .success { color: green; font-weight: bold; }
        .failure { color: red; font-weight: bold; }
        pre { white-space: pre-wrap; word-wrap: break-word; max-height: 200px; overflow-y: auto; }
    </style>
</head>
<body>
    <h2>Stored Procedure Test Report</h2>
    <table>
        <tr>
            <th>Stored Procedure</th>
            <th>Test Name/Type</th>
            <th>Status</th>
            <th>Reason for Failure</th>
        </tr>"""

    for proc_name, test_type, status, reason, output in results:  # Unpacking 4 values
        status_class = "success" if status == "✅ Success" else "failure"
        html_content += f"""
        <tr>
            <td>{proc_name}</td>
            <td>{test_type}</td>
            <td class="{status_class}">{status}</td>
            <td>{reason}</td>
            <td><pre>{output}</pre></td>
        </tr>"""

    html_content += """
    </table>
</body>
</html>"""

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_content)

    log_info(f"Test report generated: {os.path.abspath(output_file)} for {proc_name}")

class TestStoredProcedure(unittest.TestCase):

    def __init__(self, sql_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.proc_name = proc_name
        self.sql_file = sql_file
        filename = os.path.basename(self.sql_file)  
        m = re.match(r'.*_(?P<proc>[^.]+)\.sql$', filename)
        self.proc_name = m.group('proc') 

    @classmethod
    def setUpClass(cls):
        """Setup Snowflake connection before tests."""
        cls.conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        cls.cursor = cls.conn.cursor()

    @classmethod
    def tearDownClass(cls):
        """Close the connection after tests."""
        cls.cursor.close()
        cls.conn.close()
        generate_html_report(results=test_results)

    def run_test_with_capture(self, test_func, test_name="test_function"):
        global test_case_id_counter

        # --- 2) Increment counter and create ID ---
        test_case_id_counter += 1
        test_case_id = str(test_case_id_counter)

        """Runs a test function and captures its output."""
        output_capture = io.StringIO()
        sys.stdout = output_capture
        sys.stderr = output_capture  # Capture errors as well

        try:
            test_func()
            status = "✅ Success"
            reason = "-"
        except Exception as e:
            status = "❌ Failed"
            reason = str(e)

        sys.stdout = sys.__stdout__  # Restore standard output
        sys.stderr = sys.__stderr__  # Restore error output

        test_results.append((self.proc_name, test_name, status, reason, output_capture.getvalue()))

        # 2) Immediately INSERT into Snowflake Pyunit test results table
        # → get a timezone‐aware UTC datetime, then format it
        utc = datetime.now(timezone.utc)
        # if you still want a naive string (e.g. for TIMESTAMP_NTZ), drop the tzinfo:
        naive = utc.replace(tzinfo=None)
        # format to millisecond precision
        ts = naive.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        # ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        insert_sql = f"""
          INSERT INTO {TARGET_TABLE} (
            TEST_CASE_ID,
            TEST_CASE_NAME,
            PROCEDURE_NAME,
            TEST_TIMESTAMP,
            STATUS,
            ERRORS
          ) VALUES (%s, %s, %s, TO_TIMESTAMP_NTZ(%s), %s, %s)
        """
        # You can generate a unique TEST_CASE_ID however you like; here we just combine proc+test name+ts
        # test_case_id = f"{self.proc_name}::{test_name}::{ts}"
        try:
            self.cursor.execute(
                insert_sql,
                (test_case_id, test_name, self.proc_name, ts, status, reason)
            )
            self.conn.commit()
        except Exception as sf_e:
            log_error(f"Failed to log to Snowflake for {self.proc_name}/{test_name}: {sf_e}")

        
        # ── 5) If this test was a SUCCESS, mark the proc deployed in the metadata table
        if status == "✅ Success":
            clean_proc_name = re.sub(r'\(.*\)$', '', self.proc_name)
            try:
                update_sql = f"""
                UPDATE {METADATA_TABLE}
                   SET IS_DEPLOYED = TRUE
                 WHERE PROCEDURE_NAME = %s
                """
                self.cursor.execute(update_sql, (clean_proc_name))
                self.conn.commit()
                log_info(f"Marked {self.proc_name} as deployed in {METADATA_TABLE}")
            except Exception as upd_e:
                log_error(f"Failed to update IS_DEPLOYED for {clean_proc_name}: {upd_e}")


    def test_create_procedure_from_file(self):
        def test_logic():
            with open(self.sql_file, "r") as file:
                sql_script = file.read()
            self.cursor.execute(sql_script)
            log_info(f"Stored procedure {self.proc_name} executed successfully.")

        self.run_test_with_capture(test_logic, "test_create_procedure")



    def test_procedure_execution(self):
        """Test whether the stored procedure runs successfully."""

        # 2) Fetch its PARAMETERS definition from Snowflake metadata:
        self.cursor.execute(
            "SELECT PARAMETERS FROM PROCEDURES_METADATA WHERE PROCEDURE_NAME = %s",
            (self.proc_name,)
        )
        row = self.cursor.fetchone()
        params_str = row[0] if row and row[0] else ""
        
        # 3) Count declared parameters (commas → count+1), or zero if empty
        num_params = len(params_str.split(',')) if params_str.strip() else 0

        # 4) Build the "(NULL, NULL, ...)" suffix
        nulls = ", ".join("NULL" for _ in range(num_params))
        full_proc_call = f"{self.proc_name}({nulls})"

        def test_logic():
            self.cursor.execute(f"CALL {full_proc_call}")
            result = self.cursor.fetchall()
            self.assertIsNotNone(result, f"Stored procedure {full_proc_call} returned None")
            log_info(f"Stored procedure {full_proc_call} executed and returned results.")

        self.run_test_with_capture(test_logic, "test_procedure_execution")





