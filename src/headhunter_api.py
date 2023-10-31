import requests
import json
import os
import argparse


class HeadHunter:
    """Класс для работы с HeadHunter"""

    _api_link = "https://api.hh.ru/vacancies"
    _employer_ids = [6, 80, 1057, 1373, 2180, 2180, 3529, 4181, 15478, 23427]
    _search_word = "python"

    def __init__(self):
        self.session = requests.Session()

    def __str__(self):
        return "headhunter.ru"

    @staticmethod
    def printj(data_dict) -> None:
        """Выводит словарь в json-подобном удобном формате с отступами (Для разработки)"""
        print(json.dumps(data_dict, indent=2, ensure_ascii=False))

    def get_vacancies_api(self, **kwargs):
        """
        :param kwargs:
        text - Поисковый запрос
        employer_id - id компании. Указывать фактические идентификаторы компаний, разделенные запятыми.
        'employer_id':6, 80, 1057, 1373, 2180, 2180, 3529, 4181, 15478, 23427"
        per_page - Количество вакансий на странице
        """

        params = kwargs
        response = self.session.get(self._api_link, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print("Ошибка при выполнении запроса:", response.status_code)
            return None

    def get_company_name(self, employer_id):
        """Получение названия компании по ее идентификатору"""
        try:
            response = self.session.get(f"https://api.hh.ru/employers/{employer_id}")
            response.raise_for_status()
            data = response.json()
            return data.get("name", None)
        except requests.exceptions.RequestException as e:
            print("Ошибка при получении названия компании:", e)
            return None

    def get_json_files(self):
        """Сохранить JSON-файлы указанных компаний и компаний, содержащих ключевое слово"""
        employer_ids = self._employer_ids.copy()
        for employer_id in employer_ids:
            company_name = self.get_company_name(employer_id)
            if company_name is not None:
                file_path = os.path.join("src/data_json_employers", f"{employer_id}.json")
                with open(file_path, 'w', encoding="utf-8") as f:
                    json.dump({"название": company_name}, f, ensure_ascii=False, indent=2)
            employer_ids.remove(employer_id)  # Удаление идентификатора работодателя, чтобы избежать повторной обработки

        vacancies_data = self.get_vacancies_api(text=self._search_word, per_page=50)
        vacancy_file_path = os.path.join("src/data_json_employers", "вакансии.json")
        with open(vacancy_file_path, 'w', encoding="utf-8") as f:
            json.dump(vacancies_data, f, ensure_ascii=False, indent=2)


hh = HeadHunter()

# Добавление вакансии по запросу "python"
vacancies_data = hh.get_vacancies_api(text="python", area=1, per_page=50)
file_path = os.path.join("src/data_json_employers", "vacancy.json")
with open(file_path, 'w', encoding="utf-8") as file:
    json.dump(vacancies_data, file, ensure_ascii=False, indent=2)
# Создание парсера аргументов командной строки
parser = argparse.ArgumentParser(description="Программа для работы с вакансиями")

# Добавление аргументов
parser.add_argument("--employer_ids", nargs="+", type=int, help="Список идентификаторов компаний")
parser.add_argument("--per_page", type=int, help="Количество вакансий на странице")

# Парсинг аргументов
args = parser.parse_args()

# Получение значений аргументов
employer_ids = args.employer_ids
per_page = args.per_page

# Ввод запроса от пользователя
search_query = input("Введите поисковый запрос: ")

# Создание экземпляра класса HeadHunter
hh = HeadHunter()

# Проверка аргументов и выполнение соответствующих действий
if search_query:
    vacancies_data = hh.get_vacancies_api(text=search_query, per_page=per_page)
    file_path = os.path.join("src/data_json_employers", "vacancy.json")
    with open(file_path, 'w', encoding="utf-8") as file:
        json.dump(vacancies_data, file, ensure_ascii=False, indent=2)

if employer_ids:
    for employer_id in employer_ids:
        company_name = hh.get_company_name(employer_id)
        if company_name is not None:
            file_path = os.path.join("src/data_json_employers", f"{employer_id}.json")
            with open(file_path, 'w', encoding="utf-8") as f:
                json.dump({"название": company_name}, f, ensure_ascii=False, indent=2)

# Получение информации о вакансиях и сохранение в файл
hh.get_json_files()