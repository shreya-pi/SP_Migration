CREATE PROCEDURE [dbo].[GetCustomerRentals]
    @customer_id INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT r.rental_id, f.title AS film_title, r.rental_date, r.return_date
    FROM dbo.rental r
    INNER JOIN dbo.inventory i ON r.inventory_id = i.inventory_id
    INNER JOIN dbo.film f ON i.film_id = f.film_id
    WHERE r.customer_id = @customer_id
    ORDER BY r.rental_date DESC;
END;
