# Backend Deploy Guide

## Option 1: PythonAnywhere (BEPUL, ENG OSON)

### 1. Ro'yxatdan o'ting
- https://www.pythonanywhere.com
- Beginner account (bepul)

### 2. Bash console ochib, code yuklang
```bash
git clone https://github.com/yourusername/oila_backend.git
cd oila_backend
```

### 3. Virtual environment yarating
```bash
mkvirtualenv --python=/usr/bin/python3.10 oila
pip install -r requirements_prod.txt
```

### 4. Database yarating
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 5. Web app sozlang
- Web tab → Add new web app
- Manual configuration → Python 3.10
- Source code: `/home/yourusername/oila_backend`
- Working directory: `/home/yourusername/oila_backend`
- WSGI file: Edit va quyidagini qo'shing:

```python
import sys
import os

path = '/home/yourusername/oila_backend'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'oila_backend.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 6. Static files
- Static files → URL: `/static/`
- Directory: `/home/yourusername/oila_backend/staticfiles`

### 7. Reload
- Web tab → Reload button

### 8. Test
- https://yourusername.pythonanywhere.com/swagger/

---

## Option 2: Railway.app (PROFESSIONAL, $5/oy)

### 1. GitHub ga push qiling
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/oila_backend.git
git push -u origin main
```

### 2. Railway.app da deploy
- https://railway.app → Login with GitHub
- New Project → Deploy from GitHub repo
- Select `oila_backend`
- Add PostgreSQL database (optional)
- Environment variables:
  - `DJANGO_SETTINGS_MODULE=oila_backend.settings_prod`
  - `SECRET_KEY=your-secret-key`
- Deploy!

### 3. Domain
- Settings → Generate Domain
- URL: `https://your-app.railway.app`

---

## Option 3: Render.com (BEPUL, YAXSHI)

### 1. GitHub ga push qiling (yuqoridagi kabi)

### 2. Render.com da deploy
- https://render.com → New → Web Service
- Connect GitHub repo
- Build Command: `pip install -r requirements_prod.txt && python manage.py migrate && python manage.py collectstatic --noinput`
- Start Command: `gunicorn oila_backend.wsgi:application`
- Environment variables:
  - `DJANGO_SETTINGS_MODULE=oila_backend.settings_prod`
  - `SECRET_KEY=your-secret-key`

### 3. URL
- `https://your-app.onrender.com`

---

## Flutter App ni yangilash

Deploy qilgandan keyin, Flutter app da URL ni o'zgartiring:

```dart
// lib/core/constants/api_constants.dart
static const String baseUrl = 'https://yourusername.pythonanywhere.com';
```

Hot Restart qiling va test qiling!
