CREATE DATABASE IF NOT EXISTS waka;
USE waka;

CREATE TABLE IF NOT EXISTS book (
    book_id VARCHAR(50) PRIMARY KEY,
    title NVARCHAR(255),
    category VARCHAR(50),
    thumb VARCHAR(200),
    author_id VARCHAR(50),
    author_name NVARCHAR(100)
);
CREATE TABLE IF NOT EXISTS reader (
    reader_id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(10) UNIQUE,
    username VARCHAR(50),
    password VARCHAR(50)
);
CREATE TABLE IF NOT EXISTS favorite (
    favorite_id INT AUTO_INCREMENT PRIMARY KEY,
    reader_id INT NOT NULL,
    book_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (reader_id) REFERENCES reader(reader_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id)
);