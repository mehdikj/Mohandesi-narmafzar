# Digital Library — Sprint 1 Backend

Backend foundation for a web-based digital library. This project is being
developed incrementally across multiple sprints.

## Sprint 1 Features

- User registration and JWT authentication
- User roles: Super Admin, Librarian, and Registered User
- Current-user API endpoint
- Author and category management
- Digital resource registration and listing
- PDF and EPUB file validation
- SHA-256-based duplicate file detection
- Basic resource access control
- Django Admin
- OpenAPI schema and Swagger UI
- PostgreSQL database and Django migrations
- Automated tests for selected Sprint 1 workflows

## Technology Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker Compose
- Simple JWT
- drf-spectacular
- pytest and pytest-django

## Requirements

- Python 3.12 or newer
- Git
- Docker Desktop with WSL2 integration (recommended)
- Docker Compose

A local PostgreSQL installation can also be used instead of Docker.

## Setup on Ubuntu / WSL2

Run the following commands from the repository root:

```bash
cd backend
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure the Django secret key and database credentials.

Do not commit `.env` to Git.

## Setup on Windows (PowerShell)

Run the following commands from the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and configure the Django secret key and database credentials.

## PostgreSQL with Docker Compose

Docker Compose is the recommended database setup for local development.

The Compose configuration reads database settings from `.env`.
The default host port is `5433`, mapped to PostgreSQL's container port `5432`.

Start the database from the `backend` directory:

```bash
docker compose up -d db
```

Check the container:

```bash
docker compose ps
```

To inspect the resolved Compose configuration:

```bash
docker compose config
```

Make sure the database settings in `.env` match the Compose configuration.

Example local development settings:

```env
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
POSTGRES_DB=digital_library
POSTGRES_USER=library
POSTGRES_PASSWORD=library
```

The example credentials are for local development only. Use strong credentials
and secure secret management outside local development.
# اجرای پروژه با Docker

## ۱. پیش‌نیازها

برای اجرای پروژه به موارد زیر نیاز است:

- Docker Desktop
- فعال بودن موتور Docker با پشتیبانی WSL2
- Git
- دسترسی به ترمینال Ubuntu یا WSL

## ۲. دریافت پروژه

```bash
git clone https://github.com/AriaAlimahmoodi/Mohandesi-narmafraz.git
cd Mohandesi-narmafraz/backend
```

## ۳. تنظیم متغیرهای محیطی

فایل نمونه تنظیمات را کپی کنید:

```bash
cp .env.example .env
```

مقادیر فایل `.env` را متناسب با محیط خود تنظیم کنید:

```env
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
POSTGRES_DB=digital_library
POSTGRES_USER=library
POSTGRES_PASSWORD=your-database-password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
```

**نکته امنیتی:** فایل `.env` شامل اطلاعات محرمانه است و نباید در Git ثبت شود. برای محیط واقعی نیز باید از Secret Key و رمز عبور امن استفاده شود.

## ۴. ساخت و اجرای سرویس‌ها

از پوشه `backend` اجرا کنید:

```bash
docker compose up --build -d
```

این دستور تصویر Django را می‌سازد و سرویس‌های زیر را اجرا می‌کند:

- `web`: برنامه Django و API
- `db`: پایگاه داده PostgreSQL

سرویس Django پس از سالم شدن سرویس PostgreSQL اجرا می‌شود.

## ۵. بررسی وضعیت سرویس‌ها

```bash
docker compose ps
```

برای مشاهده گزارش Django:

```bash
docker compose logs --tail=50 web
```

برای مشاهده گزارش PostgreSQL:

```bash
docker compose logs --tail=50 db
```

## ۶. اجرای Migrationها

```bash
docker compose exec web python manage.py migrate
```

## ۷. ساخت حساب مدیر

```bash
docker compose exec web python manage.py createsuperuser
```

مراحل وارد کردن نام کاربری، ایمیل و رمز عبور را تکمیل کنید.

## ۸. دسترسی به سامانه

پس از اجرای موفق سرویس‌ها:

- مستندات API و Swagger: http://127.0.0.1:8000/api/docs/
- پنل مدیریت Django: http://127.0.0.1:8000/admin/

## ۹. اجرای تست‌ها

```bash
docker compose exec web pytest -q
```

برای بررسی تنظیمات Django:

```bash
docker compose exec web python manage.py check
```

## ۱۰. توقف سرویس‌ها

برای متوقف کردن سرویس‌ها بدون حذف داده‌های پایگاه داده:

```bash
docker compose stop
```

برای اجرای مجدد:

```bash
docker compose start
```

برای خاموش کردن سرویس‌ها و حذف کانتینرها، بدون حذف Volume دیتابیس:

```bash
docker compose down
```

**هشدار:** از `docker compose down -v` استفاده نکنید، مگر اینکه عمداً بخواهید Volume و داده‌های پایگاه داده Docker را حذف کنید.

## ۱۱. نکات توسعه

- فایل‌های بارگذاری‌شده در پوشه `backend/media` نگهداری می‌شوند.
- داده‌های PostgreSQL در Docker Volume ذخیره می‌شوند.
- تغییرات کد و تنظیمات باید با تست‌های خودکار بررسی شوند.
- فایل `.env`، رمزها و کلیدهای محرمانه نباید به مخزن Git ارسال شوند.
- دستور اجرای فعلی Django از `runserver` استفاده می‌کند و برای توسعه و نمایش محلی است؛ برای استقرار Production باید سرور مناسب و تنظیمات امنیتی Production پیکربندی شوند.
## Database Migrations

After configuring the environment and starting PostgreSQL, run:

```bash
python manage.py migrate
```

Create a Django superuser:

```bash
python manage.py createsuperuser
```

## Run the Development Server

```bash
python manage.py runserver
```

The development server is available at:

http://127.0.0.1:8000/

## Run Tests

Run the automated test suite from the `backend` directory:

```bash
python -m pytest -v
```

The current Sprint 1 tests cover selected authentication, public resource
listing, and librarian resource registration workflows.

## API Documentation

When the development server is running:

- Swagger UI: http://127.0.0.1:8000/api/docs/
- OpenAPI schema: http://127.0.0.1:8000/api/schema/

## Django Admin

http://127.0.0.1:8000/admin/

Sign in using the superuser account created with `createsuperuser`.

## Current Sprint 1 Limitations

The following capabilities are not yet fully implemented:

- Subscription lifecycle and subscription-based access
- Advanced group-specific and confidential permission management
- Complete resource publishing and archival workflows
- Secure online reading and file downloading
- File replacement and complete resource version management
- Advanced search, filtering, and pagination

These capabilities are planned for subsequent development sprints.
