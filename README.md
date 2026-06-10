# Мониторинг ВсОШ

Данный репозиторий содержит исходный код веб-системы, предназначенной для автоматизации учёта и анализа участия обучающихся Новгородской области в этапах Всероссийской олимпиады школьников. Проект выполнен в рамках выпускной квалификационной работы.

Система реализована в виде клиент-серверного веб-приложения. Серверная часть предоставляет REST API для работы с данными, клиентская часть — одностраничное приложение (SPA) с интерактивным интерфейсом.

Стек технологий:

- клиентская часть: Vue 3, Pinia, Vue Router, Vite, ECharts;
- серверная часть: Python, Django, Django REST Framework, Celery;
- база данных: PostgreSQL;
- кеширование и очереди задач: Redis;
- развёртывание: Docker, Docker Compose, Nginx.

Инструкция по запуску:

- установите Docker и Docker Compose;
- скопируйте файл .env.production.example (backend) в .env с актуальными значениями;
- выполните docker compose build && docker compose up.

Для запуска в режиме разработки:

```bash
# Установка зависимостей
cd frontend && npm install
cd ../backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt

# Запуск Redis
docker run -d --name redis -p 6379:6379 redis:alpine

# Запуск серверной части
cd backend && python manage.py runserver

# Запуск клиентской части
cd frontend && npm run dev

# Запуск Celery (в отдельных терминалах)
cd backend
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
```

Для запуска тестов:

```bash
cd backend
python manage.py test apps.vsosh --settings=config.settings_test -v 2
