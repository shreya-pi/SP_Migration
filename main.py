import unittest
from helper_scripts.generate_scripts import SQLServerScripter
from helper_scripts.convert_scripts import SnowConvertRunner
from helper_scripts.process_sc_script import ScScriptProcessor
from helper_scripts.py_test import TestStoredProcedure
from helper_scripts.qt_test import DatabaseProcedureExecutor



class MigrationPipeline:
    """Class to handle the entire pipeline for SQL Server to Snowflake migration."""
    
    def __init__(self):
        # Configuration settings
        #to extract the scripts from the SQL Server database
        # self.server = "tulapi.database.windows.net"
        # self.database = "Airbyte_demo_base"
        self.output_dir = r"C:\Users\shreya.naik\Documents\Flask\Sp_demo\sql_output"
        
        #to convert the extracted scripts to Snowflake compatible scripts
        self.input_path = r"C:\Users\shreya.naik\Documents\Flask\Sp_demo\sql_output\Airbyte_demo_base"
        self.output_path = r"C:\Users\shreya.naik\Documents\Flask\Sp_demo\converted_output"
        self.schema_name = "TESTSCHEMA_MG"
        self.log_file = r"C:\Users\shreya.naik\Documents\Flask\Sp_demo\assessment_log.txt"

        #to process the converted scripts
        self.processed_input_folder = "converted_output/Output/SnowConvert"
        self.processed_output_folder = "processed_output"


        #to PyUnit run tests on the processed scripts

        # self.proc_name = "GetStoreRevenue(1)"
        # self.sql_file = r"processed_output\processed_dbo_GetStoreRevenue.sql"

        self.proc_name = "GetTopRentedMovies()"
        self.sql_file = r"processed_output\processed_dbo_GetTopRentedMovies.sql"

        

        #to perform quality testing on the database procedures

        # self.snowflake_proc_name = "GetCustomerRentals(5)"
        # self.sqlserver_proc_name = "GetCustomerRentals @customer_id = 5"

        # self.snowflake_proc_name = "GetStoreRevenue(1)"
        # self.sqlserver_proc_name = "GetStoreRevenue @store_id = 1"

        # self.snowflake_proc_name = "GetInActiveCustomers()"
        # self.sqlserver_proc_name = "GetInActiveCustomers"

        self.snowflake_proc_name = "GetTopRentedMovies()"
        self.sqlserver_proc_name = "GetTopRentedMovies"


    def generate_sql_scripts(self):
        """Generate SQL scripts from the SQL Server database."""
        print("🔹 Generating SQL scripts from SQL Server...")
        # scripter = SQLServerScripter(self.server, self.database, self.output_dir)
        scripter = SQLServerScripter(self.output_dir)
        scripter.run_powershell_script()

    def convert_sql_scripts(self):
        """Run the SnowConvert command and convert SQL scripts."""
        print("🔹 Converting SQL scripts using SnowConvert...")
        runner = SnowConvertRunner(self.input_path, self.output_path, self.schema_name, self.log_file)
        runner.run_snowct_command()

    def process_sc_scripts(self):
        """Process the converted SQL scripts."""
        print("🔹 Processing converted SQL scripts...")
        sql_processor = ScScriptProcessor(self.processed_input_folder, self.processed_output_folder)
        sql_processor.process_all_files()

    def run_py_tests(self):
        """Run PyUnit tests on the processed SQL scripts."""
        print("🔹 Running unit tests on stored procedures...")

        suite = unittest.TestSuite()
        suite.addTest(TestStoredProcedure(self.proc_name, self.sql_file, "test_create_procedure_from_file"))
        suite.addTest(TestStoredProcedure(self.proc_name, self.sql_file, "test_procedure_execution"))

        runner = unittest.TextTestRunner()
        runner.run(suite)

    def quality_testing(self):
        """Perform quality testing on database procedures."""
        print("🔹 Performing quality testing on database procedures...")
        executor = DatabaseProcedureExecutor()
        executor.run(self.snowflake_proc_name, self.sqlserver_proc_name)

    def run_pipeline(self):
        """Run the entire migration pipeline."""
        print("🚀 Starting the migration pipeline...\n")
        self.generate_sql_scripts()
        self.convert_sql_scripts()
        self.process_sc_scripts()
        self.run_py_tests()
        self.quality_testing()
        print("\n✅ Pipeline execution completed successfully!")

if __name__ == "__main__":
    pipeline = MigrationPipeline()
    pipeline.run_pipeline()





