import snowflake.connector
import pyodbc
import pandas as pd
from config import SNOWFLAKE_CONFIG, SQL_SERVER_CONFIG



class DatabaseProcedureExecutor:
    """Class to execute stored procedures from Snowflake and SQL Server, and compare results."""
    
    def __init__(self):
        self.snowflake_config = SNOWFLAKE_CONFIG
        self.sql_server_config = SQL_SERVER_CONFIG

    def execute_snowflake_procedure(self, proc_name):
        """Executes a Snowflake stored procedure and returns the result as a DataFrame."""
        conn = snowflake.connector.connect(**self.snowflake_config)
        cursor = conn.cursor()
        
        query = f"CALL {proc_name};"
        cursor.execute(query)
        result = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        df = pd.DataFrame.from_records(result, columns=columns)
        
        cursor.close()
        conn.close()
        return df

    def execute_sqlserver_procedure(self, proc_name):
        """Executes a SQL Server stored procedure and returns the result as a DataFrame."""
        conn_str = f"DRIVER={self.sql_server_config['driver']};SERVER={self.sql_server_config['server']};DATABASE={self.sql_server_config['database']};UID={self.sql_server_config['username']};PWD={self.sql_server_config['password']}"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        query = f"EXEC {proc_name};"
        cursor.execute(query)
        result = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        # print("Extracted Column Names:", columns)
        
        df = pd.DataFrame.from_records(result, columns=columns)
        
        cursor.close()
        conn.close()
        return df

    @staticmethod
    def compare_results(df1, df2):
        """Compares two DataFrames after fixing column names and data types."""
        count_df1 = len(df1)
        count_df2 = len(df2)

        print(f"Number of rows in Snowflake DataFrame: {count_df1}")
        print(f"Number of rows in SQL Server DataFrame: {count_df2}")

        df1.columns = df1.columns.str.lower()
        df2.columns = df2.columns.str.lower()

        # print("df1 index:", df1.index)
        # print("df2 index:", df2.index)
        
        # print("df1 index type:", type(df1.index))
        # print("df2 index type:", type(df2.index))

        print("df1 columns:", df1.columns.tolist())
        print("df2 columns:", df2.columns.tolist())
 
 
        #  if not df1.index.equals(df2.index):
        #      print("❌ Index mismatch detected!")
        #      print("Indexes only in df1:", df1.index.difference(df2.index))
        #      print("Indexes only in df2:", df2.index.difference(df1.index))

            # Align column orders
        df2 = df2[df1.columns]
    
        # Align data types
        for col in df1.columns:
            if df1[col].dtype != df2[col].dtype:
                try:
                    # Attempt to convert df2 column to match df1 column type
                    df1[col] = df1[col].astype(df2[col].dtype)
                except ValueError:
                    # If conversion fails, convert both columns to string
                    df1[col] = df1[col].astype(str)
                    df2[col] = df2[col].astype(str)
    
        print("df1 dtypes:\n", df1.dtypes)
        print("df2 dtypes:\n", df2.dtypes)



        if df1.equals(df2):
            print("✅ The results match perfectly!")
        else:
            print("❌ The results do not match!")

                # Find common columns between the two DataFrames for merging
            common_columns = df1.columns.intersection(df2.columns).tolist()
        
            # Perform an outer merge on common columns to detect differences
            merged_df = pd.merge(df1, df2, how='outer', indicator=True, on=common_columns)
        
            # Extract rows that differ or are missing in one of the DataFrames
            diff = merged_df[merged_df['_merge'] != 'both'].copy()

                # Check for Categorical columns and add 'NaN' as a category if needed
            for col in diff.select_dtypes(['category']).columns:
                # Explicitly cast to category if not already compatible
                diff[col] = diff[col].astype('category')
                
                # Add 'NaN' as a category if not present
                if 'NaN' not in diff[col].cat.categories:
                    diff[col] = diff[col].cat.add_categories(['NaN'])
                
            # Replace missing entries with NaN explicitly (should already be the case)
            diff = diff.fillna('NaN')
        
            # Save the differences to CSV
            diff.to_csv("differences.csv", index=True)
        
            count_diff = len(diff)
            print(f"Number of differences detected: {count_diff}")

        return count_df1, count_df2  # Return counts if needed for further processing



    def run(self, snowflake_proc, sqlserver_proc):
        """Runs the procedures and compares the results."""
        print(f"Executing Snowflake procedure: {snowflake_proc}")
        snowflake_result = self.execute_snowflake_procedure(snowflake_proc)
        
        print(f"Executing SQL Server procedure: {sqlserver_proc}")
        sqlserver_result = self.execute_sqlserver_procedure(sqlserver_proc)
        
        print("Comparing results...")
        self.compare_results(snowflake_result, sqlserver_result)

