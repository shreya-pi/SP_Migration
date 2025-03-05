**Stored Procedure Extraction and Conversion Pipeline**
The pipeline is designed to facilitate the extraction and conversion of stored procedures from SQL Server to Snowflake. It consists of the following stages:

1. **Script Extraction and Generation**: 
    - Extract stored procedures from SQL Server.
    - Generate corresponding SQL scripts for the extracted procedures.

2. **Conversion to SnowScript**: 
    - Utilize SnowConvert to transform the SQL scripts into SnowScript, which is compatible with Snowflake.

3. **Pre-processing of Converted SnowScripts**: 
    - Perform necessary pre-processing steps on the converted SnowScripts to ensure they are optimized and ready for execution.

4. **PyUnit Testing**: 
    - Conduct PyUnit tests on the stored procedures to validate their functionality before executing them on Snowflake.

5. **Execution Testing**: 
    - Execute the newly created stored procedures on Snowflake.
    - Test for any runtime errors during execution to ensure smooth operation.

6. **Quality Testing**: 
    - Compare the output of the original SQL Server stored procedures with the Snowflake stored procedures.
    - Identify any discrepancies and export the differences to a CSV file for further analysis.

This structured approach ensures a seamless transition of stored procedures from SQL Server to Snowflake, maintaining their integrity and performance.