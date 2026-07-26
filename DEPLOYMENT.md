# GoalFit-AI Pro — Production Deployment Guide for Render

This guide provides step-by-step instructions to deploy **GoalFit-AI Pro** to **Render** with a Cloud MySQL database.

---

## 1. Quick Technical Summary

- **Framework**: Python 3.12 + Flask
- **WSGI Production Server**: Gunicorn (`gunicorn app:app`)
- **Database Engine**: MySQL (`mysql-connector-python`)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

---

## 2. Cloud MySQL Database Options

Render Web Services host Linux containers, but Render does not offer managed native MySQL. You can connect your Render app to any external MySQL provider:

### Recommended Free/Low-Cost MySQL Cloud Options:
1. **Aiven MySQL** ([aiven.io](https://aiven.io)) — Free tier available with standard MySQL.
2. **Clever Cloud** ([clever-cloud.com](https://www.clever-cloud.com)) — Provides free MySQL add-on databases.
3. **Railway MySQL** ([railway.app](https://railway.app)) — One-click MySQL database plugin.
4. **AWS RDS / PlanetScale / Supabase** — Enterprise or cloud MySQL-compatible database hosts.

---

## 3. Step-by-Step Render Web Service Deployment

### Step A: Push Project to GitHub
Ensure all updated files are committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "Prepare Flask application for Render deployment"
git push origin main
```

### Step B: Create Web Service on Render
1. Log into **[dashboard.render.com](https://dashboard.render.com)**.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository: **`harshpdcode/GoalFit-AI-Pro`**.
4. Configure service settings:
   - **Name**: `goalfit-ai-pro`
   - **Region**: Select closest region (e.g. Singapore / Frankfurt / Oregon)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

---

## 4. Environment Variables Configuration

In your Render Dashboard, go to your Web Service -> **Environment** tab, and add the following keys:

| Environment Variable | Recommended Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | *(Generate Random Key)* | Key for securing user session cookies. |
| `FLASK_DEBUG` | `false` | Disables debug mode in production. |
| `DB_HOST` | `your-db-host.com` | Hostname of your Cloud MySQL server. |
| `DB_USER` | `db_username` | MySQL database user. |
| `DB_PASSWORD` | `db_password` | MySQL database password. |
| `DB_NAME` | `goalfit_ai` | Name of your database schema. |
| `DB_PORT` | `3306` (or custom port) | MySQL port (e.g., 3306, 13306, 25060). |
| `RAZORPAY_KEY_ID` | `rzp_live_xxx` *(Optional)* | Razorpay Public Key ID. |
| `RAZORPAY_KEY_SECRET` | `secret_xxx` *(Optional)* | Razorpay Private Key Secret. |

*(Alternative)*: If your cloud database provider provides a single URL string, set `DATABASE_URL` = `mysql://user:pass@host:port/dbname`.

---

## 5. Initializing Database Schema & Seed Data

Once your Render Web Service and Cloud Database are connected:

### Option A: Shell Execution from Render Dashboard
1. Go to your Web Service on Render.
2. Click **Shell** (top right toolbar).
3. Run schema creation and seed scripts:
   ```bash
   python setup_db.py
   python seed_data.py
   ```

### Option B: Local Initialization to Remote DB
You can also run schema setup locally targeting your Cloud Database:
```bash
# In your local terminal, temporarily set Cloud DB variables:
$env:DB_HOST="your-db-host.com"
$env:DB_USER="db_username"
$env:DB_PASSWORD="db_password"
$env:DB_NAME="goalfit_ai"
python setup_db.py
python seed_data.py
```

---

## 6. Verifying Deployment Success

1. Visit your live Render URL (e.g., `https://goalfit-ai-pro.onrender.com`).
2. Test features:
   - User Registration / Login (`auth`)
   - Health Profile & BMI Engine (`health`, `bmi`)
   - AI Predictions & Step Recommendations (`prediction`, `dashboard`)
   - Diet & Workout Generation (`diet`, `workout`)
   - Water Hydration Tracker (`water`)
   - Professional Marketplace & Trainer Dashboard (`marketplace`, `pro_bp`)
   - PDF Download (`pdf_generator`)

---

## 7. Troubleshooting Common Deployment Questions

- **Render Free Tier Spin-Down**: Render free web services go to sleep after 15 minutes of inactivity. The first request after sleep may take ~30–50 seconds to boot up. This is normal behavior for Render free tier.
- **Uploaded Images on Free Tier**: Files saved in `static/images/progress_photos/` will be reset on container restart unless a Render Persistent Disk is attached. For persistent long-term media storage in production, AWS S3 or Cloudinary is recommended.
