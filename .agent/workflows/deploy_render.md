# Hướng Dẫn Deploy Lên Render.com (Chi Tiết)

## Tổng Quan

**Render.com** là nền tảng PaaS với:
- ✅ Free tier (có giới hạn)
- ✅ PostgreSQL database miễn phí (90 ngày)
- ✅ Auto deploy từ GitHub
- ✅ SSL/HTTPS tự động
- ✅ Custom domain support
- ✅ Đơn giản, dễ sử dụng

---

## Bước 1: Chuẩn Bị Repository

### 1.1. Push Code Lên GitHub

```bash
cd d:\github\club-web-app
git init
git add .
git commit -m "Initial commit for Render deployment"

# Push lên GitHub
git remote add origin https://github.com/<username>/club-web-app.git
git branch -M main
git push -u origin main
```

### 1.2. Tạo File `build.sh` (Script Build)

Tạo file `build.sh` trong root directory:

```bash
#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
flask db upgrade
```

Cấp quyền executable (trên Linux/Mac):
```bash
chmod +x build.sh
```

### 1.3. Tạo File `render.yaml` (Tùy Chọn - Cấu Hình Tự Động)

Tạo `render.yaml` để Render tự động setup:

```yaml
services:
  - type: web
    name: club-karatedo
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: club-karatedo-db
          property: connectionString
      - key: ADMIN_USERNAME
        value: admin
      - key: ADMIN_PASSWORD
        sync: false  # Set manually in dashboard
      - key: ADMIN_FULL_NAME
        value: Administrator
      - key: ADMIN_EMAIL
        value: admin@yourdomain.com

databases:
  - name: club-karatedo-db
    databaseName: karate_club
    user: karate_club_user
    plan: free
```

---

## Bước 2: Tạo Tài Khoản Render

1. Truy cập: https://render.com
2. Click **"Get Started"** 
3. Sign up với **GitHub** account
4. Authorize Render truy cập GitHub

---

## Bước 3: Tạo PostgreSQL Database

### 3.1. Create Database

1. Dashboard → Click **"New +"** → **"PostgreSQL"**
2. Cấu hình:
   - **Name**: `club-karatedo-db`
   - **Database**: `karate_club`
   - **User**: `karate_club_user`
   - **Region**: Singapore/Oregon (gần Việt Nam nhất)
   - **Plan**: **Free** (90 ngày, sau đó $7/month)
3. Click **"Create Database"**

### 3.2. Lấy Database URL

1. Click vào database vừa tạo
2. Tab **"Connect"** → Copy **"Internal Database URL"**
3. URL format: `postgresql://user:password@host:port/database`
4. **Lưu lại** để dùng cho web service

---

## Bước 4: Tạo Web Service

### 4.1. Create Web Service

1. Dashboard → Click **"New +"** → **"Web Service"**
2. Click **"Build and deploy from a Git repository"** → **"Next"**
3. Connect  GitHub repository `club-web-app`
4. Click **"Connect"**

### 4.2. Cấu Hình Service

**Basic Settings:**
- **Name**: `club-karatedo`
- **Region**: Singapore/Oregon
- **Branch**: `main`
- **Root Directory**: Leave empty (root of repo)

**Build Settings:**
- **Environment**: **Docker**
- **Dockerfile Path**: `./Dockerfile`

**Plan:**
- **Instance Type**: **Free** (512 MB RAM, web service sleeps sau 15 phút không active)

### 4.3. Advanced Settings

Click **"Advanced"** để thêm environment variables:

```bash
# Flask
FLASK_ENV=production
SECRET_KEY=<tạo-secret-key-mạnh>
FLASK_APP=wsgi.py

# Database
DATABASE_URL=<paste Internal Database URL từ bước 3.2>

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<mật-khẩu-mạnh>
ADMIN_FULL_NAME=Administrator
ADMIN_EMAIL=admin@yourdomain.com

# Upload
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

# Python
PYTHON_VERSION=3.11
```

**Tạo SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4.4. Create Web Service

Click **"Create Web Service"** → Render sẽ bắt đầu build và deploy

---

## Bước 5: Cập Nhật Code Cho PostgreSQL

### 5.1. Thêm `psycopg2` vào `requirements.txt`

```txt
psycopg2-binary==2.9.9
```

### 5.2. Fix PostgreSQL URL trong `config.py`

Cập nhật [config.py](file:///d:/github/club-web-app/app/config.py):

```python
# Database
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///karate_club.db')

# Fix for Render PostgreSQL URL (postgres:// -> postgresql://)
if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
```

### 5.3. Push Changes

```bash
git add .
git commit -m "Add PostgreSQL support for Render"
git push origin main
```

Render sẽ tự động detect và redeploy!

---

## Bước 6: Chạy Database Migrations

### Cách 1: Sử Dụng Render Shell

1. Service Dashboard → Tab **"Shell"**
2. Chạy commands:

```bash
# Migrations
flask db upgrade

# Seed data
flask seed-db
```

### Cách 2: Thêm vào `build.sh`

Update [build.sh](file:///d:/github/club-web-app/build.sh):

```bash
#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
flask db upgrade

# Seed initial data (chỉ chạy lần đầu)
flask seed-db || true  # Ignore error if data exists
```

Redeploy để chạy script.

---

## Bước 7: Cấu Hình Domain

### 7.1. Free Render Domain

Render tự động cung cấp domain: `https://<service-name>.onrender.com`

Example: `https://club-karatedo.onrender.com`

### 7.2. Custom Domain (Tùy Chọn)

1. Service Settings → **"Custom Domains"**
2. Click **"Add Custom Domain"**
3. Nhập domain: `karate.yourdomain.com`
4. Render sẽ hiện DNS records cần thêm

**Tại nhà cung cấp domain:**
```
Type: CNAME
Name: karate
Value: <value-from-render>
TTL: 3600
```

5. Sau khi DNS propagate, Render tự động cấp SSL certificate

---

## Bước 8: Test và Verification

### 8.1. Kiểm Tra Deployment

1. Dashboard → Deployment status chuyển sang **"Live"** (màu xanh)
2. Click **"View Logs"** để xem build/deploy logs
3. Mở URL: `https://<service-name>.onrender.com`

### 8.2. Test Functionality

- ✅ Homepage loads
- ✅ Login với admin
- ✅ Tạo post mới
- ✅ Upload ảnh
- ✅ Belt system hiển thị đúng

### 8.3. Xem Logs

```
Dashboard → Logs tab
```

Real-time logs hiển thị requests, errors, etc.

---

## Bước 9: Persistent Storage (File Uploads)

### ⚠️ Vấn Đề: Render Filesystem Là Ephemeral

Files uploaded sẽ bị mất khi service restart/redeploy!

### Giải Pháp 1: Render Disks (Recommended)

1. Service Settings → **"Disks"**
2. Click **"Add Disk"**
3. Cấu hình:
   - **Name**: `uploads`
   - **Mount Path**: `/app/app/static/uploads`
   - **Size**: 1 GB (free tier)
4. Save và redeploy

### Giải Pháp 2: External Storage

Sử dụng Cloudinary, AWS S3, hoặc Google Cloud Storage.

**Ví dụ với Cloudinary:**

```bash
# Add to requirements.txt
cloudinary==1.36.0

# Environment variables
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

---

## Auto Deploy Từ GitHub

### Kích Hoạt Auto Deploy

Mặc định Render **đã bật** auto-deploy:
- Mỗi khi push code lên GitHub branch `main`
- Render tự động build và deploy

### Tắt Auto Deploy (Nếu Muốn)

Service Settings → **"Auto-Deploy"** → Toggle off

### Manual Deploy

Dashboard → Click **"Manual Deploy"** → Select branch/commit

---

## Troubleshooting

### Lỗi "Build failed"

**Xem logs:**
```
Logs tab → Build logs
```

**Nguyên nhân thường gặp:**
- Thiếu dependencies trong `requirements.txt`
- Python version không đúng
- Database URL không đúng

### Lỗi "Application failed to respond"

**Kiểm tra port:**

Render inject port qua `$PORT`, update [wsgi.py](file:///d:/github/club-web-app/wsgi.py):

```python
import os
from app import create_app

application = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    application.run(host='0.0.0.0', port=port)
```

### Service "Sleeping" (Free Tier)

Free tier sleeps sau 15 phút không activity.

**Giải pháp:**
- Upgrade lên Starter ($7/month) → không sleep
- Sử dụng uptime monitoring (UptimeRobot) để ping app

### Database Connection Error

**Kiểm tra DATABASE_URL:**
```bash
# Trong Render Shell
echo $DATABASE_URL
```

Đảm bảo format đúng và sử dụng **Internal Database URL**.

---

## Monitoring và Logs

### View Metrics

Dashboard → **"Metrics"** tab:
- CPU usage
- Memory usage
- Response times
- Error rates

### Download Logs

```bash
# Render không có CLI, download qua Web UI
Logs tab → Copy logs manually
```

---

## Backup Database

### Cách 1: Qua Render Dashboard

1. Database service → **"Backups"** tab
2. Click **"Create Backup"**
3. Download backup file

### Cách 2: Thủ Công

```bash
# Get connection string
# Database → Connect tab → External Database URL

# Backup locally
pg_dump <external-database-url> > backup.sql

# Restore
psql <external-database-url> < backup.sql
```

---

## Chi Phí

### Free Tier

**Web Service:**
- 750 hours/month
- Auto-sleep sau 15 phút
- 512 MB RAM
- 0.1 CPU

**PostgreSQL:**
- 90 ngày miễn phí
- 256 MB RAM
- 1 GB storage
- **Sau 90 ngày:** $7/month

### Paid Plans

**Starter ($7/month):**
- No sleep
- 512 MB RAM

**Standard ($25/month):**
- 2 GB RAM
- Better performance

---

## So Sánh Railway vs Render

| Feature | Railway | Render |
|---------|---------|--------|
| **Free Credit** | $5/month | 750 hours/month |
| **Database** | PostgreSQL free | 90 ngày, sau đó $7/month |
| **Sleep** | Không | Có (15 phút) |
| **CLI** | ✅ Có | ❌ Không |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Auto Deploy** | ✅ | ✅ |
| **Custom Domain** | ✅ | ✅ |

**Khuyến nghị:** 
- **Railway** nếu cần database dài hạn
- **Render** nếu chỉ test ngắn hạn (90 ngày)

---

## Summary

✅ **Deploy thành công choir:**
- App live tại `https://<name>.onrender.com`
- PostgreSQL database hoạt động
- Auto-deploy từ GitHub
- SSL/HTTPS enabled
- Belt system 10 cấp hoạt động

🎉 **Done! App đã online!**
