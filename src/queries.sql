-- Создаем базу данных "HHBD"
CREATE DATABASE HHBD;

-- Подключаемся к базе данных "HHBD"
\c HHBD

-- Создаем таблицы "Employers" и "Vacancies"
CREATE TABLE IF NOT EXISTS Employers (
    employer_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Vacancies (
    vacancy_id SERIAL PRIMARY KEY,
    employer_id INT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    salary DECIMAL(10,2),
    url VARCHAR(255),
    FOREIGN KEY (employer_id) REFERENCES Employers(employer_id)
);