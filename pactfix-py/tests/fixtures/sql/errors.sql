-- SQL Error Fixture - 10+ different error types

-- SQL001: SELECT *
SELECT * FROM users;
SELECT * FROM orders WHERE status = 'active';

-- SQL003: UPDATE/DELETE without WHERE
UPDATE users SET status = 'inactive';
DELETE FROM logs;
DELETE FROM temp_data;

-- SQL004: DROP without IF EXISTS
DROP TABLE users;
DROP TABLE orders;
DROP INDEX idx_users_email;

-- SQL005: CREATE without IF NOT EXISTS
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT
);

-- SQL007: GRANT ALL
GRANT ALL ON database.* TO 'user'@'localhost';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%';

-- SQL008: Plain text password
CREATE USER 'app'@'localhost' IDENTIFIED BY 'password123';
ALTER USER 'admin' PASSWORD = 'secret456';

-- Additional issues:

-- No indexes on frequently queried columns
CREATE TABLE products (
    id INT,
    name VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10,2)
);

-- Missing foreign key constraints
CREATE TABLE order_items (
    id INT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT
);

-- Using deprecated syntax
SELECT * FROM users, orders WHERE users.id = orders.user_id;

-- N+1 query pattern (simulated)
SELECT * FROM users;
-- Then for each user:
SELECT * FROM orders WHERE user_id = 1;
SELECT * FROM orders WHERE user_id = 2;

-- Missing transaction for related operations
INSERT INTO orders (user_id, total) VALUES (1, 100);
INSERT INTO order_items (order_id, product_id) VALUES (1, 1);
UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 1;
