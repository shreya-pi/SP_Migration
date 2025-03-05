--/****** Object:  StoredProcedure [dbo].[GetInactiveCustomers]    Script Date: 25-02-2025 13:33:36 ******/
----** SSC-FDM-TS0027 - SET ANSI_NULLS ON STATEMENT MAY HAVE A DIFFERENT BEHAVIOR IN SNOWFLAKE **
--SET ANSI_NULLS ON

!!!RESOLVE EWI!!! /*** SSC-EWI-0040 - THE STATEMENT IS NOT SUPPORTED IN SNOWFLAKE ***/!!!
SET QUOTED_IDENTIFIER ON;

CREATE OR REPLACE PROCEDURE dbo.GetInactiveCustomers ()
RETURNS TABLE()
LANGUAGE SQL
COMMENT = '{ "origin": "sf_sc", "name": "snowconvert", "version": {  "major": 1,  "minor": 2,  "patch": "5.0" }, "attributes": {  "component": "transact",  "convertedOn": "02-25-2025",  "domain": "tulapi" }}'
EXECUTE AS CALLER
AS
$$
    DECLARE
        ProcedureResultSet RESULTSET;
    BEGIN
        !!!RESOLVE EWI!!! /*** SSC-EWI-0040 - THE STATEMENT IS NOT SUPPORTED IN SNOWFLAKE ***/!!!
        SET NOCOUNT ON;
        ProcedureResultSet := (
        SELECT
            c.customer_id,
            c.first_name,
            c.last_name,
            MAX(r.rental_date) AS last_rental_date
        FROM
            sakila.customer c
        LEFT JOIN
                sakila.rental r
                ON c.customer_id = r.customer_id
        GROUP BY
            c.customer_id,
            c.first_name,
            c.last_name
        HAVING
            MAX(r.rental_date) < DATEADD(MONTH, -6, CURRENT_TIMESTAMP() :: TIMESTAMP)
            OR MAX(r.rental_date) IS NULL);
        RETURN TABLE(ProcedureResultSet);
    END;
$$;