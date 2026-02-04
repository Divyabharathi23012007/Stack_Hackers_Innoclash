-- schema.sql
-- Database schema for Water Level Prediction System

CREATE DATABASE IF NOT EXISTS waterlevel_db;
USE waterlevel_db;

-- ---------------- USERS ----------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('civilian', 'farmer', 'authority') NOT NULL
);

-- ---------------- BOREWELLS ----------------
CREATE TABLE IF NOT EXISTS borewells (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ---------------- USER SETTINGS ----------------
CREATE TABLE IF NOT EXISTS settings (
    user_id INT PRIMARY KEY,
    threshold DOUBLE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
