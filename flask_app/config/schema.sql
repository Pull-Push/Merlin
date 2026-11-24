-- Merlin database schema
-- Reconstructed from the columns the User model reads and writes
-- (id, username, email, password, dateCreated, dateUpdated).
-- If you have an original .sql dump, compare it against this before using.

CREATE DATABASE IF NOT EXISTS merlin_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE merlin_db;

CREATE TABLE IF NOT EXISTS users (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    -- bcrypt hashes are 60 chars; 255 leaves room to change algorithms later
    password    VARCHAR(255) NOT NULL,
    dateCreated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dateUpdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);