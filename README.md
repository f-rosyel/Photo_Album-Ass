# Lumière — Photo Album Management System

A production-ready Django application for managing photo albums with role-based access control, Cloudinary media storage, and PostgreSQL — deployed on Render.

---

## Architecture Overview

| Concern | Solution |
|---|---|
| Framework | Django 4.2 |
| Views | Class-Based Views (CBVs) |
| Auth & RBAC | Django's built-in auth + custom mixins |
| Database | PostgreSQL (via Render) |
| Media storage | Cloudinary |
| Static files | WhiteNoise |
| Production server | Gunicorn on Render |

---

## Role-Based Access Control

| Role | Capabilities |
|---|---|
| **Anonymous** | View public albums and photos |
| **Authenticated user** | + Create albums, upload photos to own albums, edit/delete own content |
| **Staff / Admin** | + Edit or delete any album or photo; access `/admin/` |

Enforced via Django mixins in `albums/mixins.py`:
- `AlbumOwnerOrAdminMixin` — album edit/delete
- `PhotoOwnerOrAdminMixin` — photo edit/delete
- `PublicOrAuthenticatedMixin` — private album gating

---

## Local Development Setup

### 1. Clone & create virtual environment

```bash
git clone <repo-url>
cd photo_album
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your values (see below)
```

Minimum `.env` for local dev (SQLite + Cloudinary):

```
SECRET_KEY=any-random-string-for-dev
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

> **Get Cloudinary credentials**: Sign up free at [cloudinary.com](https://cloudinary.com), go to **Dashboard → API Keys**.

### 3. Run migrations & create superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Start the development server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## Deploying to Render

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/photo-album.git
git push -u origin main
```

### Step 2 — Create a PostgreSQL database on Render

1. [render.com](https://render.com) → **New → PostgreSQL**
2. Name it (e.g. `lumiere-db`), choose region, click **Create Database**
3. Copy the **Internal Database URL** — you'll need it shortly

### Step 3 — Create a Web Service on Render

1. **New → Web Service** → connect your GitHub repo
2. Configure:

| Field | Value |
|---|---|
| **Runtime** | Python 3 |
| **Build Command** | `./render-build.sh` |
| **Start Command** | `gunicorn photo_album.wsgi:application` |

3. Add Environment Variables (under **Environment** tab):

| Key | Value |
|---|---|
| `SECRET_KEY` | A long random string (use [randomkeygen.com](https://randomkeygen.com)) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` |
| `DATABASE_URL` | Internal DB URL from Step 2 |
| `CLOUDINARY_CLOUD_NAME` | From Cloudinary dashboard |
| `CLOUDINARY_API_KEY` | From Cloudinary dashboard |
| `CLOUDINARY_API_SECRET` | From Cloudinary dashboard |

4. Click **Create Web Service** — Render will build and deploy automatically.

### Step 4 — Create a superuser in production

In the Render dashboard → your service → **Shell** tab:

```bash
python manage.py createsuperuser
```

---

## Project Structure

```
photo_album/
├── photo_album/          # Project config
│   ├── settings.py       # All settings (env-var driven)
│   ├── urls.py           # Root URL conf
│   └── wsgi.py
├── albums/               # Main app
│   ├── models.py         # Album, Photo (CloudinaryField)
│   ├── views.py          # All CBVs
│   ├── mixins.py         # RBAC mixins
│   ├── forms.py          # AlbumForm, PhotoForm, RegisterForm
│   ├── urls.py           # App URL patterns
│   └── admin.py          # Admin registration
├── templates/
│   ├── base.html
│   ├── albums/           # All album/photo templates
│   └── registration/     # Login, register
├── static/css/main.css   # Stylesheet
├── requirements.txt
├── render-build.sh       # Render build hook
├── Procfile
└── .env.example
```

---

## Key Endpoints

| URL | View | Description |
|---|---|---|
| `/` | `AlbumListView` | Browse albums |
| `/albums/create/` | `AlbumCreateView` | New album (auth required) |
| `/albums/<pk>/` | `AlbumDetailView` | View album + photos |
| `/albums/<pk>/edit/` | `AlbumUpdateView` | Edit (owner/admin) |
| `/albums/<pk>/delete/` | `AlbumDeleteView` | Delete (owner/admin) |
| `/albums/<pk>/photos/upload/` | `PhotoCreateView` | Upload photo |
| `/albums/<apk>/photos/<pk>/` | `PhotoDetailView` | View photo |
| `/accounts/login/` | Django built-in | Sign in |
| `/accounts/register/` | `RegisterView` | Sign up |
| `/admin/` | Django admin | Staff only |
