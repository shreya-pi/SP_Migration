**Stored Procedure Extraction and Conversion Pipeline**

It consists of the following stages:-
1) Script extraction and generation from SQL server
2) Converting them to SnowScript using SnowConvert
3) Performing some pre-processing on the converted Snowscripts 
4) Performing PyUnit testing on the Stored procedures, before executing them on Snowflake
5) Testing the execution of the newly created stored procedures for runtime errors
6) Quality testing of the stored procedures, that performs comparison of the output of both(SQL SP vs Snowflake SP) and finally exports the differences to a csv file