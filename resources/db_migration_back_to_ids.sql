INSERT INTO `km3003_dev`.users (first_name, last_name, current_balance, last_update, barcode)
SELECT 
    first_name,
    last_name,
    current_balance,
    last_update,
    barcode
FROM km3003.users;

INSERT INTO `km3003_dev`.`user-barcodes` (user_id, barcode)
SELECT 
    id,
    barcode
FROM `km3003_dev`.users;

INSERT INTO `km3003_dev`.products (barcode, brand, name, sell_price, buy_price, created, last_update)
SELECT 
    barcode,
    brand,
    name,
    sell_price,
    buy_price,
    created,
    last_update
FROM km3003.products;


INSERT INTO `km3003_dev`.deposits (date, amount, reason, user_id)
SELECT 
    km3003.deposits.date,
    km3003.deposits.amount,
    km3003.deposits.reason,
	`km3003_dev`.users.id AS user_id
FROM km3003.deposits
INNER JOIN `km3003_dev`.users 
	ON km3003.deposits.`user_barcode` = `km3003_dev`.users.barcode;


INSERT INTO `km3003_dev`.purchases (date, product_id, user_id, price_then)
SELECT 
    km3003.purchases.date,
    `km3003_dev`.products.id AS product_id,
	`km3003_dev`.users.id AS user_id,
	km3003.purchases.price_then
FROM km3003.purchases 
INNER JOIN `km3003_dev`.users ON km3003.purchases.user_barcode =`km3003_dev`.users.barcode
INNER JOIN `km3003_dev`.products ON km3003.purchases.product_barcode = `km3003_dev`.products.barcode;
