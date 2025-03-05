ALTER PROCEDURE [dbo].[GetTopRentedMovies]
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP 10 f.film_id, f.title, COUNT(r.rental_id) AS total_rentals
    FROM sakila.rental r
    INNER JOIN sakila.inventory i ON r.inventory_id = i.inventory_id
    INNER JOIN sakila.film f ON i.film_id = f.film_id
    GROUP BY f.film_id, f.title
    ORDER BY total_rentals DESC;
END;

