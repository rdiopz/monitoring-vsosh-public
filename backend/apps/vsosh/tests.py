from datetime import date

from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.account.models import UserAccount, UserRole
from apps.vsosh.models import (
    EducationInstitution,
    Municipality,
    OlympiadParticipation,
    Participant,
    Subject,
)
from apps.vsosh.queries.participants import extract_name_and_birth_date


class VSOSHBaseAPITestCase(APITestCase):
    """Базовый класс с авторизацией и тестовыми данными"""

    def setUp(self):
        self.role, _ = UserRole.objects.get_or_create(name="Администратор")

        self.user, _ = UserAccount.objects.get_or_create(
            email="test@example.com",
            defaults={
                "role": self.role,
                "password_hash": make_password("testpass123"),
                "is_active": True,
            },
        )

        self.client.force_authenticate(user=self.user)

        self.municipality, _ = Municipality.objects.get_or_create(name="Великий Новгород")

        self.subject, _ = Subject.objects.get_or_create(
            full_name="Математика",
            defaults={"short_name": "Мат."},
        )

        self.education, _ = EducationInstitution.objects.get_or_create(
            full_name="Гимназия №1",
            municipality=self.municipality,
            defaults={"short_name": "Гимн.1"},
        )

        self.participant, _ = Participant.objects.get_or_create(
            lastname="Иванов",
            firstname="Иван",
            patronymic="Иванович",
            birth_date=date(2010, 5, 15),
            defaults={"gender": "М"},
        )

        self.participation, _ = OlympiadParticipation.objects.get_or_create(
            participant=self.participant,
            education=self.education,
            subject=self.subject,
            stage="РЭ",
            year=2024,
            defaults={
                "class_field": 9,
                "status": "победитель",
            },
        )

    def make_csv_file(self, name: str, content: str) -> SimpleUploadedFile:
        """Создаёт CSV-файл в памяти"""
        return SimpleUploadedFile(
            name=name,
            content=content.encode("utf-8"),
            content_type="text/csv",
        )


# =====================================================
# Авторизация
# =====================================================


class AuthenticationTests(APITestCase):
    """Проверка доступа без авторизации"""

    def test_dashboard_requires_auth(self):
        """Дашборд недоступен без авторизации"""
        response = self.client.get("/api/vsosh/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reports_require_auth(self):
        """Отчёты недоступны без авторизации"""
        response = self.client.get("/api/vsosh/reports/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_participations_require_auth(self):
        """Участия в олимпиаде недоступны без авторизации"""
        response = self.client.get("/api/vsosh/olympiad-participation/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# =====================================================
# Дашборд
# =====================================================


class DashboardTests(VSOSHBaseAPITestCase):
    """Тесты аналитического дашборда"""

    def test_dashboard_returns_data(self):
        """Общий дашборд возвращает основные секции"""
        response = self.client.get("/api/vsosh/dashboard/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertIn("by_stage", response.data)
        self.assertIn("by_year", response.data)
        self.assertIn("by_subject", response.data)
        self.assertIn("by_municipality", response.data)
        self.assertIn("by_class", response.data)
        self.assertIn("by_status", response.data)
        self.assertIn("by_gender", response.data)

    def test_dashboard_filters_work(self):
        """Фильтр по году и этапу работает корректно"""
        response = self.client.get(
            "/api/vsosh/dashboard/",
            {"year": 2024, "stage": "РЭ"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["summary"]["total_participations"], 1)

    def test_participant_dashboard_returns_data(self):
        """Дашборд участника возвращает аналитику по участнику"""
        response = self.client.get(
            f"/api/vsosh/dashboard/participants/{self.participant.participant_id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("participant", response.data)
        self.assertIn("summary", response.data)
        self.assertIn("by_year", response.data)
        self.assertIn("by_stage", response.data)
        self.assertIn("by_subject", response.data)
        self.assertIn("by_status", response.data)
        self.assertIn("participations", response.data)


# =====================================================
# Отчёты
# =====================================================


class ReportsTests(VSOSHBaseAPITestCase):
    """Тесты отчётов"""

    def test_reports_list_returns_reports(self):
        """Список отчётов возвращается корректно"""
        response = self.client.get("/api/vsosh/reports/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 6)

        first = response.data[0]
        self.assertIn("key", first)
        self.assertIn("title", first)
        self.assertIn("description", first)
        self.assertIn("filename", first)

    def test_stage_year_report_returns_excel(self):
        """Отчёт по этапам и годам возвращает Excel"""
        response = self.client.get("/api/vsosh/reports/stage_year/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_rating_report_returns_excel(self):
        """Рейтинг обучающихся возвращает Excel"""
        response = self.client.get("/api/vsosh/reports/rating/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# =====================================================
# Экспорт
# =====================================================


class ExportTests(VSOSHBaseAPITestCase):
    """Тесты экспорта данных в Excel"""

    def test_export_participations_returns_excel(self):
        """Экспорт участий возвращает Excel"""
        response = self.client.get(
            "/api/vsosh/olympiad-participation/export/",
            {"columns": ["olymp_id", "participant_full_name", "year"]},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_export_participants_returns_excel(self):
        """Экспорт участников возвращает Excel"""
        response = self.client.get(
            "/api/vsosh/participant/export/",
            {"columns": ["participant_id", "lastname", "birth_date"]},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# =====================================================
# Импорт
# =====================================================


class ImportTests(VSOSHBaseAPITestCase):
    """Тесты импорта данных из CSV"""

    def test_import_municipalities_creates_records(self):
        """Импорт муниципалитетов из CSV создаёт записи"""
        file = self.make_csv_file(
            "municipalities.csv",
            "Название\nБоровичи\nСтарая Русса\n",
        )

        response = self.client.post(
            "/api/vsosh/municipality/import_data/",
            {"file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Municipality.objects.filter(name="Боровичи").exists())

    def test_import_participants_creates_records(self):
        """Импорт участников из CSV создаёт записи"""
        file = self.make_csv_file(
            "participants.csv",
            "Фамилия,Имя,Дата рождения,Пол\nПетров,Пётр,20.03.2011,М\n",
        )

        response = self.client.post(
            "/api/vsosh/participant/import_data/",
            {"file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Participant.objects.filter(
                lastname="Петров",
                firstname="Пётр",
            ).exists()
        )

    def test_import_participations_creates_records(self):
        """Импорт участий создаёт запись по существующим справочникам"""
        file = self.make_csv_file(
            "participations.csv",
            (
                "Фамилия,Имя,Пол,Дата рождения,Муниципалитет,"
                "ОУ,Предмет,Класс,Этап,Статус,Год\n"
                "Сидоров,Алексей,М,10.01.2011,Великий Новгород,"
                "Гимназия №1,Математика,8,МЭ,участник,2025\n"
            ),
        )

        response = self.client.post(
            "/api/vsosh/olympiad-participation/import_data/",
            {"file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            OlympiadParticipation.objects.filter(
                year=2025,
                stage="МЭ",
                status="участник",
            ).exists()
        )

    def test_import_without_file_returns_error(self):
        """Импорт без файла возвращает 400"""
        response = self.client.post(
            "/api/vsosh/municipality/import_data/",
            {},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# =====================================================
# Поиск участника
# =====================================================


class SearchTests(VSOSHBaseAPITestCase):
    """Тесты API поиска участников"""

    def test_search_returns_participant(self):
        """Поиск по ФИО и дате возвращает результат"""
        response = self.client.get(
            "/api/vsosh/participant/search/",
            {
                "q": "Иванов Иван Иванович 15.05.2010",
                "limit": 10,
                "offset": 0,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertGreaterEqual(len(response.data["results"]), 1)


class SearchParserTests(TestCase):
    """Тесты парсера строки поиска"""

    def test_parse_full_name_and_date(self):
        """ФИО и дата рождения корректно выделяются из строки"""
        name, birth_date = extract_name_and_birth_date("Иванов Иван Иванович 15.05.2010")

        self.assertEqual(name, "Иванов Иван Иванович")
        self.assertEqual(birth_date, date(2010, 5, 15))

    def test_parse_name_without_date(self):
        """Строка без даты — только имя"""
        name, birth_date = extract_name_and_birth_date("Иванов")

        self.assertEqual(name, "Иванов")
        self.assertIsNone(birth_date)

    def test_parse_date_only(self):
        """Строка только с датой — имя пустое"""
        name, birth_date = extract_name_and_birth_date("15.05.2010")

        self.assertEqual(name, "")
        self.assertEqual(birth_date, date(2010, 5, 15))


# python manage.py test apps.vsosh --settings=config.settings_test -v 2
# redis-server.exe
