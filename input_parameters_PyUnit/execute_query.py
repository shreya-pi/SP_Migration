from config import SQL_SERVER_CONFIG 
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import json



class ExecuteQuery:
    def execute_query(self,response_text, input_parameters,engine, sf_schema, stored_procedure):
        try:
            # Execute the query on SQL Server
            df = pd.read_sql(response_text, engine)
    
            # Display the top 5 rows
            print("Query Result (Top 5 rows):")
            print(df.head())
    
            # Ensure DataFrame is not empty and contains all input parameters
            if not df.empty and all(param in df.columns for param in input_parameters):
                # Pick a random row
                random_row = df.sample(n=1).iloc[0]
    
                # Extract values for the input parameters from the random row
                random_values = [str(random_row[param]) for param in input_parameters]
                joined_values = ", ".join(random_values)
    
                print(f"Randomly selected values for {input_parameters}: {joined_values}")
    
                call_statement = f"CALL {sf_schema}.{stored_procedure}({joined_values});"
                print("CALL Statement:", call_statement)
                return call_statement
            else:
                print(f"DataFrame missing required parameters or is empty.")
                return None
    
        except Exception as e:
            print("Error executing SQL query:", str(e))
            return None
    
    
    
    
    def run(self,response_text, input_parameters, file_name, call_statements,sf_schema,stored_procedure):
            password = quote_plus(SQL_SERVER_CONFIG['password'])
            # Create SQLAlchemy Engine for SQL Server Connection
            engine = create_engine(
                f"mssql+pyodbc://{SQL_SERVER_CONFIG['username']}:{password}@"
                f"{SQL_SERVER_CONFIG['server']}/{SQL_SERVER_CONFIG['database']}?driver={SQL_SERVER_CONFIG['driver'].replace(' ', '+')}",
                pool_size=10,
                max_overflow=20
            )
            #merge with execute query
            
            # # Execute the cleaned query and get the call statement
            call_statement = self.execute_query(response_text,input_parameters,engine,sf_schema,stored_procedure)
            
            # Append the call statement to the list
            call_statements.append(call_statement)
            # break  # Process only the first test case 
            
            
            # Export the accumulated call statements to a JSON file
            with open(file_name, "w", encoding="utf-8") as json_file:
                json.dump(call_statements, json_file, indent=4)
            
            # Close the database connection
            engine.dispose()
    
    
    
