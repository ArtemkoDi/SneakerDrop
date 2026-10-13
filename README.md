# SneakerDrop

## Ідея проєкту: 
Веб сайт для дистриб'ютора оригінальних кросівок відомих брендів (Nike, Adidas, New Balance, Asics тощо)

**Основний функціонал**
* **Каталог товарів:** Перегляд переліку кросівок, пошук за назвою моделі чи брендом.
* **Фільтрація та сортування:** Фільтрація за брендом, призначенням, статтю, розміром. Сортування за ціною 
> **"TODO:** придумати ще за цим сортувати".
* **Деталі товару:** Окрема сторінка для товару з інформацією про нього, фотографією товару, ціною та доступними розмірами.
* **Сторінки брендів:** Перелік усіх доступних брендів, при переході на окремий бренд буде відображатись список усіх його кросівок.
* **Управління контентом:** Адміністратор може редагувати, додавати, видаляти інформацію про товар, бренди або навіть сам товар.
* **Акаунти користувачів:** Реєстрація для нових користувачів, авторизація, профіль користувача з історією замовлень.
* **Корзина та замовлення:** Додавання товарів у корзину та швидке оформлення замовлення однією кнопкою.
* **Інформація про магазин:** Розділ "Про Нас" з контактними даними, інформацією про доставку та повернення. 

## REST API Endpoints

Дані передаватимуться у форматі JSON.
> **TBD:** Як саме буде реалізовано потребують уточнення, але нижче наведено приблизний консепт як це буде виглядати

### Sneakers (Кросівки)

- **Отримання списку кросівок**
    - **Опис:** Повертає каталог взуття.
    - **Request method:** `GET /api/sneakers/`
    - **Request parameters:** `?brand=nike&sort=price_asc&size=42`
    - **Response status:** `200 OK`
    - **Response body:**
      ```json
      [
        {"id": 1, "name": "Nike Air Max 90", "brand": "Nike", "price": 4500.00}
      ]
      ```

- **Отримання деталей про пару кросівок**
    - **Request method:** `GET /api/sneakers/{id}/`
    - **Response status:** `200 OK` або `404 Not Found`
    - **Response body:**
      ```json
      {
        "id": 1, 
        "name": "Nike Air Max 90", 
        "description": "Класичні кросівки...",
        "price": 4500.00,
        "sizes": [41, 42, 43]
      }
      ```

- **Додавання нових кросівок (Адмін)**
    - **Request method:** `POST /api/sneakers/`
    - **Request body:** `{"name": "Nike Air Max 90", "brand_id": 1, "price": 4500.00, "category": "lifestyle"}`
    - **Response status:** `201 Created`

- **Редагування кросівок (Адмін)**
    - **Request method:** `PUT /api/sneakers/{id}/`
    - **Request body:** Оновлений JSON об'єкт товару.
    - **Response status:** `200 OK`

- **Видалення кросівок (Адмін)**
    - **Request method:** `DELETE /api/sneakers/{id}/`
    - **Response status:** `204 No Content`

### Brands (Бренди)

- **Отримання списку брендів**
    - **Request method:** `GET /api/brands/`
    - **Response status:** `200 OK`
    - **Response body:** `[{"id": 1, "name": "Nike"}, {"id": 2, "name": "Adidas"}]`

- **Отримання деталей бренду та його товарів**
    - **Request method:** `GET /api/brands/{id}/`
    - **Response status:** `200 OK`

- **Управління брендами (Адмін)**
    - **Request methods:** `POST /api/brands/`, `PUT /api/brands/{id}/`, `DELETE /api/brands/{id}/`

### Users & Auth (Користувачі та Профіль)

- **Реєстрація та Логін**
    - **Request methods:** `POST /api/auth/register/` та `POST /api/auth/login/`
    - **Request body:** `{"email": "user@example.com", "password": "password"}`
    - **Response status:** `200 OK` або `201 Created`

- **Отримання профілю та історії замовлень**
    - **Request method:** `GET /api/users/profile/`
    - **Response body:**
      ```json
      {
        "id": 10,
        "first_name": "Іван",
        "email": "user@example.com",
        "orders_history": [{"order_id": 101, "total": 4500.00, "status": "delivered"}]
      }
      ```

- **Редагування профілю**
    - **Request method:** `PUT /api/users/profile/`
    - **Request body:** `{"first_name": "Олексій", "phone": "+380991234567"}`
    - **Response status:** `200 OK`

### Cart & Orders (Корзина та Замовлення)

- **Отримання вмісту корзини**
    - **Request method:** `GET /api/cart/`
    - **Response status:** `200 OK`

- **Додавання товару в корзину**
    - **Request method:** `POST /api/cart/items/`
    - **Request body:** `{"sneaker_id": 1, "size": 42, "quantity": 1}`
    - **Response status:** `201 Created`

- **Створення замовлення**
    - **Опис:** Оформлення замовлення з товарів, що знаходяться у корзині.
    - **Request method:** `POST /api/orders/`
    - **Response status:** `201 Created`

## Схема бази даних

![Схема БД](https://github.com/user-attachments/assets/cf37c249-1808-4401-b6bb-2933c742edde)



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
