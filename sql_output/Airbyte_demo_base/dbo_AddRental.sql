ALTER PROCEDURE [dbo].[AddRental]
    @customer_id INT,
    @inventory_id INT,
    @staff_id INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @rental_id INT;
    DECLARE @rental_date DATETIME = GETDATE();

    -- Insert rental record
    INSERT INTO sakila.rental (rental_date, inventory_id, customer_id, staff_id, return_date)
    VALUES (@rental_date, @inventory_id, @customer_id, @staff_id, NULL);

    -- Return the last inserted rental ID
    SET @rental_id = SCOPE_IDENTITY();

    -- Return the new rental ID
    SELECT @rental_id AS NewRentalID;
END;
