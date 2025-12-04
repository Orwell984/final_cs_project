CREATE DATABASE IF NOT EXISTS groceries;
USE groceries;

DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS dept;
DROP TABLE IF EXISTS origin;

CREATE TABLE IF NOT EXISTS dept (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS origin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(3) NOT NULL
);

INSERT INTO dept (name) VALUES
('Beverages'),
('Bread/Bakery'),
('Canned/Jarred Goods'),
('Dairy');

INSERT INTO origin (name) VALUES
('USA'),
('ARG'),
('MXN'),
('CAN');

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    dept_id INT NOT NULL,
    origin_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    FOREIGN KEY (dept_id) REFERENCES dept(id),
    FOREIGN KEY (origin_id) REFERENCES origin(id)
);


INSERT INTO products (name, dept_id, origin_id, price, stock) VALUES
('Milk', 4, 1, 2.99, 100),
('Bread', 2, 2, 1.99, 50),
('Canned Beans', 3, 3, 0.99, 200),
('Orange Juice', 1, 4, 3.49, 75);