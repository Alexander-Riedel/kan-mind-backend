
# 🧠 KanMind – Kanban Backend API

This is the backend for **KanMind**, a task management and collaboration tool inspired by Kanban.  
It is developed as part of a **training project for the Developer Akademie** and is intended for testing and educational purposes only.

> ❗ **Important:** This project is part of a course exercise at the Developer Akademie.  
> It is not intended for production use and does **not** include a license.

---

## 🚀 Features

- ✅ User registration and login (token-based authentication)
- 🗂️ Board creation with owners and members
- 📌 Task assignment with statuses, priorities, deadlines, assignee and reviewer roles
- 💬 Comments on tasks
- 🔐 Permissions based on ownership and board membership

---

## 🧱 Tech Stack

- Python 3.10+
- Django 5.x
- Django REST Framework
- SQLite (default, can be switched to PostgreSQL or MySQL)
- Token authentication via `rest_framework.authtoken`

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Alexander-Riedel/kan-mind-backend.git
cd kan-mind-backend
```

### 2. Set up a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (optional, for admin panel)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

---

## 🔐 Authentication

The API uses **token authentication**. After login or registration, you'll receive a token in the response. Include this token in the `Authorization` header for all authenticated requests:

```
Authorization: Token your_token_here
```

---

## 📚 API Endpoints (Overview)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/registration/` | POST | Register a new user |
| `/api/login/` | POST | Log in and get auth token |
| `/api/email-check/` | GET | Check if an email is already registered |
| `/api/boards/` | GET/POST | List or create boards |
| `/api/boards/<id>/` | GET/PATCH/DELETE | Retrieve, update or delete a board |
| `/api/tasks/` | POST | Create a task |
| `/api/tasks/<id>/` | PATCH/DELETE | Update or delete a task |
| `/api/tasks/assigned-to-me/` | GET | List tasks assigned to current user |
| `/api/tasks/reviewing/` | GET | List tasks where user is reviewer |
| `/api/tasks/<task_id>/comments/` | GET/POST | List or create comments on a task |
| `/api/tasks/<task_id>/comments/<comment_id>/` | DELETE | Delete a specific comment |

---

## ⚙️ Project Structure

```
kanmind-backend/
├── auth_app/           # Handles registration, login, user profiles
├── kanban_app/         # Boards, tasks, comments
├── core/               # Django project settings and root URLs
├── db.sqlite3          # Default database (can be changed)
└── manage.py           # Django CLI tool
```

---

## ❌ License

This project is part of a learning exercise at the Developer Akademie.  
There is **no license** associated with this code.

---

## 🙌 Contributing

This repository is for training purposes. Contributions are not expected.
