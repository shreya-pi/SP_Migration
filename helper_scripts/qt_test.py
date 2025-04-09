import snowflake.connector
import pyodbc
import pandas as pd
from config import SNOWFLAKE_CONFIG, SQL_SERVER_CONFIG
from .log import log_info,log_error, log_dq_info, log_dq_error

comparison_data = []

class DatabaseProcedureExecutor:
    """Class to execute stored procedures from Snowflake and SQL Server, and compare results."""
    
    def __init__(self):
        self.snowflake_config = SNOWFLAKE_CONFIG
        self.sql_server_config = SQL_SERVER_CONFIG
        self.all_comparisons = []

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



    # def generate_comparison_html(self, output_filename):
    #     # Convert the list of dictionaries to a DataFrame
    #     # df = pd.DataFrame(comparison_data)
    #     df = pd.DataFrame(self.all_comparisons)
        
    #     # Generate HTML table
    #     html_content = f"""
    #     <html>
    #     <head>
    #         <title>Comparison Report</title>
    #     <style>
    #         body {{
    #             font-family: Arial, sans-serif;
    #             margin: 20px;
    #         }}
    #         table {{
    #             width: 100%;
    #             border-collapse: collapse;
    #             margin-bottom: 20px;
    #         }}
    #         th, td {{
    #             border: 1px solid black;
    #             padding: 8px;
    #             text-align: left;
    #         }}
    #         th {{
    #             background-color: #4CAF50;
    #             color: white;
    #         }}
    #         .mismatch {{
    #             background-color: #ffcccc;
    #         }}
    #         .procedure-header {{
    #             font-size: 18px;
    #             font-weight: bold;
    #             background-color: #ddd;
    #             padding: 10px;
    #             margin-top: 20px;
    #             border: 1px solid black;
    #             text-align: center;
    #         }}
    #     </style>

  
    #         </style>
    #     </head>
    #     <body>
    #         <h2>Comparison Report</h2>
    #     {df.to_html(index=False, escape=False)}
    #     </body>
    #     </html>
    #     """
        
    #     # Write to an HTML file
    #     with open(output_filename, "w", encoding="utf-8") as file:
    #         file.write(html_content)
        
    #     log_dq_info(f"HTML report generated: {output_filename}")

    def generate_comparison_html(self, output_filename):
        html_content = """
        <html>
        <head>
            <title>Comparison Report</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                th, td {
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #4CAF50;
                    color: white;
                }
                .mismatch {
                    background-color: #ffcccc;
                }
                .procedure-header {
                    font-size: 18px;
                    font-weight: bold;
                    background-color: #ddd;
                    padding: 10px;
                    margin-top: 20px;
                    border: 1px solid black;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <h2>Comparison Report</h2>
        """
    
        procedures = {}  # Dictionary to store grouped attributes under each procedure name
        current_proc_name = None  # Track the active procedure section
    
        for row in self.all_comparisons:
            if row["Attribute"] == "Executed Procedure":
                # Extract procedure name from Snowflake output
                current_proc_name = row["Snowflake Procedure Output"]
                procedures[current_proc_name] = []  # Initialize list for this procedure
            else:
                if current_proc_name:
                    procedures[current_proc_name].append(row)  # Store attributes under this procedure
    
        # Generate HTML content for each procedure
        for proc_name, rows in procedures.items():
            html_content += f'<div class="procedure-header">{proc_name}</div>'
            
            if rows:
                table_df = pd.DataFrame(rows)
                html_content += table_df.to_html(index=False, escape=False)
            else:
                html_content += "<p>No additional attributes for this procedure.</p>"
    
        html_content += """
        </body>
        </html>
        """
    
        # Write to an HTML file
        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(html_content)
    
        log_dq_info(f"HTML report generated: {output_filename}")


    def compare_results(self, df1, df2, proc_snowflake, proc_sqlserver):
        comparison_data = []
    
        # Compare procedure names
        comparison_data.append({
            "Attribute": "Executed Procedure",
            "Snowflake Procedure Output": proc_snowflake,
            "SQL Server Procedure Output": proc_sqlserver,
            "Comparison": "Same" if proc_snowflake.lower() == proc_sqlserver.lower() else "Different"
        })
    
        # Compare number of rows
        count_df1 = len(df1)
        count_df2 = len(df2)
        comparison_data.append({
            "Attribute": "Number of Rows",
            "Snowflake Procedure Output": count_df1,
            "SQL Server Procedure Output": count_df2,
            "Comparison": "Same" if count_df1 == count_df2 else "Different"
        })
    
        # Standardize column names
        # df1.columns = df1.columns.str.lower()
        # df2.columns = df2.columns.str.lower()
        # Ensure column names are strings before converting to lowercase
        df1.columns = df1.columns.astype(str).str.lower()
        df2.columns = df2.columns.astype(str).str.lower()
    
        # Compare column names
        col_df1 = set(df1.columns)
        col_df2 = set(df2.columns)

        comparison_data.append({
            "Attribute": "Column Names",
            "Snowflake Procedure Output": ", ".join(col_df1),
            "SQL Server Procedure Output": ", ".join(col_df2),
            "Comparison": "Same" if col_df1 == col_df2 else "Different"
        })
    
        # Compare data types
        dtype_df1 = {col: str(df1[col].dtype) for col in df1.columns}
        dtype_df2 = {col: str(df2[col].dtype) for col in df2.columns}
        comparison_data.append({
            "Attribute": "Data Types",
            "Snowflake Procedure Output": ", ".join(f"{col}: {dtype}" for col, dtype in dtype_df1.items()),
            "SQL Server Procedure Output": ", ".join(f"{col}: {dtype}" for col, dtype in dtype_df2.items()),
            "Comparison": "Same" if dtype_df1 == dtype_df2 else "Different"
        })
    
        # Align column orders and convert types
        df2 = df2[df1.columns]  # Align column order
        for col in df1.columns:
            if df1[col].dtype != df2[col].dtype:
                df1[col] = df1[col].astype(str)
                df2[col] = df2[col].astype(str)
    

            # Check if DataFrames are exactly equal
        if df1.equals(df2):
            log_dq_info("The results match perfectly!")
            comparison_data.append({
                "Attribute": "Data Comparison",
                "Snowflake Procedure Output": "Exact Match",
                "SQL Server Procedure Output": "Exact Match",
                "Comparison": "Same"
            })
        else:
            log_dq_error("The results do not match!")
    
            # Find common columns for merging
            common_columns = df1.columns.intersection(df2.columns).tolist()
    
            # Perform an outer merge to detect differences
            merged_df = pd.merge(df1, df2, how='outer', indicator=True, on=common_columns)
    
            # Extract differing rows
            diff = merged_df[merged_df['_merge'] != 'both'].copy()
    
            # Handle categorical columns properly
            for col in diff.select_dtypes(['category']).columns:
                diff[col] = diff[col].astype('category')
                if 'NaN' not in diff[col].cat.categories:
                    diff[col] = diff[col].cat.add_categories(['NaN'])
            
            diff = diff.fillna('NaN')
    
            # Save differences to CSV
            diff.to_csv(f"Dq_analysis/{proc_snowflake}differences.csv", index=True)
    
            count_diff = len(diff)
            log_dq_info(f"Number of differences detected: {count_diff}")
    
            comparison_data.append({
                "Attribute": "Data Comparison",
                "Snowflake Procedure Output": count_diff,
                "SQL Server Procedure Output": count_diff,
                "Comparison": "Data mismatch detected"
            })

    
        # Log the results
        for row in comparison_data:
            log_dq_info(f"{row['Attribute']}: {row['Snowflake Procedure Output']} | {row['SQL Server Procedure Output']} | {row['Comparison']}")

        self.all_comparisons.extend(comparison_data)
    
        # Generate HTML Report
        # self.generate_comparison_html(comparison_data, output_html_file)
    
        return count_df1, count_df2
    



    def run(self, snowflake_proc, sqlserver_proc):
        # """Runs the procedures and compares the results."""
        # log_dq_info(f"Executing Snowflake procedure: {snowflake_proc}")
        # snowflake_result = self.execute_snowflake_procedure(snowflake_proc)
        
        # log_dq_info(f"Executing SQL Server procedure: {sqlserver_proc}")
        # sqlserver_result = self.execute_sqlserver_procedure(sqlserver_proc)
        
        # log_dq_info("Comparing results...")
        # # self.compare_results(snowflake_result, sqlserver_result)
        # self.compare_results(snowflake_result, sqlserver_result, snowflake_proc, sqlserver_proc)

        """Runs the procedures and compares the results."""
        log_dq_info(f"Executing Snowflake procedure: {snowflake_proc}")
        
        try:
            snowflake_result = self.execute_snowflake_procedure(snowflake_proc)
        except Exception as e:
            log_dq_error(f"Error executing Snowflake procedure {snowflake_proc}: {str(e)}")
            snowflake_result = pd.DataFrame()  # Assign an empty DataFrame to continue
        

        log_dq_info(f"Executing SQL Server procedure: {sqlserver_proc}")
        try:
            sqlserver_result = self.execute_sqlserver_procedure(sqlserver_proc)
        except Exception as e:
            log_dq_error(f"Error executing SQL Server procedure {sqlserver_proc}: {str(e)}")
            sqlserver_result = pd.DataFrame()  # Assign an empty DataFrame to continue
        
        log_dq_info("Comparing results...")
        self.compare_results(snowflake_result, sqlserver_result, snowflake_proc, sqlserver_proc)

