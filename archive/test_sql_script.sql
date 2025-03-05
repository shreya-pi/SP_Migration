SET ANSI_NULLS ON
SET QUOTED_IDENTIFIER ON
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[GetStoreRevenue]') AND type in (N'P', N'PC'))
BEGIN
EXEC dbo.sp_executesql @statement = N'CREATE PROCEDURE [dbo].[GetStoreRevenue] AS' 
END
ALTER PROCEDURE [dbo].[GetStoreRevenue]
    @store_id INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT s.store_id, SUM(p.amount) AS total_revenue
    FROM sakila.payment p
    INNER JOIN sakila.rental r ON p.rental_id = r.rental_id
    INNER JOIN sakila.staff st ON p.staff_id = st.staff_id
    INNER JOIN sakila.store s ON st.store_id = s.store_id
    WHERE s.store_id = @store_id
    GROUP BY s.store_id;
END;
