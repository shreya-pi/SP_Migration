#!/usr/bin/env python3
from config import SNOWFLAKE_CONFIG, SQL_SERVER_CONFIG
from .log import log_info
import pyodbc
import snowflake.connector
from datetime import datetime

# TARGET_TABLE = "procedures_metadata"

class CreateMetadataTable:
    def __init__(self, TARGET_TABLE):
        self.TARGET_TABLE = TARGET_TABLE

    def fetch_sqlserver_procedures(self):
        """Connects to SQL Server and returns a list of dicts with procedure metadata."""
        # cfg = SQL_SERVER_CONFIG
        sql_server_config = SQL_SERVER_CONFIG
    
        conn_str = f"DRIVER={sql_server_config['driver']};SERVER={sql_server_config['server']};DATABASE={sql_server_config['database']};UID={sql_server_config['username']};PWD={sql_server_config['password']}"
        cnxn = pyodbc.connect(conn_str)
        cursor = cnxn.cursor()
    
        # 1) Routines
        # Get all stored procedures
    
        cursor.execute("""
            SELECT 
              SPECIFIC_CATALOG AS dbname,
              SPECIFIC_SCHEMA  AS schema_name,
              SPECIFIC_NAME    AS procedure_name,
              ROUTINE_DEFINITION AS procedure_definition
            FROM INFORMATION_SCHEMA.ROUTINES
            WHERE ROUTINE_TYPE = 'PROCEDURE'
        """)
        procs = cursor.fetchall()
    
        # 2) Parameters 
        # Get all parameters for the stored procedures 
        cursor.execute("""
            SELECT
              SPECIFIC_NAME      AS procedure_name,
              PARAMETER_MODE     AS mode,
              PARAMETER_NAME     AS name,
              DATA_TYPE          AS data_type,
              CHARACTER_MAXIMUM_LENGTH AS char_length
            FROM INFORMATION_SCHEMA.PARAMETERS
            ORDER BY SPECIFIC_NAME, ORDINAL_POSITION
        """)
        params = cursor.fetchall()
    
        # Group params by proc name
        # Create a dictionary where the key is the procedure name and the value is a list of parameter descriptions
        params_by_proc = {}
        for p in params:
            desc = f"{p.mode} {p.name} {p.data_type}"
            if p.char_length is not None:
                desc += f"({p.char_length})"
            params_by_proc.setdefault(p.procedure_name, []).append(desc)
    
        # Build result
        # Create a list of dictionaries, each representing a procedure with its metadata and parameters
        rows = []
        for r in procs:
            pname = r.procedure_name
            rows.append({
                "SOURCE":               "SQLServer",
                "DBNAME":               r.dbname,
                "SCHEMA_NAME":          r.schema_name,
                "PROCEDURE_NAME":       pname,
                "PROCEDURE_DEFINITION": r.procedure_definition,
                "PARAMETERS":           ", ".join(params_by_proc.get(pname, [])),
            })
    
        cursor.close()
        cnxn.close()
        return rows
    

    #     """Connects to SQL Server and returns a list of dicts with procedure metadata."""
    def load_into_snowflake(self,proc_list):
        """Creates the target table if needed and bulk‐loads procedure metadata."""
        sf_cfg = SNOWFLAKE_CONFIG
        ctx = snowflake.connector.connect(
            user=sf_cfg['user'],
            password=sf_cfg['password'],
            account=sf_cfg['account'],
            warehouse=sf_cfg['warehouse'],
            database=sf_cfg['database'],
            schema=sf_cfg['schema']
        )
        cs = ctx.cursor()
    
        # create table
        # Check if the table already exists
        cs.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.TARGET_TABLE} (
          SOURCE                STRING,
          DBNAME                STRING,
          SCHEMA_NAME           STRING,
          PROCEDURE_NAME        STRING,
          PROCEDURE_DEFINITION  STRING,
          CONVERSION_FLAG       BOOLEAN,
          LOAD_TIMESTAMP        TIMESTAMP_NTZ(9),
          SNOWFLAKE_DBNAME      STRING,
          SNOWFLAKE_SCHEMA_NAME STRING,
          SNOWFLAKE_DDL         STRING,
          PARAMETERS            STRING,
          IS_DEPLOYED           BOOLEAN,
          ERRORS                STRING
        )
        """)
    
        insert_sql = f"""
        INSERT INTO {self.TARGET_TABLE} (
          SOURCE, DBNAME, SCHEMA_NAME, PROCEDURE_NAME, PROCEDURE_DEFINITION,
          CONVERSION_FLAG, LOAD_TIMESTAMP,
          SNOWFLAKE_DBNAME, SNOWFLAKE_SCHEMA_NAME, SNOWFLAKE_DDL,
          PARAMETERS, IS_DEPLOYED, ERRORS
        ) VALUES (
          %s, %s, %s, %s, %s,
          %s, CURRENT_TIMESTAMP(),
          %s, %s, %s,
          %s, %s, %s
        )
        """
    
        for p in proc_list:
            cs.execute(insert_sql, (
                p["SOURCE"],
                p["DBNAME"],
                p["SCHEMA_NAME"],
                p["PROCEDURE_NAME"],
                p["PROCEDURE_DEFINITION"],
                False,                      # CONVERSION_FLAG
                sf_cfg['database'],         # SNOWFLAKE_DBNAME
                sf_cfg['schema'],           # SNOWFLAKE_SCHEMA_NAME
                "",                         # SNOWFLAKE_DDL placeholder
                p["PARAMETERS"],
                False,                       # IS_DEPLOYED
                ""                          # ERRORS
            ))
    
        ctx.commit()
        cs.close()
        ctx.close()
    
    
    def create_metadata_table(self):
        log_info("🔍 Fetching procedures from SQL Server…")
        procs = self.fetch_sqlserver_procedures()
        log_info(f"   → {len(procs)} procedures found.")
    
        log_info("⏫ Loading metadata into Snowflake…")
        self.load_into_snowflake(procs)
        log_info("✅ Done.")
    
    # if __name__ == "__main__":
    #     main()
    
    
    