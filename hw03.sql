CREATE DATABASE pet_café;
USE pet_café;
CREATE TABLE animals (
    animal_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    species ENUM('Dog', 'Cat', 'Alpaca', 'Call Duck') NOT NULL,
    birth_year YEAR,
    is_available BOOLEAN DEFAULT TRUE,
    special_skills JSON COMMENT 'Store JSON array, e.g., ["High-five", "Play dead"]'
);
CREATE TABLE customers(
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    nickname VARCHAR(20) UNIQUE NOT NULL,
    membership_level ENUM('Bronze','Silver','Gold') DEFAULT 'Bronze',
    last_visit DATE,
    total_paws INT DEFAULT 0 COMMENT 'Accumulated paw stamps'
);
CREATE TABLE interactions(
    interaction_id INT PRIMARY KEY AUTO_INCREMENT,
    animal_id INT,
    customer_id INT,
    interaction_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    happiness_rating TINYINT CHECK (happiness_rating BETWEEN 1 AND 5),
    FOREIGN KEY (animal_id) REFERENCES animals(animal_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

INSERT INTO animals (name, species, birth_year, special_skills)
VALUES
('Latte', 'Cat', 2020, '["Kneading Dough", "High Wire Walking"]'),
('Mocha', 'Dog', 2019, '["Fetch Frisbee", "Sad Eyes"]'),
('Cappu', 'Alpaca', 2021, '["Head Nodding", "Tongue Tricks"]');

INSERT INTO customers (nickname, membership_level, last_visit) 
VALUES
('CatLover123', 'Gold', '2023-10-15'),
('DoggoAmbassador', 'Silver', NULL),
('AlpacaFanatic', 'Bronze', '2023-10-16');

INSERT INTO interactions (animal_id, customer_id, happiness_rating)
VALUES
(1, 1, 5),
(3, 3, 4),
(2, 1, 4),
(1, 3, 3);

ALTER TABLE animals ADD COLUMN weight_kg DECIMAL(5,2) COMMENT 'Track animal''s weight in kilograms';

DELETE FROM customers WHERE last_visit IS NULL AND total_paws = 0;

ALTER TABLE customers MODIFY nickname VARCHAR(50);

SET SQL_SAFE_UPDATES = 0;

SELECT name, birth_year 
FROM animals
WHERE species = 'Dog' 
  AND is_available = TRUE;
  
SELECT 
    name AS animal_name,
    JSON_CONTAINS(special_skills, '"Kneading Dough"') AS can_knead
FROM animals
WHERE species = 'Cat';

SELECT 
    a.name AS animal_name,
    COUNT(i.interaction_id) AS interaction_count
FROM animals a
LEFT JOIN interactions i ON a.animal_id = i.animal_id
WHERE DATE(i.interaction_time) = CURDATE()
GROUP BY a.animal_id
ORDER BY interaction_count DESC;