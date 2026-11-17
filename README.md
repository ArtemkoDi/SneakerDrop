# SneakerDrop

Бекенд веб-сайту для дистриб'ютора оригінальних кросівок (Nike, Adidas, New Balance, Asics та інші). Реалізований як REST API на Django REST Framework з JWT-автентифікацією.

Фронтенд-частина знаходиться в окремому репозиторії: [sneakerdrop-frontend](https://github.com/ArtemkoDi/sneakerdrop-frontend).

## Ідея проєкту

Сайт, де користувач може переглянути каталог кросівок, знайти потрібну модель, обрати розмір і оформити замовлення. Адміністратор керує каталогом через API.

### Основний функціонал

- **Каталог товарів:** перегляд кросівок, пошук за назвою моделі чи брендом.
- **Фільтрація та сортування:** фільтрація за брендом, призначенням, статтю, розміром; сортування за ціною.
- **Деталі товару:** окрема сторінка з описом, фото, ціною та доступними розмірами.
- **Сторінки брендів:** список брендів і всіх кросівок конкретного бренду.
- **Управління контентом:** адміністратор може додавати, редагувати та видаляти кросівки й бренди.
- **Акаунти користувачів:** реєстрація, авторизація, профіль з історією замовлень.
- **Корзина та замовлення:** додавання товарів у корзину та оформлення замовлення однією кнопкою.
- **Інформація про магазин:** розділ "Про нас" з контактами, умовами доставки та повернення.

## Технології

- Python 3.12+
- Django, Django REST Framework
- `djangorestframework-simplejwt` для JWT-автентифікації
- `drf-spectacular` для документації API (OpenAPI / Swagger)
- `pytest`, `pytest-django`, `pytest-cov` для тестів
- SQLite (для локальної розробки)

## Локальний запуск

Усі команди виконуються з папки, де лежить `manage.py`.

1. Склонуйте репозиторій і створіть віртуальне середовище:

   ```bash
   git clone https://github.com/ArtemkoDi/SneakerDrop.git
   cd SneakerDrop

   python -m venv .venv

   # Windows
   .venv\Scripts\activate
   # Linux / macOS
   source .venv/bin/activate
   ```

2. Встановіть залежності (разом із пакетами для тестів і документації):

   ```bash
   pip install -r requirements.txt
   ```

3. Створіть файл `.env` у корені проєкту на основі шаблону:

   ```bash
   cp .env.example .env
   ```

4. Заповніть змінні середовища в `.env` (опис нижче).

5. Застосуйте міграції та запустіть сервер:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

Після запуску API доступне за адресою `http://127.0.0.1:8000`.

Щоб отримати доступ до адмін-панелі (`/admin/`) і мати користувача з правами адміністратора, створіть суперкористувача:

```bash
python manage.py createsuperuser
```

### Змінні середовища

| Змінна | Опис | Приклад |
|--------|------|---------|
| `SECRET_KEY` | Секретний ключ Django, використовується для підпису сесій та JWT-токенів. Обов'язкова. | `django-insecure-...` |
| `DEBUG` | Режим налагодження: `True` для розробки, `False` для продакшену. | `True` |
| `ALLOWED_HOSTS` | Дозволені хости через кому. | `127.0.0.1,localhost` |
| `CORS_ALLOWED_ORIGINS` | Адреси фронтенду, яким дозволено звертатися до API, через кому. | `http://localhost:3000,http://127.0.0.1:5500` |

## Документація API

Документація генерується автоматично за допомогою `drf-spectacular`. Коли сервер запущений, доступні:

| Інтерфейс | Адреса |
|-----------|--------|
| Swagger UI (інтерактивна документація) | http://127.0.0.1:8000/api/docs/ |
| ReDoc | http://127.0.0.1:8000/api/redoc/ |
| OpenAPI-схема (специфікація) | http://127.0.0.1:8000/api/schema/ |

За посиланням на схему відкривається (або завантажується) актуальний файл специфікації OpenAPI 3.0.

## Автентифікація та права доступу

Автентифікація реалізована через **JWT** (бібліотека `djangorestframework-simplejwt`). Для захищених операцій клієнт має надсилати заголовок:

```
Authorization: Bearer <access_token>
```

### Ендпоінти автентифікації (`/api/auth/`)

#### `POST /api/auth/register/` — реєстрація

Тіло запиту (JSON):

| Поле | Опис |
|------|------|
| `username` | обов'язкове, до 150 символів, унікальне |
| `email` | обов'язкове, валідна адреса, унікальна |
| `password` | обов'язкове, мінімум 8 символів |
| `password_confirm` | обов'язкове, має збігатися з `password` |
| `first_name` | необов'язкове |
| `last_name` | необов'язкове |

Відповіді:

- `201 Created` — користувача створено, пароль збережено у захешованому вигляді (PBKDF2-SHA256).
- `400 Bad Request` — помилка валідації (паролі не збігаються, email або username зайняті, пароль надто простий чи короткий).

#### `POST /api/auth/login/` — вхід

Тіло запиту: `{"username": "...", "password": "..."}`

- `200 OK` — повертає `{"access": "<token>", "refresh": "<token>"}`. Access-токен діє 15 хвилин, refresh-токен — 24 години.
- `401 Unauthorized` — невірні облікові дані.

#### `POST /api/auth/token/refresh/` — оновлення access-токена

Тіло запиту: `{"refresh": "<refresh_token>"}`

- `200 OK` — повертає `{"access": "<new_access_token>"}`.
- `401 Unauthorized` — refresh-токен недійсний або прострочений.

#### `GET /api/auth/me/` — профіль поточного користувача

Потрібен заголовок `Authorization: Bearer <access_token>`.

- `200 OK` — повертає `id`, `username`, `email`, `first_name`, `last_name`, `is_staff`.
- `401 Unauthorized` — токена немає або він недійсний.

### Права доступу до каталогу

Для каталогу використовується власний пермішен `IsAdminOrReadOnly`:

- **Безпечні методи** (`GET`, `HEAD`, `OPTIONS`) доступні всім без авторизації: можна переглядати кросівки, бренди та розміри.
- **Методи зміни** (`POST`, `PUT`, `DELETE`) дозволені лише адміністраторам (`is_staff = True`).

| Ситуація | Відповідь |
|----------|-----------|
| Зміна даних без токена | `401 Unauthorized` |
| Зміна даних звичайним користувачем | `403 Forbidden` з повідомленням: *"Дія заборонена! Додавати, змінювати та видаляти товари може лише адміністратор"* |
| Запит до неіснуючого ресурсу | `404 Not Found` |

## REST API Endpoints

Дані передаються у форматі JSON. Нижче наведено основні ендпоінти та приклади запитів. Повний і актуальний опис дивіться у Swagger UI.


### Sneakers (кросівки)

| Метод | URL | Опис | Доступ |
|-------|-----|------|--------|
| `GET` | `/api/sneakers/` | Список кросівок (параметри: `?brand=nike&sort=price_asc&size=42`) | Усі |
| `GET` | `/api/sneakers/{id}/` | Деталі кросівок (`200` або `404`) | Усі |
| `POST` | `/api/sneakers/` | Додати кросівки (`201`) | Адмін |
| `PUT` | `/api/sneakers/{id}/` | Редагувати кросівки (`200`) | Адмін |
| `DELETE` | `/api/sneakers/{id}/` | Видалити кросівки (`204`) | Адмін |

Приклад відповіді `GET /api/sneakers/`:

```json
[
  {"id": 1, "name": "Nike Air Max 90", "brand": "Nike", "price": 4500.00}
]
```

Приклад відповіді `GET /api/sneakers/{id}/`:

```json
{
  "id": 1,
  "name": "Nike Air Max 90",
  "description": "Класичні кросівки...",
  "price": 4500.00,
  "sizes": [41, 42, 43]
}
```

Приклад тіла `POST /api/sneakers/`:

```json
{"name": "Nike Air Max 90", "brand_id": 1, "price": 4500.00, "category": "lifestyle"}
```

### Brands (бренди)

| Метод | URL | Опис | Доступ |
|-------|-----|------|--------|
| `GET` | `/api/brands/` | Список брендів | Усі |
| `GET` | `/api/brands/{id}/` | Деталі бренду та його товарів | Усі |
| `POST` | `/api/brands/` | Додати бренд | Адмін |
| `PUT` | `/api/brands/{id}/` | Редагувати бренд | Адмін |
| `DELETE` | `/api/brands/{id}/` | Видалити бренд | Адмін |

Приклад відповіді `GET /api/brands/`:

```json
[{"id": 1, "name": "Nike"}, {"id": 2, "name": "Adidas"}]
```

### Users (користувачі)

| Метод | URL | Опис |
|-------|-----|------|
| `GET` | `/api/users/profile/` | Профіль та історія замовлень |
| `PUT` | `/api/users/profile/` | Редагування профілю |

Приклад відповіді `GET /api/users/profile/`:

```json
{
  "id": 10,
  "first_name": "Іван",
  "email": "user@example.com",
  "orders_history": [{"order_id": 101, "total": 4500.00, "status": "delivered"}]
}
```

### Cart & Orders (корзина та замовлення)

| Метод | URL | Опис |
|-------|-----|------|
| `GET` | `/api/cart/` | Вміст корзини |
| `POST` | `/api/cart/items/` | Додати товар у корзину (`201`) |
| `POST` | `/api/orders/` | Створити замовлення з товарів у корзині (`201`) |

Приклад тіла `POST /api/cart/items/`:

```json
{"sneaker_id": 1, "size": 42, "quantity": 1}
```

## Схема бази даних

![Схема БД](https://github.com/user-attachments/assets/cf37c249-1808-4401-b6bb-2933c742edde)

## Тестування

У проєкті використовуються `pytest`, `pytest-django` та `pytest-cov`. Фікстури знаходяться в `conftest.py`, тести каталогу кросівок — у `shop/test_sneakers.py`.

Запустити всі тести:

```bash
pytest -v
```

Запустити тести зі звітом про покриття коду застосунку `shop`:

```bash
pytest --cov=shop --cov-report=term-missing
```


## web-programming-2026-template

A reusable Django project with no bundled application, SQLite, and Django's
standard admin, authentication, sessions, messages, and staticfiles support.

## Local setup

Requires the latest patch release of Python 3.12, 3.13, or 3.14. Run these commands from the project directory containing
`manage.py`.

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   
   # for linux/macos
   source .venv/bin/activate
   # for Windows:
   .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   python -m pip install -r requirements-dev.txt
   ```


3. Apply migrations to create the local SQLite database:

   ```bash
   python manage.py migrate
   ```

4. Start the development server:

   ```bash
   python manage.py runserver
   ```

## Endpoints

With the server running at `http://127.0.0.1:8000`:

| URL | Behavior |
| --- | --- |
| http://127.0.0.1:8000/ | No application homepage; may show Django's development welcome page while `DEBUG = True` |
| http://127.0.0.1:8000/admin/ | Django admin, available after applying migrations |

With `DEBUG = False`, unmatched URLs such as `/` return HTTP 404.

To create an account for admin login, run this after applying migrations:

```bash
python manage.py createsuperuser
```

## Add your first application

1. Create an app from the directory containing `manage.py` (replace `myapp`
   with your application name):

   ```bash
   python manage.py startapp myapp
   ```

2. Add its generated configuration class, `myapp.apps.MyappConfig`, to
   `INSTALLED_APPS` in `config/settings.py`.
3. Define your views and create `myapp/urls.py` with their URL patterns.
4. Register that URLconf in `config/urls.py` using `path()` and `include()`,
   choosing a URL prefix for the app and retaining the admin route.

See the official Django 6.1 tutorial for
[views and URL registration](https://docs.djangoproject.com/en/6.1/intro/tutorial01/)
and [app registration and models](https://docs.djangoproject.com/en/6.1/intro/tutorial02/).

## Git attributes

Git detects text files automatically and normalizes them to LF. Checkouts use
LF on Linux and Windows, while `.bat` and `.cmd` files use CRLF. Binary files
are auto-detected and left unchanged, helping avoid newline-only diffs.


## Code style and submission verification

All submissions are required to adhere to PEP-8, Django best practices, and standard HTML/CSS/JS formatting. A deterministic cross-platform utility is provided to help you check and format your code.

### 1. Verification (Check Mode)
Before submitting, verify that all files adhere to the required standards:

```bash
python check_submission.py
```

If all checks pass, you are ready to submit! If any checks fail, review the error output or run the auto-formatter below.

### 2. Auto-Formatting
To automatically format Python files, fix safe PEP-8 rules, format Django HTML templates, and format CSS/JS static files:

```bash
python check_submission.py --format
```

### 3. PyCharm Integration
If you use PyCharm:
- **One-Click Run:** In the top-right toolbar run configurations dropdown, select **"Verify Submission"** or **"Format Project"** and click the green **Play** button.

## Development only

The included settings use `DEBUG = True`, a development secret key, and a local
SQLite database. The default mailer uses the console backend: email is printed
to the process's console instead of being delivered.

This configuration and Django's development server are not suitable for
production deployment.
