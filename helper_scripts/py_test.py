import snowflake.connector
import unittest
import os
import io
import sys
from config import SNOWFLAKE_CONFIG
from .log import log_info,log_error

# Global list to store test results
test_results = []


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

    def __init__(self, proc_name, sql_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proc_name = proc_name
        self.sql_file = sql_file

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

    def test_create_procedure_from_file(self):
        def test_logic():
            with open(self.sql_file, "r") as file:
                sql_script = file.read()
            self.cursor.execute(sql_script)
            log_info(f"Stored procedure {self.proc_name} executed successfully.")

        self.run_test_with_capture(test_logic, "test_create_procedure")



    def test_procedure_execution(self):
        """Test whether the stored procedure runs successfully."""

        def test_logic():
            self.cursor.execute(f"CALL {self.proc_name}")
            result = self.cursor.fetchall()
            self.assertIsNotNone(result, f"Stored procedure {self.proc_name} returned None")
            log_info(f"Stored procedure {self.proc_name} executed and returned results.")

        self.run_test_with_capture(test_logic, "test_procedure_execution")


# if __name__ == "__main__":
#     unittest.main()




