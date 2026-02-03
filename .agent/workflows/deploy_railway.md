# Hướng Dẫn Deploy Lên Railway.app (Chi Tiết)

## Tổng Quan

**Railway.app** là nền tảng PaaS cho phép deploy ứng dụng dễ dàng với:
- ✅ Miễn phí $5 credit/tháng
- ✅ Tự động detect và build từ GitHub
- ✅ PostgreSQL database miễn phí
- ✅ SSL/HTTPS tự động
- ✅ Domain miễn phí (.railway.app)
- ✅ Custom domain support

---

## Bước 1: Chuẩn Bị Repository

### 1.1. Push Code Lên GitHub

```bash
# Nếu chưa có Git repository
cd d:\github\club-web-app
git init
git add .
git commit -m "Initial commit for Railway deployment"

# Tạo repository trên GitHub và push
git remote add origin https://github.com/<username>/club-web-app.git
git branch -M main
git push -u origin main
```

### 1.2. Kiểm Tra Files Cần Thiết

Đảm bảo có các files này trong repository:

✅ `requirements.txt` - Dependencies
✅ `wsgi.py` - Entry point
✅ `Dockerfile` - Railway sẽ dùng để build
✅ `.env.example` - Template cho environment variables

---

## Bước 2: Tạo Tài Khoản Railway

1. Truy cập: https://railway.app
2. Click **"Login"** → Chọn **"Login with GitHub"**
3. Authorize Railway truy cập GitHub của bạn

---

## Bước 3: Tạo Project Mới

1. Click **"New Project"**
2. Chọn **"Deploy from GitHub repo"**
3. Chọn repository `club-web-app`
4. Railway sẽ tự động detect Dockerfile và bắt đầu deploy

---

## Bước 4: Thêm PostgreSQL Database

### 4.1. Thêm Database Service

1. Trong project dashboard, click **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway sẽ tự động tạo PostgreSQL instance
3. Database URL sẽ được tự động inject vào app

### 4.2. Lấy Database URL

1. Click vào PostgreSQL service
2. Tab **"Connect"** → Copy **"Postgres Connection URL"**
3. URL sẽ có format: `postgresql://user:password@host:port/database`

---

## Bước 5: Cấu Hình Environment Variables

### 5.1. Truy Cập Variables Settings

1. Click vào web service (không phải database)
2. Tab **"Variables"**
3. Click **"+ New Variable"**

### 5.2. Thêm Các Biến Sau

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=<tạo-secret-key-mạnh>
FLASK_APP=wsgi.py

# Database (Railway tự động set, nhưng đảm bảo đúng tên)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Admin Credentials (QUAN TRỌNG: đổi password mạnh)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<mật-khẩu-mạnh-của-bạn>
ADMIN_FULL_NAME=Administrator
ADMIN_EMAIL=admin@yourdomain.com

# Upload Settings
UPLOAD_FOLDER=app/static/uploads
MAX_UPLOAD_SIZE=5242880
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,webp,gif
ALLOWED_VIDEO_EXTENSIONS=mp4,webm
MAX_IMAGES_PER_POST=5

# Pagination
POSTS_PER_PAGE=12
COMMENTS_PER_PAGE=20

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

**Tạo SECRET_KEY mạnh:**
```bash
# Chạy local để tạo
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5.3. Cấu Hình Database URL

Railway tự động link PostgreSQL, nhưng đảm bảo variable `DATABASE_URL` có giá trị:
```
${{Postgres.DATABASE_URL}}
```

---

## Bước 6: Fix PostgreSQL Compatibility

### 6.1. Cập Nhật `requirements.txt`

Thêm driver PostgreSQL:

```bash
# Database
psycopg2-binary==2.9.9
```

### 6.2. Update `config.py` (Nếu Cần)

Đảm bảo config hỗ trợ PostgreSQL URL:

```python
# Database
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///karate_club.db')

# Fix for Railway PostgreSQL URL (postgres:// -> postgresql://)
if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
```

---

## Bước 7: Deploy và Khởi Tạo Database

### 7.1. Trigger Redeploy

Sau khi thêm variables:
1. Railway sẽ tự động redeploy
2. Hoặc click **"Redeploy"** trong Deployments tab

### 7.2. Chạy Database Migrations

Railway cung cấp terminal để chạy commands:

1. Click vào web service
2. Tab **"Deployments"** → Click vào deployment mới nhất
3. Click **"View Logs"** → Chuyển sang tab **"Deploy Logs"**
4. Nhấn **">"** icon để mở Railway Shell

Trong Railway Shell:

```bash
# Chạy migrations
flask db upgrade

# Seed dữ liệu ban đầu
flask seed-db
```

**Lưu ý:** Nếu không có Railway Shell, bạn có thể:
- Sử dụng Railway CLI (xem bước 8)
- Hoặc thêm commands vào Dockerfile

---

## Bước 8: Sử dụng Railway CLI (Tùy Chọn)

### 8.1. Cài Đặt Railway CLI

```bash
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# hoặc với npm
npm install -g @railway/cli
```

### 8.2. Login và Link Project

```bash
# Login
railway login

# Link với project
cd d:\github\club-web-app
railway link
```

### 8.3. Chạy Commands

```bash
# Chạy migrations
railway run flask db upgrade

# Seed database
railway run flask seed-db

# Xem logs
railway logs

# Open shell
railway shell
```

---

## Bước 9: Cấu Hình Domain

### 9.1. Domain Miễn Phí Railway

Railway tự động cung cấp domain dạng: `<app-name>.up.railway.app`

1. Tab **"Settings"** → **"Domains"**
2. Click **"Generate Domain"**
3. Domain sẽ có SSL tự động

### 9.2. Custom Domain (Tùy Chọn)

1. Tab **"Settings"** → **"Domains"**
2. Click **"Custom Domain"**
3. Nhập domain của bạn (vd: `karate.yourdomain.com`)
4. Thêm CNAME record tại nhà cung cấp domain:
   ```
   Type: CNAME
   Name: karate (hoặc subdomain bạn muốn)
   Value: <giá trị Railway cung cấp>
   TTL: 3600
   ```
5. SSL sẽ tự động được cấu hình

---

## Bước 10: Test và Verification

### 10.1. Kiểm Tra App

1. Mở URL Railway: `https://<app-name>.up.railway.app`
2. Test login với admin account
3. Test tạo post, upload ảnh
4. Kiểm tra belt system mới

### 10.2. Xem Logs

```bash
# Via CLI
railway logs

# Via Web UI
Project → Deployments → Click deployment → View Logs
```

### 10.3. Kiểm Tra Database

```bash
# Connect to PostgreSQL
railway connect Postgres

# Hoặc qua Railway CLI
railway run flask shell
```

```python
# Trong Flask shell
from app.models import User, Post
print(f"Total users: {User.query.count()}")
print(f"Total posts: {Post.query.count()}")
```

---

## Cập Nhật Code (Auto Deploy)

### Push lên GitHub

```bash
git add .
git commit -m "Update features"
git push origin main
```

Railway sẽ **tự động** detect và deploy version mới!

---

## Troubleshooting

### Lỗi "Application failed to respond"

**Nguyên nhân:** Port không đúng

**Giải pháp:** Railway inject port qua `$PORT`, cập nhật `wsgi.py`:

```python
import os
from app import create_app

application = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    application.run(host='0.0.0.0', port=port)
```

### Lỗi "Database connection failed"

**Kiểm tra:**
```bash
railway run python -c "import os; print(os.getenv('DATABASE_URL'))"
```

Đảm bảo DATABASE_URL được set đúng: `${{Postgres.DATABASE_URL}}`

### Lỗi "No such table"

**Nguyên nhân:** Chưa chạy migrations

**Giải pháp:**
```bash
railway run flask db upgrade
railway run flask seed-db
```

### Lỗi Upload File

**Nguyên nhân:** Railway filesystem là ephemeral (bị xóa khi redeploy)

**Giải pháp:** Sử dụng Railway Volumes hoặc external storage (Cloudinary, S3)

**Thêm Volume:**
1. Service Settings → Volumes
2. Add volume: Mount path `/app/app/static/uploads`

---

## Monitoring và Logs

### View Metrics

1. Project Dashboard → Service
2. Tab **"Metrics"** - CPU, Memory, Network

### Download Logs

```bash
railway logs > logs.txt
```

---

## Chi Phí

**Free Tier:**
- $5 credit/tháng
- Đủ cho 1 web app nhỏ + PostgreSQL
- Estimate: ~150-200 hours runtime/tháng

**Nếu hết credit:** App sẽ bị pause, cần upgrade lên Hobby ($5/month) hoặc Pro.

---

## Backup Database

### Sử dụng Railway CLI

```bash
# Backup PostgreSQL
railway run pg_dump $DATABASE_URL > backup.sql

# Restore
railway run psql $DATABASE_URL < backup.sql
```

### Hoặc kết nối qua tool như pgAdmin

1. Lấy connection details từ Railway
2. Connect bằng pgAdmin/DBeaver
3. Backup/Restore qua GUI

---

## Summary

✅ **Deploy thành công nếu:**
- App accessible qua Railway URL
- Login admin hoạt động
- Database có dữ liệu
- SSL/HTTPS hoạt động
- Auto-deploy khi push GitHub

🎉 **Xong! App đã live trên internet!**
