# Railway Deployment - Tóm Tắt

## ✅ Files Đã Chuẩn Bị

- ✅ `Dockerfile` - Railway sẽ dùng để build
- ✅ `wsgi.py` - Entry point với PORT handling
- ✅ `requirements.txt` - Có psycopg2-binary cho PostgreSQL
- ✅ `app/config.py` - Có fix PostgreSQL URL

## 🚀 Làm Theo File Này

**👉 Đọc và làm theo:** `RAILWAY_DEPLOY_GUIDE.md`

## 📋 Tóm Tắt Nhanh 9 Bước

1. **Push code lên GitHub**
2. **Login Railway** → Deploy from GitHub
3. **Thêm PostgreSQL** database
4. **Set Environment Variables** (quan trọng nhất!)
   - `DATABASE_URL` = Reference từ Postgres
   - `FLASK_ENV`, `SECRET_KEY`, `ADMIN_PASSWORD`, etc.
5. **Set Start Command:**
   ```
   sh -c 'gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 wsgi:application'
   ```
6. **Redeploy**
7. **Chạy migrations:** `railway run flask db upgrade`
8. **Seed data:** `railway run flask seed-db`
9. **Test app!**

## ⚠️ Điểm Quan Trọng

### Start Command PHẢI đúng format:
```bash
sh -c 'gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 wsgi:application'
```

- Dùng `sh -c '...'` với **single quotes**
- `$PORT` sẽ được Railway inject tự động

### DATABASE_URL:

**Cách 1 (Khuyến nghị):** Add Reference
- Variables → New Variable → Add a Reference
- Service: Postgres
- Variable: DATABASE_URL

**Cách 2:** Copy/Paste URL
- Postgres → Connect → Copy URL
- Web Service → Variables → Add Variable
- Paste URL

## 🔧 Nếu Gặp Lỗi

| Lỗi | Fix |
|-----|-----|
| `$PORT is not valid` | Kiểm tra Start Command có đúng format không |
| `Could not parse URL` | DATABASE_URL chưa được set |
| `Worker failed to boot` | Thiếu environment variables |
| Build timeout | Đổi Builder sang Nixpacks |

## 📞 Hỗ Trợ

Đọc chi tiết: **RAILWAY_DEPLOY_GUIDE.md**

---

**🎯 Bắt đầu từ BƯỚC 1 trong RAILWAY_DEPLOY_GUIDE.md và làm tuần tự!**
