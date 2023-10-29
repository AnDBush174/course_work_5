import psycopg2
import os
import json


class DBManager:
    """Класс для работы HeadHunter"""

    def __init__(self):
        self.conn = psycopg2.connect(host="localhost",
                                     database="HHBD",
                                     user=os.environ.get('PG_USER'),
                                     password=os.environ.get('PG_PASSWORD'),
                                     options="-c client_encoding=utf-8")

    def create_tables(self):
        """Создание таблиц"""
        query_1 = """
        CREATE TABLE IF NOT EXISTS Employers (
        employer_id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL)"""

        query_2 = """
        CREATE TABLE IF NOT EXISTS Vacancies (
        vacancy_id SERIAL PRIMARY KEY,
        employer_id INTEGER REFERENCES Employers (employer_id),
        title VARCHAR NOT NULL,
        description VARCHAR,
        salary INTEGER,
        url VARCHAR)"""

        for query in [query_1, query_2]:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                self.conn.commit()

    def fill_tables_from_files(self, file_path):
        """Заполнение таблиц файлов с вакансиями."""

        with open(f"src/data_json_employers/{file_path}", 'r', encoding="utf-8") as file:
            data = json.load(file)

            for vacancy in data.get("items", []):
                if vacancy.get("salary"):
                    salary = vacancy["salary"].get("from", 1)
                else:
                    salary = 1

                url = vacancy.get("apply_alternate_url", "")
                name_company = vacancy["employer"].get("name", "")
                name_vacancy = vacancy.get("name", "")
                vacancy_desc_1 = vacancy["snippet"].get("requirement", "")
                vacancy_desc_2 = vacancy["snippet"].get("responsibility", "")
                description = f"{vacancy_desc_1} {vacancy_desc_2}"

                with self.conn.cursor() as cursor:
                    cursor.execute("""
                                INSERT INTO Employers (name) 
                                SELECT %s
                                WHERE NOT EXISTS (
                                SELECT name 
                                FROM Employers
                                WHERE name = %s)
                                """, (name_company, name_company))
                    self.conn.commit()

                    cursor.execute("SELECT employer_id FROM employers ORDER BY employer_id DESC LIMIT 1")
                    employer_id = cursor.fetchone()

                    cursor.execute("""
                                INSERT INTO vacancies (employer_id, title, description, salary, url)
                                VALUES (%s, %s, %s, %s, %s)""",
                                   (employer_id[0], name_vacancy, description, salary, url))
                    self.conn.commit()

    def get_companies_and_vacancies_count(self):
        """Получает список всех компаний и количество вакансий у каждой компании."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.name, COUNT(v.vacancy_id)
                FROM employers e
                JOIN vacancies v ON e.employer_id = v.employer_id
                GROUP BY e.name
            """)
            data = cursor.fetchall()
            return data

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием названия компании,
         названия вакансии и зарплаты и ссылки на вакансию."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.name, v.title, v.salary, v.url
                FROM employers e
                JOIN vacancies v ON e.employer_id = v.employer_id
            """)
            data = cursor.fetchall()
            return data

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT AVG(salary)
                FROM vacancies
            """)
            data = cursor.fetchone()
            return data[0] if data else None

    def get_vacancies_with_higher_salary(self):
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        avg_salary = self.get_avg_salary()
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.name, v.title, v.salary, v.url
                FROM employers e
                JOIN vacancies v ON e.employer_id = v.employer_id
                WHERE v.salary > %s
            """, (avg_salary,))
            data = cursor.fetchall()
            return data

    def get_vacancies_with_keyword(self, keyword):
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова."""
        keyword = f"%{keyword}%"
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.name, v.title, v.salary, v.url
                FROM employers e
                JOIN vacancies v ON e.employer_id = v.employer_id
                WHERE v.title LIKE %s
            """, (keyword,))
            data = cursor.fetchall()
            return data

    def close_conn(self):
        self.conn.close()
