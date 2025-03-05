




CREATE OR REPLACE PROCEDURE TESTSCHEMA_MG.GetInactiveCustomers ()
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
            c."customer_id",
            c."first_name",
            c."last_name",
            MAX(r."rental_date") AS last_rental_date
        FROM
            MYSQL_customer c
        LEFT JOIN
                MYSQL_rental r
                ON c."customer_id" = r."customer_id"
        GROUP BY
            c."customer_id",
            c."first_name",
            c."last_name"
        HAVING
            MAX(r."rental_date") < DATEADD(MONTH, -6, CURRENT_TIMESTAMP() :: TIMESTAMP)
            OR MAX(r."rental_date") IS NULL);
        RETURN TABLE(ProcedureResultSet);
    END;
$$;