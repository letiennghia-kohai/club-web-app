# Fix Lỗi "Could not parse SQLAlchemy URL from string ''"

## Vấn Đề
Database URL không được set trong Railway → SQLAlchemy không thể kết nối database.

## Giải Pháp: Setup PostgreSQL Trên Railway

### Bước 1: Tạo PostgreSQL Database

1. **Vào Railway Dashboard** → Project của bạn
2. Click **"+ New"** (góc trên bên phải)
3. Chọn **"Database"** → **"Add PostgreSQL"**
4. Railway sẽ tạo PostgreSQL instance tự động

### Bước 2: Link Database Với Web Service

**Cách 1: Automatic (Khuyến nghị)**

1. Click vào **Web Service** (không phải Database)
2. Tab **"Variables"**
3. Click **"+ New Variable"** → **"Add Reference"**
4. Chọn:
   - **Service**: PostgreSQL (tên database vừa tạo)
   - **Variable**: `DATABASE_URL`
5. Railway sẽ tự động inject: `${{Postgres.DATABASE_URL}}`

**Cách 2: Manual**

1. Click vào **PostgreSQL service**
2. Tab **"Connect"** → Copy **"Postgres Connection URL"**
3. Click vào **Web Service** 
4. Tab **"Variables"** → Add:
   ```
   DATABASE_URL=<paste-url-here>
   ```

### Bước 3: Verify Variables

Trong Web Service → Variables tab, đảm bảo có:

```bash
# Required
DATABASE_URL=${{Postgres.DATABASE_URL}}  # hoặc URL đầy đủ
FLASK_ENV=production
SECRET_KEY=<your-secret-key>

# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password>
ADMIN_FULL_NAME=Administrator
ADMIN_EMAIL=admin@yourdomain.com
```

### Bước 4: Redeploy

1. **Sau khi thêm DATABASE_URL**, Railway tự động redeploy
2. Hoặc: Deployments tab → **"Redeploy"**

### Bước 5: Chạy Migrations

Sau khi app deploy thành công:

```bash
# Cài Railway CLI (nếu chưa)
npm install -g @railway/cli

# Login
railway login

# Link project
cd d:\github\club-web-app
railway link

# Chạy migrations
railway run flask db upgrade

# Seed data
railway run flask seed-db
```

**Hoặc qua Railway Dashboard:**
1. Service → **"Deployments"** → Click deployment mới nhất
2. Có button **"View Logs"** → Tìm **">_"** icon để mở shell
3. Chạy commands trong shell

---

## Kiểm Tra Kết Quả

### 1. Check Logs
```bash
railway logs
```

Nên thấy:
```
[INFO] Starting gunicorn...
[INFO] Booting worker with pid: xxx
[INFO] Worker listening at: http://0.0.0.0:xxxx
```

### 2. Test Database Connection

```bash
railway shell
```

Trong shell:
```python
python3
>>> import os
>>> print(os.getenv('DATABASE_URL'))
# Nên hiện: postgresql://user:pass@host:port/db
>>> exit()
```

### 3. Test App

Mở URL Railway: `https://<your-app>.up.railway.app`

---

## Troubleshooting

### Vẫn lỗi "Could not parse URL"

**Check:** DATABASE_URL có đúng format không?

```bash
railway run python -c "import os; print(os.getenv('DATABASE_URL'))"
```

Phải có format:
```
postgresql://user:password@host:port/database
```

### Database URL bị thiếu

**Nguyên nhân:** Database chưa được link với web service

**Fix:** Làm lại Bước 2 (Link Database)

### Lỗi "relation does not exist"

**Nguyên nhân:** Chưa chạy migrations

**Fix:**
```bash
railway run flask db upgrade
railway run flask seed-db
```

### Permission denied khi chạy migrations

**Nguyên nhân:** Database user không có quyền

**Fix:** 
- Railway PostgreSQL mặc định có full quyền
- Kiểm tra DATABASE_URL có đúng credentials

---

## Checklist

- [ ] PostgreSQL database đã được tạo trong Railway
- [ ] DATABASE_URL đã được set trong Web Service variables
- [ ] DATABASE_URL format: `postgresql://...`
- [ ] App đã redeploy sau khi thêm DATABASE_URL
- [ ] Migrations đã chạy: `railway run flask db upgrade`
- [ ] Seed data đã chạy: `railway run flask seed-db`
- [ ] App accessible và không có lỗi database

---

## Sau Khi Fix

App sẽ chạy với:
- ✅ PostgreSQL database
- ✅ Port động từ Railway
- ✅ Tất cả tables được tạo
- ✅ Admin account và sample data

Test bằng cách login với:
- Username: `admin`
- Password: `<ADMIN_PASSWORD bạn đã set>`

🎉 **Done!**
