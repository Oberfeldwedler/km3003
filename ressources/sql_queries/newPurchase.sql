INSERT INTO purchases (product_id, user_id, price_then)
SELECT  '2', '3', products.sell_price
FROM    products
WHERE   products.product_id = '2';