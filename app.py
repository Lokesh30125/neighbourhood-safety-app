from flask import Flask, render_template, request, redirect, session, jsonify, url_for, send_from_directory
import sqlite3
import os
from datetime import datetime
import secrets
import base64

app = Flask(__name__)

# Production secret key - use environment variable
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Ensure upload folder exists
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Database path
DATABASE = os.environ.get('DATABASE_PATH', 'safety.db')

def get_db_connection():
    """Create a database connection with proper settings"""
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with all required tables"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Create users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            firstname TEXT,
            lastname TEXT,
            mobile TEXT,
            state TEXT,
            district TEXT,
            village TEXT,
            photo TEXT,
            country TEXT
        )
    """)
    
    # Create incidents table
    c.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            image TEXT NOT NULL,
            description TEXT,
            place TEXT,
            latitude REAL,
            longitude REAL,
            time TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)
    
    # Create comments table
    c.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            comment_text TEXT NOT NULL,
            time TEXT NOT NULL,
            FOREIGN KEY (incident_id) REFERENCES incidents(id),
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# Static file serving route (explicit for production)
@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json
        username = data.get("username")
        password = data.get("password")
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            return jsonify({"success": True, "message": "Login successful"})
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/register", methods=["POST"])
def register():
    try:
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        mobile = request.form.get("mobile")
        district = request.form.get("district")
        village = request.form.get("village")
        username = request.form.get("username")
        password = request.form.get("password")
        country = request.form.get("country", "India")
        
        # Handle photo upload
        photo_path = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename:
                # Create safe filename
                filename = f"{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(file_path)
                # Store relative URL path
                photo_path = f"/static/uploads/{filename}"
        
        # Create user directly without OTP
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            c.execute("""
                INSERT INTO users (username, password, firstname, lastname, mobile, state, district, village, photo, country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                username,
                password,
                firstname,
                lastname,
                mobile,
                'Andhra Pradesh',
                district,
                village,
                photo_path,
                country
            ))
            conn.commit()
            conn.close()
            
            return jsonify({"success": True, "message": "Registration successful"})
        
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"success": False, "message": "Username already exists"}), 400
    
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        return redirect("/")
    
    username = session['username']
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT photo FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    user_photo = user[0] if user and user[0] else None
    
    return render_template("dashboard.html", username=username, user_photo=user_photo)

@app.route("/profile")
def profile():
    if 'username' not in session:
        return redirect("/")
    
    username = session['username']
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user:
        user_data = {
            'username': user[1],
            'firstname': user[3] or '',
            'lastname': user[4] or '',
            'mobile': user[5] or '',
            'state': user[6] or '',
            'district': user[7] or '',
            'village': user[8] or '',
            'photo': user[9] or ''
        }
        return render_template("profile.html", user=user_data)
    
    return redirect("/dashboard")

@app.route("/update_profile", methods=["POST"])
def update_profile():
    if 'username' not in session:
        return redirect("/")
    
    username = session['username']
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    mobile = request.form.get("mobile")
    state = request.form.get("state")
    district = request.form.get("district")
    village = request.form.get("village")
    
    # Handle photo upload
    photo_path = None
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo and photo.filename:
            filename = f"{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(file_path)
            photo_path = f"/static/uploads/{filename}"
    
    conn = get_db_connection()
    c = conn.cursor()
    
    if photo_path:
        c.execute("""
            UPDATE users 
            SET firstname = ?, lastname = ?, mobile = ?, state = ?, district = ?, village = ?, photo = ?
            WHERE username = ?
        """, (firstname, lastname, mobile, state, district, village, photo_path, username))
    else:
        c.execute("""
            UPDATE users 
            SET firstname = ?, lastname = ?, mobile = ?, state = ?, district = ?, village = ?
            WHERE username = ?
        """, (firstname, lastname, mobile, state, district, village, username))
    
    conn.commit()
    conn.close()
    
    return redirect("/profile")

@app.route("/report", methods=["GET", "POST"])
def report():
    if 'username' not in session:
        return redirect("/")
    
    if request.method == "POST":
        try:
            data = request.json
            username = session['username']
            
            # Handle base64 image data
            image_data = data.get("image")
            description = data.get("description", "")
            place = data.get("place", "Unknown")
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            
            # Save base64 image to file
            if image_data and image_data.startswith('data:image'):
                # Extract base64 data
                image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                
                # Create filename
                filename = f"incident_{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save image
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
                
                # Store relative URL path
                image_url = f"/static/uploads/{filename}"
            else:
                image_url = image_data  # Use as-is if already a URL
            
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO incidents (username, image, description, place, latitude, longitude, time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, image_url, description, place, latitude, longitude, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            
            return jsonify({"success": True, "message": "Report submitted"})
        
        except Exception as e:
            print(f"Report error: {e}")
            return jsonify({"success": False, "message": str(e)}), 500
    
    return render_template("report.html")

@app.route("/incidents/<place>")
def get_incidents(place):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, username, image, description, time, place, latitude, longitude
            FROM incidents
            WHERE place = ?
            ORDER BY time DESC
        """, (place,))
        
        incidents = []
        for row in c.fetchall():
            incidents.append({
                "id": row[0],
                "username": row[1],
                "image": row[2],  # This is already a URL path
                "description": row[3],
                "time": row[4],
                "place": row[5],
                "latitude": row[6],
                "longitude": row[7]
            })
        
        conn.close()
        return jsonify(incidents)
    
    except Exception as e:
        print(f"Error fetching incidents: {e}")
        return jsonify([])

@app.route("/all_incidents")
def get_all_incidents():
    """Get all incidents with location data for route mapping"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT 
                i.id,
                i.username,
                i.image,
                i.description,
                i.time,
                i.place,
                i.latitude,
                i.longitude,
                u.photo as user_photo
            FROM incidents i
            LEFT JOIN users u ON i.username = u.username
            WHERE i.latitude IS NOT NULL AND i.longitude IS NOT NULL
            ORDER BY i.time DESC
        """)
        
        incidents = []
        for row in c.fetchall():
            incidents.append({
                "id": row[0],
                "username": row[1],
                "image": row[2],  # Already a URL path
                "description": row[3],
                "time": row[4],
                "place": row[5],
                "latitude": row[6],
                "longitude": row[7],
                "user_photo": row[8]  # Already a URL path
            })
        
        conn.close()
        return jsonify(incidents)
    
    except Exception as e:
        print(f"Error fetching all incidents: {e}")
        return jsonify([])

@app.route("/recent_incidents")
def recent_incidents():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Get incidents from today
        c.execute("""
            SELECT id, username, image, description, time, place
            FROM incidents
            WHERE date(time) = date('now')
            ORDER BY time DESC
            LIMIT 10
        """)
        
        incidents = []
        for row in c.fetchall():
            incidents.append({
                "id": row[0],
                "username": row[1],
                "image": row[2],  # Already a URL path
                "description": row[3],
                "time": row[4],
                "place": row[5]
            })
        
        conn.close()
        return jsonify({"incidents": incidents, "count": len(incidents)})
    
    except Exception as e:
        print(f"Error fetching recent incidents: {e}")
        return jsonify({"incidents": [], "count": 0})

@app.route("/photos/<place>")
def get_photos(place):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Get incidents with user information
        c.execute("""
            SELECT 
                i.id,
                i.image,
                i.description,
                i.time,
                i.place,
                i.username,
                u.photo as user_photo
            FROM incidents i
            LEFT JOIN users u ON i.username = u.username
            WHERE i.place = ?
            ORDER BY i.time DESC
        """, (place,))
        
        incidents = []
        for row in c.fetchall():
            incident_id, image, desc, time, place, username, user_photo = row
            
            # Get comments for this incident
            c.execute("""
                SELECT 
                    c.username,
                    c.comment_text,
                    c.time
                FROM comments c
                WHERE c.incident_id = ?
                ORDER BY c.time ASC
            """, (incident_id,))
            
            comments = []
            for comment_row in c.fetchall():
                comments.append({
                    "username": comment_row[0],
                    "text": comment_row[1],
                    "time": comment_row[2]
                })
            
            incidents.append({
                "id": incident_id,
                "image": image,  # Already a URL path
                "description": desc,
                "time": time,
                "place": place,
                "username": username,
                "user_photo": user_photo,  # Already a URL path
                "comments": comments
            })
        
        conn.close()
        return jsonify(incidents)
    except Exception as e:
        print(f"Error fetching photos: {e}")
        return jsonify([])

@app.route("/add_comment", methods=["POST"])
def add_comment():
    try:
        if 'username' not in session:
            return jsonify({"success": False, "message": "Not logged in"}), 401
        
        data = request.json
        incident_id = data.get("incident_id")
        comment_text = data.get("comment_text")
        username = session['username']
        
        if not incident_id or not comment_text:
            return jsonify({"success": False, "message": "Missing data"}), 400
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Insert comment
        c.execute("""
            INSERT INTO comments (incident_id, username, comment_text, time)
            VALUES (?, ?, ?, ?)
        """, (incident_id, username, comment_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Comment posted"})
    except Exception as e:
        print(f"Error adding comment: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/current_user")
def get_current_user():
    try:
        if 'username' not in session:
            return jsonify({"username": None})
        
        username = session['username']
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT username, photo FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        
        if user:
            return jsonify({
                "username": user[0],
                "photo": user[1]  # Already a URL path
            })
        else:
            return jsonify({"username": None})
    except Exception as e:
        print(f"Error fetching current user: {e}")
        return jsonify({"username": None})

@app.route("/view_photos")
def view_photos():
    if 'username' not in session:
        return redirect("/")
    return render_template("view_photos.html")

@app.route("/route")
def route():
    if 'username' not in session:
        return redirect("/")
    return render_template("route.html")

@app.route("/helpline")
def helpline():
    if 'username' not in session:
        return redirect("/")
    return render_template("helpline.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    return redirect("/")

@app.route("/quick_login", methods=["POST"])
def quick_login():
    """Quick login using saved username from localStorage"""
    try:
        data = request.json
        username = data.get("username")
        
        if not username:
            return jsonify({"success": False, "message": "No username provided"}), 400
        
        # Check if user exists
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        
        if user:
            # Log the user in
            session['username'] = username
            return jsonify({"success": True, "message": "Quick login successful"})
        else:
            return jsonify({"success": False, "message": "User not found"}), 404
    
    except Exception as e:
        print(f"Quick login error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/reset_db", methods=["POST"])
def reset_database():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Drop all tables
        c.execute("DROP TABLE IF EXISTS users")
        c.execute("DROP TABLE IF EXISTS incidents")
        c.execute("DROP TABLE IF EXISTS comments")
        
        conn.commit()
        conn.close()
        
        # Reinitialize
        init_database()
        
        # Clear session
        session.clear()
        
        return "✅ Database reset successfully"
    
    except Exception as e:
        return f"Error resetting database: {e}", 500

# Health check endpoint for deployment platforms
@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
