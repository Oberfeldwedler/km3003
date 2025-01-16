INSERT INTO `km3003_database-normalization`.users (barcode, first_name, last_name, current_balance, created, last_update)
SELECT 
    barcode,
    SUBSTRING_INDEX(name, ' ', 1) AS first_name,
    SUBSTRING_INDEX(name, ' ', 2) AS last_name,
    current_balance,
    created,
    last_update
FROM km3003.users;

INSERT INTO `km3003_database-normalization`.products (barcode, brand, name, sell_price, buy_price, created, last_update)
SELECT 
    barcode,
    SUBSTRING_INDEX(name, ' ', 1) AS brand,
    SUBSTRING_INDEX(name, ' ', -1) AS name,
    sell_price,
    buy_price,
    created,
    last_update
FROM km3003.products;

INSERT INTO `km3003_database-normalization`.purchases (date, product_barcode, user_barcode, price_then)
SELECT 
    km3003.purchases.date,
    km3003.products.barcode AS product_barcode,
	km3003.users.barcode AS user_barcode,
	km3003.purchases.price_then
FROM km3003.purchases 
INNER JOIN km3003.users ON km3003.purchases.user_id=km3003.users.id
INNER JOIN km3003.products ON km3003.purchases.product_id=km3003.products.id;

INSERT INTO `km3003_database-normalization`.deposits (date, amount, reason, user_barcode)
SELECT 
    km3003.deposits.date,
	km3003.deposits.amount,
    km3003.deposits.reason,
	km3003.users.barcode AS user_barcode
FROM km3003.deposits
INNER JOIN km3003.users ON km3003.deposits.user_id=km3003.users.id


INSERT INTO `km3003_dev`.`user-barcodes` (barcode, user_id)
SELECT
	barcode,
    id
FROM `km3003_dev`.`users`