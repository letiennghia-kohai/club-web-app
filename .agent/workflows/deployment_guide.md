---
description: Hướng dẫn deploy ứng dụng lên production
---

# Hướng Dẫn Deploy Ứng Dụng Lên Internet

Hướng dẫn này sẽ giúp bạn deploy ứng dụng CLB Karatedo lên môi trường production trên internet.

## Tùy Chọn Deployment

### 1. Deploy trên VPS/Cloud Server (Khuyến nghị)

Các nền tảng khuyến nghị:
- **DigitalOcean**: $5-10/tháng
- **Linode**: $5/tháng
- **Vultr**: $5/tháng
- **AWS Lightsail**: $3.5-5/tháng

### 2. Deploy trên PaaS

Các nền tảng miễn phí/giá rẻ:
- **Railway**: Miễn phí với $5 credit/tháng
- **Render**: Miễn phí tier
- **Fly.io**: Miễn phí tier

---

## Phương Án 1: Deploy trên VPS với Docker (Khuyến nghị)

### Bước 1: Chuẩn bị VPS

```bash
# SSH vào VPS
ssh root@your-server-ip

# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài đặt Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Cài đặt Docker Compose
sudo apt install docker-compose -y

# Cài đặt Git
sudo apt install git -y
```

### Bước 2: Clone Repository

```bash
# Clone code từ GitHub
git clone <your-repo-url> /opt/club-web-app
cd /opt/club-web-app
```

### Bước 3: Cấu Hình Environment

```bash
# Copy file .env.example
cp .env.example .env

# Chỉnh sửa file .env
nano .env
```

**Cấu hình quan trọng trong `.env`:**

```bash
# Flask configuration
FLASK_ENV=production
SECRET_KEY=<tạo-secret-key-mạnh-bằng-python-secrets>
DATABASE_URL=sqlite:///instance/club.db

# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<mật-khẩu-mạnh>
ADMIN_FULL_NAME=Administrator
ADMIN_EMAIL=admin@yourdomain.com

# Upload settings
MAX_CONTENT_LENGTH=10485760
UPLOAD_FOLDER=app/static/uploads

# Timezone
TIMEZONE=Asia/Ho_Chi_Minh
```

**Tạo SECRET_KEY mạnh:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Bước 4: Build và Deploy

```bash
# Build và khởi động containers
docker-compose up -d --build

# Kiểm tra containers đang chạy
docker-compose ps

# Xem logs
docker-compose logs -f web
```

### Bước 5: Khởi tạo Database

```bash
# Chạy migrations
docker-compose exec web flask db upgrade

# Seed dữ liệu ban đầu
docker-compose exec web flask seed-db
```

### Bước 6: Cấu Hình Domain và SSL

#### A. Trỏ Domain về VPS

Tại nhà cung cấp domain của bạn, tạo A record:
```
Type: A
Name: @ (hoặc www)
Value: <IP-của-VPS>
TTL: 3600
```

#### B. Cài đặt SSL với Let's Encrypt

```bash
# Cài đặt Certbot
sudo apt install certbot python3-certbot-nginx -y

# Cập nhật nginx.conf với domain của bạn
nano nginx.conf
# Thay đổi server_name từ _ thành yourdomain.com

# Restart nginx
docker-compose restart nginx

# Tạo SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Hoặc cấu hình SSL thủ công trong nginx.conf:**

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Bước 7: Tự động renew SSL

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot sẽ tự động renew, nhưng bạn có thể thêm cronjob
sudo crontab -e

# Thêm dòng này để renew SSL mỗi ngày
0 3 * * * certbot renew --quiet
```

---

## Phương Án 2: Deploy trên Railway.app (Đơn giản nhất)

### Bước 1: Tạo tài khoản Railway

Truy cập: https://railway.app và đăng ký

### Bước 2: Deploy từ GitHub

1. Click "New Project"
2. Chọn "Deploy from GitHub repo"
3. Chọn repository của bạn
4. Railway sẽ tự động detect và deploy

### Bước 3: Thêm Environment Variables

Trong Railway dashboard:
1. Click vào project → Settings → Variables
2. Thêm các biến:
   - `FLASK_ENV=production`
   - `SECRET_KEY=<your-secret-key>`
   - `ADMIN_USERNAME=admin`
   - `ADMIN_PASSWORD=<strong-password>`
   - `DATABASE_URL=sqlite:///instance/club.db`

### Bước 4: Khởi tạo Database

Railway cung cấp terminal:
```bash
flask db upgrade
flask seed-db
```

### Bước 5: Cấu hình Domain

Railway cung cấp domain miễn phí hoặc bạn có thể thêm custom domain.

---

## Phương Án 3: Deploy trên Render.com

### Bước 1: Tạo tài khoản

Truy cập: https://render.com và đăng ký

### Bước 2: Tạo Web Service

1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Cấu hình:
   - **Name**: club-karatedo
   - **Environment**: Docker
   - **Plan**: Free

### Bước 3: Environment Variables

Thêm trong Render dashboard:
- `FLASK_ENV=production`
- `SECRET_KEY=<generated-key>`
- `ADMIN_USERNAME=admin`
- `ADMIN_PASSWORD=<strong-password>`

### Bước 4: Deploy

Render sẽ tự động build và deploy. Sau khi deploy xong:

```bash
# Trong Render Shell
flask db upgrade
flask seed-db
```

---

## Bảo trì và Quản lý

### Update code mới

```bash
# Trên VPS
cd /opt/club-web-app
git pull origin main
docker-compose up -d --build

# Chạy migrations nếu có
docker-compose exec web flask db upgrade
```

### Backup Database

```bash
# Backup SQLite database
docker-compose exec web cp /app/instance/club.db /app/instance/club_backup_$(date +%Y%m%d).db

# Copy ra host
docker cp <container-id>:/app/instance/club_backup_*.db ./backups/
```

### Xem Logs

```bash
# Toàn bộ logs
docker-compose logs -f

# Chỉ web service
docker-compose logs -f web

# Logs trong file
tail -f logs/app.log
```

### Restart Services

```bash
# Restart toàn bộ
docker-compose restart

# Restart chỉ web service
docker-compose restart web
```

---

## Checklist Trước Khi Go Live

- [ ] Đã thay đổi `SECRET_KEY` mạnh
- [ ] Đã thay đổi mật khẩu admin mặc định
- [ ] `FLASK_ENV=production`
- [ ] SSL/HTTPS đã được cấu hình
- [ ] Database backup tự động
- [ ] Monitoring/logging đã setup
- [ ] Firewall đã cấu hình (chỉ mở port 80, 443, 22)
- [ ] Email thông báo lỗi đã cấu hình (nếu cần)

---

## Troubleshooting

### Lỗi "502 Bad Gateway"

```bash
# Kiểm tra web container
docker-compose logs web

# Restart web container
docker-compose restart web
```

### Lỗi Database

```bash
# Kiểm tra database file
docker-compose exec web ls -la /app/instance/

# Chạy lại migrations
docker-compose exec web flask db upgrade
```

### Lỗi Permission

```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/club-web-app/app/static/uploads
sudo chmod -R 755 /opt/club-web-app/app/static/uploads
```

---

## Liên hệ & Hỗ trợ

Nếu gặp vấn đề trong quá trình deploy, vui lòng liên hệ admin hoặc tạo issue trên GitHub repository.
