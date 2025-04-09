--** SSC-FDM-0007 - MISSING DEPENDENT OBJECT "sakila.rental" **
CREATE OR REPLACE PROCEDURE dbo.AddRental (CUSTOMER_ID INT, INVENTORY_ID INT, STAFF_ID INT)
RETURNS TABLE()
LANGUAGE SQL
COMMENT = '{ "origin": "sf_sc", "name": "snowconvert", "version": {  "major": 1,  "minor": 2,  "patch": "6.0" }, "attributes": {  "component": "transact",  "convertedOn": "03-19-2025",  "domain": "test" }}'
EXECUTE AS CALLER
AS
$$
    DECLARE
        RENTAL_ID INT;
        RENTAL_DATE TIMESTAMP_NTZ(3) := CURRENT_TIMESTAMP() :: TIMESTAMP;
        ProcedureResultSet RESULTSET;
    BEGIN
        !!!RESOLVE EWI!!! /*** SSC-EWI-0040 - THE STATEMENT IS NOT SUPPORTED IN SNOWFLAKE ***/!!!
        SET NOCOUNT ON;
         
         

        -- Insert rental record
        INSERT INTO sakila.rental (rental_date, inventory_id, customer_id, staff_id, return_date)
        VALUES (:RENTAL_DATE, :INVENTORY_ID, :CUSTOMER_ID, :STAFF_ID, NULL);
        -- Return the last inserted rental ID
        RENTAL_ID :=
        !!!RESOLVE EWI!!! /*** SSC-EWI-0073 - PENDING FUNCTIONAL EQUIVALENCE REVIEW FOR 'SCOPE_IDENTITY' NODE ***/!!!
        SCOPE_IDENTITY();
        ProcedureResultSet := (

        -- Return the new rental ID
        SELECT
            :RENTAL_ID AS NewRentalID);
        RETURN TABLE(ProcedureResultSet);
    END;
$$;