## Автентифікація, Авторизація (JWT) та Права Доступу

У проєкті реалізовано систему автентифікації на основі **JWT** за допомогою бібліотеки `djangorestframework-simplejwt`.

### Заголовок авторизації
Для доступу до захищених операцій клієнт повинен надсилати HTTP-заголовок:
`Authorization: Bearer <access_token>`

---

### Ендпоінти автентифікації (`/api/auth/`):

1. **`POST /api/auth/register/`** — Реєстрація нового користувача
   * **Тіло запиту (JSON):**
     * `username` (рядок, обов'язкове, макс. 150 символів, унікальне)
     * `email` (рядок, обов'язкове, валідна адреса пошти, унікальне)
     * `password` (рядок, обов'язкове, мін. 8 символів)
     * `password_confirm` (рядок, обов'язкове, має збігатися з `password`)
     * `first_name` (рядок, необов'язкове)
     * `last_name` (рядок, необов'язкове)
   * **Коди відповідей:**
     * `201 Created` — користувача створено, пароль збережено в захешованому вигляді (PBKDF2-SHA256).
     * `400 Bad Request` — помилка валідації (паролі не збігаються, email/username зайняті, пароль надто простий або короткий).

2. **`POST /api/auth/login/`** — Отримання пари токенів (вхід)
   * **Тіло запиту:** `{"username": "...", "password": "..."}`
   * **Коди відповідей:**
     * `200 OK` — повертає `{"access": "<token>", "refresh": "<token>"}`. Час життя access-токена — 15 хв, refresh-токена — 24 години.
     * `401 Unauthorized` — невірні облікові дані.

3. **`POST /api/auth/token/refresh/`** — Оновлення access-токена
   * **Тіло запиту:** `{"refresh": "<refresh_token>"}`
   * **Коди відповідей:**
     * `200 OK` — повертає новий `{"access": "<new_access_token>"}`.
     * `401 Unauthorized` — refresh-токен недійсний або прострочений.

4. **`GET /api/auth/me/`** — Отримання профілю поточного користувача
   * **Заголовок:** `Authorization: Bearer <access_token>`
   * **Коди відповідей:**
     * `200 OK` — повертає дані профілю: `id`, `username`, `email`, `first_name`, `last_name`, `is_staff`.
     * `401 Unauthorized` — запит без токена або з недійсним токеном.

---

### Політика прав доступу (Permissions) для каталогу:
* **Кастомний пермішен `IsAdminOrReadOnly`:**
  * **Безпечні методи (`GET`, `HEAD`, `OPTIONS`):** доступні публічно без авторизації (перегляд каталогу кросівок, брендів, розмірів).
  * **Методи модифікації (`POST`, `PUT`, `DELETE`):** дозволені **виключно користувачам із правами адміністратора** (`is_staff = True`).
  * Спроба змінити дані без токена повертає `401 Unauthorized`.
  * Спроба змінити дані звичайним зареєстрованим користувачем (не адміном) повертає `403 Forbidden` із повідомленням: *"Дія заборонена! Додавати, змінювати та видаляти товари може лише адміністратор"*.
  * Запит до неіснуючого ресурсу повертає `404 Not Found`.

# web-programming-2026-template

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
