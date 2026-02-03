# Hướng Dẫn Deploy Lên Railway - CHUẨN (Từ Đầu)

## 📋 Chuẩn Bị

### 1. Push Code Lên GitHub

```bash
cd d:\github\club-web-app

git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

---

## 🚀 Deploy Lên Railway (Từng Bước)

### BƯỚC 1: Tạo Tài Khoản Railway

1. Truy cập: https://railway.app
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway

### BƯỚC 2: Tạo Project Mới

1. Dashboard → Click **"New Project"**
2. Chọn **"Deploy from GitHub repo"**
3. Chọn repository: `club-web-app`
4. Railway sẽ bắt đầu deploy (ĐỪNG LO nếu fail, chưa xong!)

### BƯỚC 3: Thêm PostgreSQL Database

1. Trong Project → Click **"+ New"** (góc trên phải)
2. Chọn **"Database"** → **"Add PostgreSQL"**
3. Đợi PostgreSQL tạo xong (1-2 phút)

### BƯỚC 4: Cấu Hình Environment Variables

1. Click vào **Web Service** (service chạy app, KHÔNG phải Postgres)
2. Tab **"Variables"**
3. Thêm từng biến sau:

#### Biến 1: DATABASE_URL (Reference)

- Click **"+ New Variable"**
- Chọn **"Add a Reference"** (QUAN TRỌNG!)
- Service: Chọn **"Postgres"** (tên database vừa tạo)
- Variable: Chọn **"DATABASE_URL"**
- Click **"Add"**

Bạn sẽ thấy: `DATABASE_URL = ${{Postgres.DATABASE_URL}}`

**HOẶC** nếu Reference không được:

- Click vào **Postgres service**
- Tab **"Connect"** → Copy **"Postgres Connection URL"**
- Quay lại Web Service → Variables
- Click **"+ New Variable"** → **"Add a Variable"**
- Variable Name: `DATABASE_URL`
- Value: Paste URL vừa copy
- Click **"Add"**

#### Biến 2-10: Các Biến Khác

Click **"+ New Variable"** → **"Add a Variable"** cho từng biến:

```bash
# Flask
FLASK_ENV=production
SECRET_KEY=YOUR_SECRET_KEY_HERE_CHANGE_THIS
FLASK_APP=wsgi.py

# Admin (ĐỔI MẬT KHẨU!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YOUR_STRONG_PASSWORD_HERE
ADMIN_FULL_NAME=Administrator
ADMIN_EMAIL=admin@yourclub.com

# Upload
UPLOAD_FOLDER=app/static/uploads
MAX_UPLOAD_SIZE=5242880

# Pagination
POSTS_PER_PAGE=12
```

**Tạo SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy output và paste vào `SECRET_KEY`.

### BƯỚC 5: Cấu Hình Deploy Settings

1. Web Service → Tab **"Settings"**
2. Scroll xuống **"Deploy"** section
3. Cấu hình:

**Start Command:** (Quan trọng!)
```
sh -c 'gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 wsgi:application'
```

**Restart Policy:** `On Failure`

**Restart Policy Max Retries:** `10`

4. Click **"Save Config"** hoặc tương tự

### BƯỚC 6: Trigger Redeploy

1. Tab **"Deployments"**
2. Click **"Redeploy"** hoặc **"New Deployment"**
3. Đợi build hoàn tất (3-5 phút)

### BƯỚC 7: Kiểm Tra Logs

Click **"View Logs"** để xem build progress.

**Logs thành công sẽ có:**
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:xxxx
[INFO] Booting worker with pid: xxx
```

**KHÔNG có lỗi PORT hay DATABASE!**

### BƯỚC 8: Chạy Database Migrations

**Cách 1: Dùng Railway CLI (Khuyến nghị)**

```bash
# Cài Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
cd d:\github\club-web-app
railway link

# Chọn project và service

# Chạy migrations
railway run flask db upgrade

# Seed data
railway run flask seed-db
```

**Cách 2: Qua Railway Shell (Web UI)**

1. Service → **"Deployments"** → Click deployment mới nhất
2. Tìm button **"Shell"** hoặc **">_"** icon
3. Trong shell chạy:
```bash
flask db upgrade
flask seed-db
```

### BƯỚC 9: Test App

1. Lấy URL: Web Service → **"Settings"** → **"Domain"** (dạng: `https://xxx.up.railway.app`)
2. Mở URL trong browser
3. Login với:
   - Username: `admin`
   - Password: `<ADMIN_PASSWORD bạn đã set>`

---

## ✅ Checklist Thành Công

- [ ] App accessible tại Railway URL
- [ ] Không có lỗi trong logs
- [ ] Login admin thành công
- [ ] Database có dữ liệu (users, posts)
- [ ] Tạo post mới được
- [ ] Upload ảnh được

---

## 🔧 Troubleshooting

### Lỗi: "Could not parse SQLAlchemy URL"

**Nguyên nhân:** DATABASE_URL chưa được set

**Fix:**
1. Variables tab → Kiểm tra có `DATABASE_URL` không
2. Nếu không → Làm lại BƯỚC 4
3. Nếu có nhưng empty → Delete và tạo lại

### Lỗi: "$PORT is not a valid port number"

**Nguyên nhân:** Start Command không đúng

**Fix:**
1. Settings → Deploy → Start Command
2. Xóa hết
3. Nhập lại CHÍNH XÁC:
```
sh -c 'gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 wsgi:application'
```
4. Lưu ý: Dùng **single quotes** `'...'`

### Lỗi: "Worker failed to boot"

**Nguyên nhân:** Thiếu environment variables

**Fix:** Kiểm tra Variables tab có đầy đủ tất cả biến không (xem BƯỚC 4)

### Build Timeout

**Nguyên nhân:** Dockerfile build lâu

**Fix:**
1. Settings → Build → Builder
2. Đổi từ `Dockerfile` sang `Nixpacks`
3. Redeploy

---

## 📝 Lưu Ý Quan Trọng

1. **Start Command PHẢI dùng:** `sh -c '...'` để Railway expand `$PORT` đúng
2. **DATABASE_URL:** Dùng Reference nếu được, nếu không thì copy/paste URL
3. **SECRET_KEY:** PHẢI đổi, không dùng default
4. **ADMIN_PASSWORD:** PHẢI đổi ngay sau deploy
5. **Migrations:** PHẢI chạy trước khi dùng app

---

## 🎯 File Cần Có Trong Repo

- ✅ `Dockerfile` - Build image
- ✅ `requirements.txt` - Dependencies
- ✅ `wsgi.py` - Entry point
- ✅ `.env.example` - Template variables
- ✅ `app/` - Application code

**Không cần:**
- ❌ `railway.toml` (có thể có hoặc không)
- ❌ `nixpacks.toml` (có thể có hoặc không)
- ❌ `entrypoint.sh` (Railway không cần)
- ❌ `build.sh` (dành cho Render)

---

## 🚀 Sau Khi Deploy Thành Công

**Update code:** Chỉ cần push lên GitHub, Railway tự động redeploy!

```bash
git add .
git commit -m "Update features"
git push origin main
```

Railway auto-deploy trong 2-3 phút.

**Backup database:**
```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

**View logs:**
```bash
railway logs -f
```

---

## ✨ Kết Luận

Làm theo **9 BƯỚC** trên, bạn sẽ deploy thành công 100%!

Quan trọng nhất:
1. PostgreSQL database được tạo
2. DATABASE_URL được set đúng
3. Start Command đúng format với `sh -c '...'`
4. Migrations được chạy

🎉 **Chúc bạn deploy thành công!**
