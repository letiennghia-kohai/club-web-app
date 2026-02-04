# Quick Railway Deployment Steps

## ⚠️ IMPORTANT: Don't run reset_database.py locally!

The script connects to Railway's PostgreSQL database, which is only accessible from Railway environment.

## ✅ Correct Way to Deploy

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Login and Link Project
```bash
railway login
railway link
```
Follow prompts to select your project.

### Step 3: Run Database Reset on Railway
```bash
railway run python reset_database.py
```
Type `YES` when prompted.

---

## Alternative: Use Local SQLite for Testing

If you want to test the reset script locally:

1. Make sure `.env` file uses SQLite:
```env
DATABASE_URL=sqlite:///instance/club.db
```

2. Then run locally:
```bash
python reset_database.py
```

---

## After Reset on Railway

Default login credentials:
- **Admin:** `admin` / `admin123`  
- **Member:** `member1` / `member123`

**⚠️ Change passwords immediately after first login!**
