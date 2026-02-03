# CLB Karatedo Bách Khoa Hà Nội - Website

Website quản lý và chia sẻ thông tin cho Câu lạc bộ Karatedo Bách Khoa Hà Nội.

## 🎯 Tính năng chính

### Cho Admin
- ✅ Quản lý người dùng & phân quyền
- ✅ Duyệt/từ chối bài viết
- ✅ Quản lý bình luận
- ✅ Dashboard thống kê
- ✅ Quản lý media (ảnh/video)

### Cho Thành viên
- ✅ Đăng bài viết (text + ảnh + video)
- ✅ Upload ảnh (tối đa 5 ảnh/bài)
- ✅ Embed video (YouTube, Facebook, Google Drive)
- ✅ Quản lý hồ sơ cá nhân
- ✅ Bình luận bài viết

### Cho Khách
- ✅ Xem bài viết đã công khai
- ✅ Bình luận ẩn danh
- ✅ Tìm kiếm bài viết

## 🛠️ Tech Stack

- **Backend**: Flask 3.0, SQLAlchemy, Flask-Login
- **Frontend**: Jinja2, Bootstrap 5, Google Fonts (Inter)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Deployment**: Docker, Docker Compose, Nginx, Gunicorn

## 📦 Cài đặt & Chạy Local

### 1. Yêu cầu

- Python 3.11+
- pip
- virtualenv (khuyến nghị)

### 2. Clone repository

```bash
git clone <repository-url>
cd club-web-app
```

### 3. Tạo virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 5. Cấu hình môi trường

```bash
# Copy file mẫu
copy .env.example .env

# Chỉnh sửa .env với thông tin của bạn
```

### 6. Khởi tạo database

```bash
# Tạo database
flask db upgrade

# Tạo dữ liệu mẫu (admin + thành viên + bài viết)
flask seed-db
```

**Tài khoản mặc định:**
- **Admin**: username=`admin`, password=`Admin@123456`
- **Member**: username=`member1`, password=`Member@123`

⚠️ **QUAN TRỌNG**: Đổi mật khẩu admin ngay sau lần đăng nhập đầu tiên!

### 7. Chạy development server

```bash
flask run
```

Truy cập: http://localhost:5000

## 🐳 Deploy với Docker

### 1. Build & Run

```bash
# Copy và cấu hình .env
copy .env.example .env

# Build và start
docker-compose up -d --build
```

### 2. Khởi tạo database trong container

```bash
# Chạy migrations
docker-compose exec web flask db upgrade

# Seed dữ liệu
docker-compose exec web flask seed-db
```

### 3. Truy cập

- Website: http://localhost
- Admin: http://localhost/auth/login

### 4. Logs

```bash
# Xem logs
docker-compose logs -f web

# Stop
docker-compose down
```

## 📁 Cấu trúc thư mục

```
club-web-app/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration
│   ├── models/              # Database models
│   ├── blueprints/          # Route handlers
│   ├── services/            # Business logic
│   ├── middleware/          # Auth decorators
│   ├── utils/               # Helpers & validators
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS, JS, uploads
├── migrations/              # Alembic migrations
├── logs/                    # Application logs
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── requirements.txt
├── wsgi.py
└── README.md
```

## 🔐 Bảo mật

- ✅ Password hashing (PBKDF2-SHA256)
- ✅ CSRF protection
- ✅ SQL injection prevention (ORM)
- ✅ XSS prevention (Jinja2 auto-escape)
- ✅ File upload validation (MIME + extension)
- ✅ UUID-based file naming
- ✅ Role-based access control

## 📝 Quy trình làm việc

### Đăng bài viết (Member)

1. Đăng nhập → Dashboard
2. "Đăng bài mới"
3. Nhập tiêu đề + nội dung (hỗ trợ Markdown)
4. Upload ảnh / embed video (optional)
5. "Lưu bản nháp" hoặc "Gửi duyệt"

### Duyệt bài (Admin)

1. Đăng nhập Admin → Quản trị
2. "Bài viết chờ duyệt"
3. Xem preview
4. "Duyệt" → công khai ngay lập tức
5. "Từ chối" → nhập lý do

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## 🚀 Roadmap

### Phase 6: Enhanced Features (3 tháng)
- [ ] Lịch tập luyện & sự kiện
- [ ] Notification in-app
- [ ] Dashboard analytics
- [ ] Advanced search & filter
- [ ] Dark/light mode

### Phase 7: Mobile & API (6 tháng)
- [ ] RESTful API
- [ ] JWT authentication
- [ ] React Native mobile app
- [ ] Push notifications

### Phase 8: Scale & Optimize (9 tháng)
- [ ] Cloud storage (S3/R2)
- [ ] CDN integration
- [ ] Redis caching
- [ ] Elasticsearch

## 📞 Liên hệ & Hỗ trợ

- Email: karate@hcmut.edu.vn
- Phone: (+84) 123 456 789
- Address: Đại học Bách Khoa TP.HCM

## 📄 License

Copyright © 2024 CLB Karate Bách Khoa. All rights reserved.

---

**Xây dựng với ❤️ cho cộng đồng võ thuật Bách Khoa**
