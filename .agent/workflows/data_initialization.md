# Hướng Dẫn Khởi Tạo Dữ Liệu Lần Đầu

Hướng dẫn này giúp bạn khởi tạo database và dữ liệu ban đầu cho ứng dụng CLB Karatedo.

---

## Môi Trường Local (Development)

### Bước 1: Cài Đặt Dependencies

```bash
# Activate virtual environment (nếu chưa)
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Cài đặt packages
pip install -r requirements.txt
```

### Bước 2: Cấu Hình Environment Variables

Tạo file `.env` từ template:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Chỉnh sửa file `.env`:

```bash
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///instance/club.db

# Admin credentials (sẽ được tạo khi seed)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin@123456
ADMIN_FULL_NAME=Administrator
ADMIN_EMAIL=admin@karateclub.edu.vn
```

### Bước 3: Khởi Tạo Database

```bash
# Tạo database và chạy migrations
flask db upgrade
```

Lệnh này sẽ:
- Tạo thư mục `instance/` nếu chưa có
- Tạo file database SQLite `club.db`
- Tạo tất cả các bảng: users, posts, comments, media

### Bước 4: Seed Dữ Liệu Mẫu

```bash
# Tạo dữ liệu mẫu
flask seed-db
```

Lệnh này sẽ tạo:
- **1 Admin account**: 
  - Username: `admin`
  - Password: `Admin@123456`
  - Belt: Đen
  
- **3 Member accounts**: 
 - `member1` - Nguyễn Văn A - Đai Xanh đậm kuy1
  - `member2` - Trần Thị B - Đai Nâu kuy2
  - `member3` - Lê Văn C - Đai Xanh lá cây
  - Password cho tất cả: `Member@123`
  
- **2 Sample posts** từ admin

### Bước 5: Chạy Ứng Dụng

```bash
flask run
```

Truy cập: http://localhost:5000

**⚠️ QUAN TRỌNG**: Đổi mật khẩu admin ngay sau lần đăng nhập đầu tiên!

---

## Môi Trường Production (Docker)

### Bước 1: Cấu Hình Environment

```bash
# Tạo file .env
cp .env.example .env

# Chỉnh sửa với thông tin production
nano .env
```

**Cấu hình Production:**

```bash
FLASK_ENV=production
SECRET_KEY=<strong-random-secret-key>
DATABASE_URL=sqlite:///instance/club.db

# Thay đổi admin credentials mạnh hơn
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password-here>
ADMIN_FULL_NAME=Administrator
ADMIN_EMAIL=admin@yourdomain.com
```

**Tạo SECRET_KEY an toàn:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Bước 2: Build và Start Containers

```bash
# Build và start
docker-compose up -d --build

# Kiểm tra containers
docker-compose ps
```

### Bước 3: Khởi Tạo Database trong Container

```bash
# Chạy migrations
docker-compose exec web flask db upgrade

# Seed dữ liệu
docker-compose exec web flask seed-db
```

### Bước 4: Kiểm Tra

```bash
# Xem logs
docker-compose logs -f web

# Test truy cập
curl http://localhost
```

---

## Tạo Admin Account Thủ Công (Không dùng seed)

Nếu bạn không muốn dùng seed data, có thể tạo admin thủ công:

### Cách 1: Qua Flask Shell

```bash
# Local
flask shell

# Docker
docker-compose exec web flask shell
```

Trong Flask shell:

```python
from app import db
from app.models import User
from app.models.user import UserRole, UserStatus
from datetime import date

# Tạo admin
admin = User(
    username='admin',
    full_name='Administrator',
    email='admin@yourdomain.com',
    role=UserRole.ADMIN,
    status=UserStatus.ACTIVE,
    belt='Đen',
    join_date=date.today()
)
admin.set_password('YourStrongPassword123!')

db.session.add(admin)
db.session.commit()

print(f"Admin created: {admin.username}")
exit()
```

### Cách 2: Qua Python Script

Tạo file `create_admin.py`:

```python
#!/usr/bin/env python3
from app import create_app, db
from app.models import User
from app.models.user import UserRole, UserStatus
from datetime import date
import sys

def create_admin(username, password, email, full_name):
    app = create_app()
    with app.app_context():
        # Kiểm tra admin đã tồn tại chưa
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f"❌ User '{username}' đã tồn tại!")
            return False
        
        # Tạo admin mới
        admin = User(
            username=username,
            full_name=full_name,
            email=email,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            belt='Đen',
            join_date=date.today()
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ Admin '{username}' đã được tạo thành công!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: python create_admin.py <username> <password> <email> <full_name>")
        sys.exit(1)
    
    create_admin(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
```

Chạy script:

```bash
# Local
python create_admin.py admin StrongPass123! admin@domain.com "Administrator"

# Docker
docker-compose exec web python create_admin.py admin StrongPass123! admin@domain.com "Administrator"
```

---

## Quản Lý Database

### Reset Database (Làm mới hoàn toàn)

**⚠️ CẢNH BÁO: Lệnh này sẽ XÓA TẤT CẢ dữ liệu!**

```bash
# Local
# Xóa database
rm instance/club.db

# Tạo lại
flask db upgrade
flask seed-db

# Docker
docker-compose exec web rm /app/instance/club.db
docker-compose exec web flask db upgrade
docker-compose exec web flask seed-db
```

### Backup Database

```bash
# Local
cp instance/club.db instance/club_backup_$(date +%Y%m%d).db

# Docker
docker-compose exec web cp /app/instance/club.db /app/instance/club_backup_$(date +%Y%m%d).db

# Copy backup ra host
docker cp <container-id>:/app/instance/club_backup_*.db ./backups/
```

### Restore Database

```bash
# Local
cp instance/club_backup_20260203.db instance/club.db

# Docker
docker cp ./backups/club_backup_20260203.db <container-id>:/app/instance/club.db
docker-compose restart web
```

### Chạy Migrations Mới

Khi có thay đổi model:

```bash
# Tạo migration tự động
flask db migrate -m "Description of changes"

# Review file migration trong migrations/versions/

# Apply migration
flask db upgrade

# Docker
docker-compose exec web flask db migrate -m "Description"
docker-compose exec web flask db upgrade
```

---

## Migration Từ Hệ Thống Đai Cũ

Nếu bạn đang có database với hệ thống 8 đai cũ và muốn chuyển sang hệ thống 10 đai mới:

### Script Migration

Tạo file `migrate_belts.py`:

```python
from app import create_app, db
from app.models import User

# Mapping đai cũ sang đai mới
BELT_MIGRATION = {
    'Cam': 'Xanh nhạt',
    'Xanh lá': 'Xanh lá cây',
    'Xanh dương': 'Xanh đậm kuy2',
    'Nâu': 'Nâu kuy2',
    'Đỏ': 'Nâu kuy1',
    # Giữ nguyên
    'Trắng': 'Trắng',
    'Vàng': 'Vàng',
    'Đen': 'Đen'
}

def migrate_belts():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        updated = 0
        
        for user in users:
            if user.belt in BELT_MIGRATION:
                old_belt = user.belt
                user.belt = BELT_MIGRATION[old_belt]
                print(f"User {user.username}: {old_belt} → {user.belt}")
                updated += 1
        
        db.session.commit()
        print(f"\n✅ Đã cập nhật {updated} users")

if __name__ == '__main__':
    migrate_belts()
```

Chạy migration:

```bash
# Local
python migrate_belts.py

# Docker
docker cp migrate_belts.py <container-id>:/app/
docker-compose exec web python migrate_belts.py
```

---

## Kiểm Tra Database

### Xem tất cả users

```bash
flask shell
```

```python
from app.models import User

# Xem tất cả users
users = User.query.all()
for u in users:
    print(f"{u.username} - {u.full_name} - {u.belt} - {u.role}")

# Đếm users
print(f"Total users: {User.query.count()}")

# Đếm theo role
from app.models.user import UserRole
print(f"Admins: {User.query.filter_by(role=UserRole.ADMIN).count()}")
print(f"Members: {User.query.filter_by(role=UserRole.MEMBER).count()}")
```

### Xem tất cả posts

```python
from app.models import Post

posts = Post.query.all()
for p in posts:
    print(f"{p.title} - {p.status} - By: {p.author.full_name}")
```

---

## Troubleshooting

### Lỗi "database is locked"

```bash
# Stop tất cả processes đang dùng database
# Kiểm tra file lock
rm instance/club.db-journal

# Restart
flask run
```

### Lỗi "table already exists"

```bash
# Xóa database và tạo lại
rm instance/club.db
flask db upgrade
flask seed-db
```

### Lỗi "No module named 'app'"

```bash
# Kiểm tra PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Hoặc chạy với python -m
python -m flask db upgrade
```

---

## Checklist Khởi Tạo Dữ Liệu

- [ ] Đã tạo và cấu hình file `.env`
- [ ] Đã chạy `flask db upgrade` thành công
- [ ] Đã chạy `flask seed-db` hoặc tạo admin thủ công
- [ ] Đã test đăng nhập với admin account
- [ ] Đã đổi mật khẩu admin mặc định
- [ ] Đã backup database sau khi setup
- [ ] Đã tạo ít nhất 1 member account thật

---

## Lưu Ý Quan Trọng

1. **Luôn backup database** trước khi làm bất kỳ thay đổi lớn nào
2. **Đổi mật khẩu admin** ngay sau lần đăng nhập đầu tiên
3. **Không commit file `.env`** lên Git (đã có trong `.gitignore`)
4. **Sử dụng SECRET_KEY mạnh** trong production
5. **Test migrations** trên database backup trước khi apply lên production
