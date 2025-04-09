import unittest
import json
from helper_scripts.generate_scripts import SQLServerScripter
from helper_scripts.convert_scripts import SnowConvertRunner
from helper_scripts.process_sc_script import ScScriptProcessor
from helper_scripts.py_test import TestStoredProcedure
from helper_scripts.qt_test import DatabaseProcedureExecutor
from helper_scripts.log import log_info, log_error



class MigrationPipeline:
    """Class to handle the entire pipeline for SQL Server to Snowflake migration."""
    
    def __init__(self):
        # Configuration settings
        #to extract the scripts from the SQL Server database
        self.output_dir = r"C:\Users\shreya.naik\Documents\SP_Demo\Sp_demo_Copy\sql_output"

    #------------------------------------------------------------------------------- 
        #to convert the extracted scripts to Snowflake compatible scripts
        self.input_path = r"C:\Users\shreya.naik\Documents\SP_Demo\Sp_demo_Copy\sql_output\Airbyte_demo_base"
        self.output_path = r"C:\Users\shreya.naik\Documents\SP_Demo\Sp_demo_Copy\converted_output"
        self.schema_name = "DB_SCHEMA" #target schema (Optional)
        self.log_file = r"C:\Users\shreya.naik\Documents\SP_Demo\Sp_demo_Copy\logs\assessment_log.txt"
        # C:\Users\shreya.naik\Documents\SP_Demo\Sp_demo - Copy\main.py
    #-------------------------------------------------------------------------------
        #to process the converted scripts
        self.processed_input_folder = "converted_output/Output/SnowConvert"
        self.processed_output_folder = "processed_output"

    #-------------------------------------------------------------------------------
        #to PyUnit run tests on the processed scripts

        # self.proc_name = "GetStoreRevenue(1)"
        # self.sql_file = r"processed_output\processed_dbo_GetStoreRevenue.sql"

        # self.proc_name = "GetTopRentedMovies()"
        # self.sql_file = r"processed_output\processed_dbo_GetTopRentedMovies.sql"

        self.proc_name = "GetInActiveCustomers()"
        self.sql_file = r"processed_output\processed_dbo_GetInActiveCustomers.sql"

        #-------------------------------------------------------------------------------

        #to perform quality testing on the database procedures

        # self.snowflake_proc_name = "GetCustomerRentals(5)"
        # self.sqlserver_proc_name = "GetCustomerRentals @customer_id = 5"

        # self.snowflake_proc_name = "GetStoreRevenue(1)"
        # self.sqlserver_proc_name = "GetStoreRevenue @store_id = 1"

        # self.snowflake_proc_name = "GetInActiveCustomers()"
        # self.sqlserver_proc_name = "GetInActiveCustomers"

        # self.snowflake_proc_name = "GetTopRentedMovies()"
        # self.sqlserver_proc_name = "GetTopRentedMovies"

        self.output_html_file = "Dq_analysis/data_quality_report.html"


    def generate_sql_scripts(self):
        """Generate SQL scripts from the SQL Server database."""
        log_info("🔹 Generating SQL scripts from SQL Server...")
        # scripter = SQLServerScripter(self.server, self.database, self.output_dir)
        scripter = SQLServerScripter(self.output_dir)
        scripter.run_powershell_script()

    def convert_sql_scripts(self):
        """Run the SnowConvert command and convert SQL scripts."""
        log_info("🔹 Converting SQL scripts using SnowConvert...")
        runner = SnowConvertRunner(self.input_path, self.output_path, self.schema_name, self.log_file)
        runner.run_snowct_command()

    def process_sc_scripts(self):
        """Process the converted SQL scripts."""
        log_info("🔹 Processing converted SQL scripts...")
        sql_processor = ScScriptProcessor(self.processed_input_folder, self.processed_output_folder)
        sql_processor.process_all_files()

    def run_py_tests(self):
        """Run PyUnit tests on the processed SQL scripts."""
        log_info("🔹 Running unit tests on stored procedures...")

        with open("py_tests/py_data.json", "r") as file:
            py_data = json.load(file)
        
        # Iterate through each query and access values
        for query in py_data:
            proc_query = query["query"]
            input_file = query["input_file"]

            suite = unittest.TestSuite()
            suite.addTest(TestStoredProcedure(proc_query, input_file, "test_create_procedure_from_file"))
            suite.addTest(TestStoredProcedure(proc_query, input_file, "test_procedure_execution"))

            runner = unittest.TextTestRunner()
            runner.run(suite)

        # suite = unittest.TestSuite()
        # suite.addTest(TestStoredProcedure(self.proc_name, self.sql_file, "test_create_procedure_from_file"))
        # suite.addTest(TestStoredProcedure(self.proc_name, self.sql_file, "test_procedure_execution"))

        # runner = unittest.TextTestRunner()
        # runner.run(suite)

    def quality_testing(self):
        """Perform quality testing on database procedures."""
        log_info("🔹 Performing quality testing on database procedures...")
        executor = DatabaseProcedureExecutor()

        with open("Dq_analysis/dq_data.json", "r") as file:
            dq_data = json.load(file)
        
        for query in dq_data:
            snowflake_proc_query = query["snowflake_proc_query"]
            sqlserver_proc_query = query["sqlserver_proc_query"]

            executor.run(snowflake_proc_query, sqlserver_proc_query)
        
        executor.generate_comparison_html(self.output_html_file)



    def run_pipeline(self):
        """Run the entire migration pipeline."""
        log_info("🚀 Starting the migration pipeline...\n")
        self.generate_sql_scripts()
        self.convert_sql_scripts()
        self.process_sc_scripts()
        self.run_py_tests()
        self.quality_testing()
        log_info("\n✅ Pipeline execution completed successfully!")

if __name__ == "__main__":
    pipeline = MigrationPipeline()
    pipeline.run_pipeline()





