# Railway Troubleshooting Guide

## Lỗi: "$PORT is not a valid port number"

### Nguyên nhân
Railway inject biến `$PORT` vào container, nhưng Dockerfile đang dùng port cố định.

### Giải pháp ✅

Đã sửa `Dockerfile` để sử dụng biến `$PORT`:

```dockerfile
# Before (SAI)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", ...]

# After (ĐÚNG)
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120 wsgi:application
```

**Giải thích:**
- `${PORT:-8000}` - Dùng biến `$PORT` từ Railway, fallback về 8000 nếu không có
- Bỏ dấu ngoặc `["..."]` để shell có thể expand biến

### Sau khi sửa

1. **Commit và push:**
   ```bash
   git add Dockerfile
   git commit -m "Fix PORT binding for Railway"
   git push origin main
   ```

2. **Railway tự động redeploy**
   - Đợi deployment hoàn tất
   - Kiểm tra logs: Deploy Logs → Success

3. **Khởi tạo database (nếu chưa):**
   ```bash
   railway run flask db upgrade
   railway run flask seed-db
   ```

### Kiểm tra

```bash
# Xem logs
railway logs

# Test URL
curl https://<your-app>.up.railway.app
```

---

## Các Lỗi Railway Khác

### 1. "Database connection refused"

**Nguyên nhân:** DATABASE_URL chưa được set hoặc sai

**Giải pháp:**
1. Railway Dashboard → Variables
2. Thêm: `DATABASE_URL = ${{Postgres.DATABASE_URL}}`
3. Redeploy

### 2. "Module not found"

**Nguyên nhân:** Thiếu package trong `requirements.txt`

**Giải pháp:**
```bash
# Cập nhật requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### 3. "No such table: users"

**Nguyên nhân:** Chưa chạy migrations

**Giải pháp:**
```bash
railway run flask db upgrade
railway run flask seed-db
```

### 4. "Build failed"

**Kiểm tra:**
1. Deploy Logs → Xem error message
2. Thường do:
   - Syntax error trong code
   - Thiếu file cần thiết
   - Docker build error

### 5. Uploaded files bị mất

**Nguyên nhân:** Railway filesystem ephemeral

**Giải pháp:** Thêm Volume
1. Service Settings → Volumes
2. Add Volume: `/app/app/static/uploads`
3. Save & redeploy

---

## Tips Deploy Railway

### 1. Environment Variables Cần Thiết

```bash
FLASK_ENV=production
SECRET_KEY=<generated-key>
DATABASE_URL=${{Postgres.DATABASE_URL}}
ADMIN_PASSWORD=<strong-password>
```

### 2. Xem Real-time Logs

```bash
railway logs -f
```

### 3. Kết nối Database

```bash
railway connect Postgres
```

### 4. Open Shell trong Container

```bash
railway shell
```

### 5. Backup Database

```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

---

## Checklist Deploy Thành Công

- [x] Dockerfile sử dụng `${PORT:-8000}`
- [ ] Code đã push lên GitHub
- [ ] PostgreSQL database đã tạo
- [ ] Environment variables đã set đầy đủ
- [ ] Migrations đã chạy: `railway run flask db upgrade`
- [ ] Seed data đã tạo: `railway run flask seed-db`
- [ ] App accessible tại Railway URL
- [ ] Login admin hoạt động
- [ ] Upload ảnh hoạt động (nếu có Volume)

---

## Liên Hệ Support

Nếu vẫn gặp lỗi:
1. Check Railway logs: `railway logs`
2. Check deploy logs trong Railway Dashboard
3. Tham khảo: https://docs.railway.app
4. Railway Discord: https://discord.gg/railway
