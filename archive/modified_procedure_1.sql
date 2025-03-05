--/****** Object:  StoredProcedure [dbo].[GetCustomerRentals]    Script Date: 25-02-2025 13:33:36 ******/
----** SSC-FDM-TS0027 - SET ANSI_NULLS ON STATEMENT MAY HAVE A DIFFERENT BEHAVIOR IN SNOWFLAKE **
--SET ANSI_NULLS ON



CREATE OR REPLACE PROCEDURE TESTSCHEMA_MG.GetCustomerRentals (CUSTOMER_ID INT)
RETURNS TABLE()
LANGUAGE SQL
COMMENT = '{ "origin": "sf_sc", "name": "snowconvert", "version": {  "major": 1,  "minor": 2,  "patch": "5.0" }, "attributes": {  "component": "transact",  "convertedOn": "02-25-2025",  "domain": "tulapi" }}'
EXECUTE AS CALLER
AS
$$
    DECLARE
        ProcedureResultSet RESULTSET;
    BEGIN
        ProcedureResultSet := (
        SELECT
            r."rental_id",
            f."title" AS film_title,
            r."rental_date",
            r."return_date"
        FROM
            MYSQL_RENTAL r
        INNER JOIN
                MYSQL_INVENTORY i
                ON r."inventory_id" = i."inventory_id"
        INNER JOIN
                MYSQL_FILM f
                ON i."film_id" = f."film_id"
        WHERE
            r."customer_id" = :CUSTOMER_ID
        ORDER BY r."rental_date" DESC);
        RETURN TABLE(ProcedureResultSet);
    END;
$$;