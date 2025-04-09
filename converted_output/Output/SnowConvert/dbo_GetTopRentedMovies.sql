--** SSC-FDM-0007 - MISSING DEPENDENT OBJECTS "sakila.rental", "sakila.inventory", "sakila.film" **
CREATE OR REPLACE PROCEDURE dbo.GetTopRentedMovies ()
RETURNS TABLE()
LANGUAGE SQL
COMMENT = '{ "origin": "sf_sc", "name": "snowconvert", "version": {  "major": 1,  "minor": 2,  "patch": "6.0" }, "attributes": {  "component": "transact",  "convertedOn": "03-19-2025",  "domain": "test" }}'
EXECUTE AS CALLER
AS
$$
    DECLARE
        ProcedureResultSet RESULTSET;
    BEGIN
        !!!RESOLVE EWI!!! /*** SSC-EWI-0040 - THE STATEMENT IS NOT SUPPORTED IN SNOWFLAKE ***/!!!
        SET NOCOUNT ON;
        ProcedureResultSet := (
        SELECT TOP 10
            f.film_id,
            f.title,
            COUNT(r.rental_id) AS total_rentals
        FROM
            sakila.rental r
        INNER JOIN
                sakila.inventory i
                ON r.inventory_id = i.inventory_id
        INNER JOIN
                sakila.film f
                ON i.film_id = f.film_id
        GROUP BY
            f.film_id,
            f.title
        ORDER BY total_rentals DESC);
        RETURN TABLE(ProcedureResultSet);
    END;
$$;