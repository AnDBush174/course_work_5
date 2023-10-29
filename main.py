import psycopg2
import os
from src.db_manager import DBManager
from src.headhunter_api import HeadHunter

if __name__ == "__main__":
    # Создаем экземпляр менеджера базы данных
    db_manager = DBManager()
    # Создаем таблицы в базе данных, если они еще не существуют
    db_manager.create_tables()

    # Создаем объект для работы с HeadHunter API
    hh = HeadHunter()
    # Получаем JSON файлы с данными о вакансиях и работодателях
    hh.get_json_files()

    i = 1
    # Обходим все файлы в директории 'src/data_json_employers'
    for file in os.listdir("src/data_json_employers"):
        # Заполняем таблицы базы данных данными из файлов
        db_manager.fill_tables_from_files(file)
        print(file, "ОК", i)
        i += 1

    print()
    # Выводим информацию о компаниях и количестве вакансий
    print(db_manager.get_companies_and_vacancies_count())

    print()
    # Выводим вакансии, содержащие ключевое слово 'python'
    print(db_manager.get_vacancies_with_keyword("python"))

    # Закрываем соединение с базой данных
    db_manager.close_conn()
