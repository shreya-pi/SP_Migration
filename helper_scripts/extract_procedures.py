import os
from snowflake.connector import connect, DictCursor
from config import SNOWFLAKE_CONFIG  # import your Snowflake config
from .log import log_info, log_error

# Constants
# OUTPUT_DIR = "./extracted_procedures"

class ExtractProcedures:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        
        # 1. Ensure the output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # 2. Connect to Snowflake using config
        self.ctx = connect(
            user=SNOWFLAKE_CONFIG['user'],
            password=SNOWFLAKE_CONFIG['password'],
            account=SNOWFLAKE_CONFIG['account'],
            warehouse=SNOWFLAKE_CONFIG['warehouse'],
            database=SNOWFLAKE_CONFIG['database'],
            schema=SNOWFLAKE_CONFIG['schema'],
        )
        self.cs = self.ctx.cursor(DictCursor)

    def extract_procedures(self):
        try:
            # 3. Query for procedures where CONVERSION_FLAG is TRUE
            self.cs.execute("""
                SELECT 
                    PROCEDURE_NAME, 
                    PROCEDURE_DEFINITION 
                FROM PROCEDURES_METADATA 
                WHERE CONVERSION_FLAG = TRUE
            """)
            rows = self.cs.fetchall()
            # 4. Write each procedure to a .sql file        
            for row in rows:
                proc_name = row["PROCEDURE_NAME"]
                definition = row["PROCEDURE_DEFINITION"]
        
                # Replace special characters in filename
                safe_name = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in proc_name)
                file_path = os.path.join(self.output_dir, f"{safe_name}.sql")
        
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(definition.strip() + "\n")
        
                log_info(f"Wrote {proc_name} → {file_path}")
                self.cs = self.ctx.cursor(DictCursor)
    
        # 5. Close the cursor and connection
        finally:
            self.cs.close()    
            self.ctx.close() 
        
    










