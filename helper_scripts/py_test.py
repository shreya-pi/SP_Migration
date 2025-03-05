import snowflake.connector
import unittest
from config import SNOWFLAKE_CONFIG


class TestStoredProcedure(unittest.TestCase):
    # proc_name = "GetCustomerRentals(5)"
    # proc_name = "GetStoreRevenue(1)"
    # proc_name = "GetInactiveCustomers()"

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

    def test_create_procedure_from_file(self):
        """Reads stored procedure SQL from a file and executes it."""
        try:
            with open(self.sql_file, "r") as file:
                sql_script = file.read()
            
            self.cursor.execute(sql_script)
            print(f"Stored procedure {self.proc_name} executed successfully.")
        except Exception as e:
            self.fail(f"Failed to execute stored procedure {self.proc_name}: {str(e)}")

    def test_procedure_execution(self):
        """Test whether the stored procedure runs successfully."""
        try:
            # self.cursor.execute(f"CALL TESTSCHEMA_MG.{self.proc_name} ")
            self.cursor.execute(f"CALL {self.proc_name}")
            result = self.cursor.fetchall()
            self.assertIsNotNone(result, f"Stored procedure {self.proc_name} returned None")
        except Exception as e:
            self.fail(f"Stored procedure {self.proc_name} execution failed: {str(e)}")

# if __name__ == "__main__":
#     unittest.main()




