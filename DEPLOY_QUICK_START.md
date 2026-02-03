# Hướng Dẫn Nhanh: Deploy Lên Railway hoặc Render

## 📋 Tóm Tắt

Ứng dụng đã được cập nhật để **sẵn sàng deploy** lên Railway.app hoặc Render.com với PostgreSQL database.

---

## 🗄️ Database Được Sử Dụng

### Development (Local)
- **SQLite** - File database tại `instance/karate_club.db`
- Không cần cài đặt server
- Phù hợp cho development và testing

### Production (Railway/Render)
- **PostgreSQL** - Database server
- Tự động được tạo bởi Railway/Render
- Dữ liệu persistent, không mất khi redeploy
- Hỗ trợ concurrent connections tốt hơn

**App tự động phát hiện:** Nếu `DATABASE_URL` có PostgreSQL → dùng PostgreSQL, nếu không → dùng SQLite.

---

## 🚀 Hướng Dẫn Deploy Nhanh

### Phương Án 1: Railway.app (Khuyến Nghị)

**Ưu điểm:**
- ✅ $5 credit miễn phí/tháng
- ✅ PostgreSQL miễn phí vĩnh viễn
- ✅ Không sleep
- ✅ Có CLI mạnh mẽ

**Các bước:**

1. **Push code lên GitHub**
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

2. **Tạo project trên Railway**
   - Đăng nhập: https://railway.app
   - New Project → Deploy from GitHub → Chọn repo
   - Add PostgreSQL database

3. **Cấu hình Environment Variables**
   ```
   FLASK_ENV=production
   SECRET_KEY=<tạo-từ-python-secrets>
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=<mật-khẩu-mạnh>
   ADMIN_EMAIL=admin@yourdomain.com
   ```

4. **Khởi tạo database**
   ```bash
   railway run flask db upgrade
   railway run flask seed-db
   ```

5. **Xong!** App live tại `https://<name>.up.railway.app`

📖 **Hướng dẫn chi tiết:** [deploy_railway.md](file:///d:/github/club-web-app/.agent/workflows/deploy_railway.md)

---

### Phương Án 2: Render.com

**Ưu điểm:**
- ✅ Free tier
- ✅ Auto deploy từ GitHub
- ✅ SSL tự động

**Nhược điểm:**
- ⚠️ PostgreSQL chỉ free 90 ngày (sau đó $7/month)
- ⚠️ App sleep sau 15 phút không hoạt động

**Các bước:**

1. **Push code lên GitHub**
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Tạo PostgreSQL Database**
   - Đăng nhập: https://render.com
   - New → PostgreSQL → Free plan
   - Copy Database URL

3. **Tạo Web Service**
   - New → Web Service → Connect GitHub repo
   - Environment: Docker
   - Dockerfile Path: `./Dockerfile`

4. **Thêm Environment Variables**
   ```
   FLASK_ENV=production
   SECRET_KEY=<generated-key>
   DATABASE_URL=<paste-from-step-2>
   ADMIN_PASSWORD=<strong-password>
   ```

5. **Deploy & Initialize**
   - Render tự động build
   - Sau khi live, vào Shell:
   ```bash
   flask db upgrade
   flask seed-db
   ```

6. **Done!** App live tại `https://<name>.onrender.com`

📖 **Hướng dẫn chi tiết:** [deploy_render.md](file:///d:/github/club-web-app/.agent/workflows/deploy_render.md)

---

## 📦 Files Đã Tạo Cho Deployment

### Mới Thêm:
- ✅ `build.sh` - Build script cho Render
- ✅ `render.yaml` - Blueprint tự động cho Render
- ✅ `deploy_railway.md` - Hướng dẫn Railway chi tiết
- ✅ `deploy_render.md` - Hướng dẫn Render chi tiết

### Đã Cập Nhật:
- ✅ `requirements.txt` - Thêm `psycopg2-binary` cho PostgreSQL
- ✅ `config.py` - Fix PostgreSQL URL compatibility
- ✅ `wsgi.py` - Handle PORT environment variable
- ✅ `seed.py` - Dữ liệu mẫu với hệ thống đai mới (10 cấp)

---

## ⚙️ Các Thay Đổi Kỹ Thuật

### 1. PostgreSQL Support
```python
# config.py - Tự động fix URL format
if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
```

### 2. Port Handling
```python
# wsgi.py - Đọc PORT từ environment
port = int(os.environ.get("PORT", 8000))
application.run(host='0.0.0.0', port=port)
```

### 3. Database Driver
```txt
# requirements.txt
psycopg2-binary==2.9.9  # PostgreSQL driver
```

---

## 🎯 So Sánh Railway vs Render

| Tiêu chí | Railway | Render |
|----------|---------|--------|
| **Miễn phí** | $5 credit/tháng | 750 giờ/tháng |
| **Database** | PostgreSQL miễn phí | 90 ngày, sau $7/m |
| **Sleep** | ❌ Không | ✅ Sau 15 phút |
| **CLI** | ✅ Mạnh | ❌ Không có |
| **Dễ dùng** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Khuyến nghị** | Production | Testing ngắn hạn |

---

## 📝 Checklist Trước Khi Deploy

- [ ] Code đã push lên GitHub
- [ ] Đã tạo SECRET_KEY mạnh (dùng `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Đã đổi ADMIN_PASSWORD mặc định
- [ ] Đã kiểm tra requirements.txt có `psycopg2-binary`
- [ ] Đã test app chạy local bằng `flask run`
- [ ] Đã đọc hướng dẫn deploy tương ứng

---

## 🆘 Troubleshooting

### "Application failed to respond"
→ Kiểm tra wsgi.py đã handle PORT đúng chưa

### "Database connection failed"
→ Kiểm tra DATABASE_URL trong environment variables

### "No such table"
→ Chưa chạy migrations:
```bash
railway run flask db upgrade  # Railway
# hoặc
flask db upgrade  # Render Shell
```

### Uploaded files bị mất khi redeploy
→ Cần setup Persistent Disk (Railway) hoặc Render Disk

---

## 📚 Tài Liệu Đầy Đủ

1. **Railway:** [deploy_railway.md](file:///d:/github/club-web-app/.agent/workflows/deploy_railway.md)
2. **Render:** [deploy_render.md](file:///d:/github/club-web-app/.agent/workflows/deploy_render.md)
3. **VPS/Docker:** [deployment_guide.md](file:///d:/github/club-web-app/.agent/workflows/deployment_guide.md)
4. **Khởi tạo dữ liệu:** [data_initialization.md](file:///d:/github/club-web-app/.agent/workflows/data_initialization.md)

---

## ✅ Kết Luận

App của bạn **sẵn sàng deploy** lên:
- ✅ Railway.app (khuyến nghị cho production)
- ✅ Render.com (tốt cho testing)
- ✅ VPS với Docker (control tối đa)

Chọn platform phù hợp và làm theo hướng dẫn chi tiết trong các file .md tương ứng!

🎉 **Chúc bạn deploy thành công!**
