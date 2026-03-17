# 🗺️ KuMap: Система навигации внутри зданий
Проект по созданию интерактивных карт и поиску кратчайших путей внутри помещений (учебных корпусов) с учетом этажности и препятствий.

## 🚀 KuMap Update:

- Закинул рабочую логику навигации в backend/app/services/pathfinder.py.

- Теперь можно тестить маршруты в Swagger: POST /calculate-path.

- Пока работаем на JSON (пример данных в tests/map_data.json), параллельно готовлю переезд на PostGIS (модели уже в models/).

- Для запуска: uvicorn app.main:app --reload из папки backend.

## 🛠 Стек технологий
- **Backend:** FastAPI, SQLModel (ORM), PostGIS (Гео-БД), NetworkX (Алгоритмы графов).

- **Frontend:** Next.js (App Router), MapLibre GL JS (Карты), Tailwind CSS.

- **DevOps:** Docker Compose (PostgreSQL 16 + PostGIS)

## 🚀 Быстрый старт (для разработчиков)
1. Клонирование и подготовка
```bash
git clone https://github.com/Bu88lleGum/ku-map
cd kumap
```
2. Запуск базы данных (Docker)
Убедитесь, что Docker Desktop запущен. Из корня проекта выполните:
```bash
docker-compose up -d
```
Важно: База доступна на порту 5434. Пароль: qwerty.
3. Настройка Backend
Перейдите в папку бэкенда, создайте виртуальное окружение и установите зависимости:
```bash
cd backend
python -m venv venv
# Для Windows:
.\venv\Scripts\activate
# Для Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```
4. Настройка Frontend
В отдельном терминале перейдите в папку фронтенда:
```bash
cd frontend
npm install
npm run dev
```
5. Запуск бэка 
```bash
cd backend
uvicorn app.main:app --reload
```

#### 2. How to Modify the Database
If you add a new field or a new table in models.py:

1) Generate a migration script:

```bash
alembic revision --autogenerate -m "description_of_changes"
```
2) Verify the generated file in migrations/versions/.

3) Apply changes to the DB:
```bash
alembic upgrade head
```

#### 3. Useful Commands
- **alembic history** --verbose – View the history of all changes.

- **alembic current** – Check the current version of your database.

- **alembic downgrade -1** – Revert the last applied migration.

## 📁 Структура проекта
- **backend/app/api** — эндпоинты (маршруты) API.

- **backend/app/models** — описание таблиц БД (SQLModel + Геометрия).

- **backend/app/services** — логика расчета пути (алгоритмы A* / Dijkstra).

- **frontend/src/components** — UI-компоненты (карта, переключатель этажей).

- **data/raw** — сюда кладем исходные картинки планов этажей.

- **data/processed** — здесь храним GeoJSON файлы после оцифровки в QGIS.

## 🤝 Распределение ролей
1. **Backend & DB:** Работа с PostGIS, написание алгоритмов поиска пути в services/, настройка API.

- **Frontend:** Визуализация карты в MapLibre, отрисовка маршрутов, UI/UX.

- **GIS & Data:** Оцифровка планов в QGIS/GeoJSON, подготовка данных для загрузки в базу.