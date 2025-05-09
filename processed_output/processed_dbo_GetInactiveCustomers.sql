
CREATE OR REPLACE PROCEDURE DB_SCHEMA.GetInactiveCustomers ()
RETURNS TABLE()
LANGUAGE SQL
COMMENT = '{ "origin": "sf_sc", "name": "snowconvert", "version": {  "major": 1,  "minor": 2,  "patch": "6.0" }, "attributes": {  "component": "transact",  "convertedOn": "03-19-2025",  "domain": "test" }}'
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