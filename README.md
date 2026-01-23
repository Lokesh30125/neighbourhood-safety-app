# Neighbourhood Safety App - Deployment Guide

## 📁 Project Structure

```
neighbourhood-safety-app/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Procfile               # Process file for deployment
├── runtime.txt            # Python version
├── .gitignore            # Git ignore file
├── README.md             # This file
├── templates/            # HTML templates
│   ├── index.html
│   ├── signup.html
│   ├── otp.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── report.html
│   ├── route.html
│   ├── helpline.html
│   └── view_photos.html
└── static/              # Static files
    └── uploads/         # User uploaded files

```

---

## 🚀 Deployment Options

### Option 1: Deploy to Render (Recommended - FREE)

1. **Create a Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Push Code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

3. **Create New Web Service on Render**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: neighbourhood-safety-app
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Plan**: Free

4. **Add Environment Variables**
   - Go to "Environment" tab
   - Add:
     - `SECRET_KEY`: Generate a random string
     - `PYTHON_VERSION`: 3.11.7

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

---

### Option 2: Deploy to Railway (Easy - FREE)

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway auto-detects Flask app

3. **Add Environment Variable**
   - Go to "Variables" tab
   - Add `SECRET_KEY` with a random value

4. **Deploy**
   - Railway automatically deploys
   - Get your URL from the deployment page

---

### Option 3: Deploy to Heroku

1. **Install Heroku CLI**
   ```bash
   # On Mac
   brew tap heroku/brew && brew install heroku

   # On Ubuntu
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create neighbourhood-safety-app
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY="your-random-secret-key-here"
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Open App**
   ```bash
   heroku open
   ```

---

### Option 4: Deploy to PythonAnywhere

1. **Create Account**
   - Go to [pythonanywhere.com](https://www.pythonanywhere.com)
   - Sign up for free account

2. **Upload Files**
   - Use "Files" tab to upload all project files
   - Or clone from GitHub using Bash console

3. **Create Virtual Environment**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 myenv
   pip install -r requirements.txt
   ```

4. **Configure Web App**
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose "Manual configuration"
   - Select Python 3.10

5. **Set WSGI File**
   Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:
   ```python
   import sys
   path = '/home/yourusername/neighbourhood-safety-app'
   if path not in sys.path:
       sys.path.append(path)

   from app import app as application
   ```

6. **Reload Web App**

---

## 🔐 Security Considerations

### Generate Secure SECRET_KEY

```python
import secrets
print(secrets.token_hex(32))
```

Use this value for your `SECRET_KEY` environment variable.

### Important Security Notes

⚠️ **Before going to production:**

1. **Change the secret key** in environment variables
2. **Use HTTPS** (most platforms provide this automatically)
3. **Implement proper password hashing** (use `bcrypt` or `werkzeug.security`)
4. **Add rate limiting** to prevent abuse
5. **Validate all user inputs**
6. **Use environment variables** for sensitive data
7. **Implement proper SMS OTP** service (like Twilio)

---

## 📝 Environment Variables Required

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret | `a1b2c3d4e5f6...` |
| `DATABASE_PATH` | Database file path (optional) | `safety.db` |
| `PORT` | Port number (auto-set by platform) | `5000` |

---

## 🧪 Local Testing

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run app
python app.py
```

Visit: `http://localhost:5000`

---

## 📦 File Requirements

Make sure you have these files:
- ✅ `app.py`
- ✅ `requirements.txt`
- ✅ `Procfile`
- ✅ `runtime.txt`
- ✅ `.gitignore`
- ✅ `templates/` folder with all HTML files
- ✅ `static/` folder (will be created automatically)

---

## 🐛 Troubleshooting

### Issue: App crashes on deployment

**Solution**: Check logs
```bash
# Render
Check "Logs" tab in dashboard

# Railway
Click on deployment → "View Logs"

# Heroku
heroku logs --tail
```

### Issue: Database not persisting

**Solution**: Most free tiers have ephemeral storage
- Use PostgreSQL for production (available on most platforms)
- Or use persistent disk storage (paid feature)

### Issue: Static files not loading

**Solution**: Ensure `static/` folder exists and is committed to git

---

## 📞 Support

For issues:
1. Check deployment logs
2. Verify all files are uploaded
3. Check environment variables are set
4. Ensure database is initialized

---

## 🎉 Success!

Once deployed, your app will be available at:
- **Render**: `https://neighbourhood-safety-app.onrender.com`
- **Railway**: `https://neighbourhood-safety-app.up.railway.app`
- **Heroku**: `https://neighbourhood-safety-app.herokuapp.com`
- **PythonAnywhere**: `https://yourusername.pythonanywhere.com`

---

## 📄 License

This project is for educational purposes.

## 👥 Admin Access

Reset Database Password: `9012`

---

## 🔄 Updates

To update your deployed app:

```bash
git add .
git commit -m "Update message"
git push origin main
```

Most platforms auto-deploy on git push!