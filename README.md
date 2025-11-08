# 🎓 Student Result Management System

A comprehensive web-based application built with Flask for managing student results. Admins can manage student data, subjects, and marks, while students can view their results by entering their roll number.

## ⚙️ Tech Stack

- **Backend**: Python (Flask Framework)
- **Database**: SQLite (with SQLAlchemy ORM)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: AWS EC2 (with Gunicorn + Nginx)

## 👤 User Roles

### 1. Admin
- Login to the dashboard
- Add, update, delete students, subjects, and marks
- View overall results

### 2. Student
- Enter roll number on the homepage
- View result details (subject-wise marks, total, percentage, and grade)

## 🔁 User Flow

### Admin Flow:
1. Visit `/admin/register` → Create a new admin account (or use default: `admin` / `admin123`)
2. Visit `/admin/login` → Login with credentials
3. Redirects to `/admin/dashboard`
4. From the dashboard, admin can:
   - Add new student
   - Add subjects
   - Add marks
   - View or delete records
5. Logout ends admin session

### Student Flow:
1. Visit homepage `/`
2. Enter roll number → Submit → View result page
3. If roll number is valid, display marks, total, percentage, and grade
4. If invalid, show "Result not found."

## 🗂️ Project Structure

```
student-result-management/
│
├── app.py                      # Main Flask app
├── models.py                   # SQLAlchemy models
├── static/
│   ├── css/style.css
│   └── js/script.js
├── templates/
│   ├── index.html
│   ├── result.html
│   ├── admin_register.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── add_student.html
│   ├── add_subject.html
│   ├── add_marks.html
│   └── view_results.html
├── database.db                 # SQLite database
├── requirements.txt
└── README.md
```

## 🧱 Database Models

### Admin Table
- `id` (Integer, Primary Key)
- `username` (String, Unique)
- `password` (String, Hashed)

### Student Table
- `id` (Integer, Primary Key)
- `roll_no` (String, Unique)
- `name` (String)
- `class_name` (String)

### Subject Table
- `id` (Integer, Primary Key)
- `name` (String, Unique)

### Marks Table
- `id` (Integer, Primary Key)
- `student_id` (ForeignKey to Student.id)
- `subject_id` (ForeignKey to Subject.id)
- `marks` (Integer, 0-100)

## 🧭 Flask Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Student search page |
| `/result` | POST | Show student result |
| `/admin/register` | GET/POST | Admin registration |
| `/admin/login` | GET/POST | Admin login |
| `/admin/dashboard` | GET | Admin dashboard |
| `/admin/add_student` | GET/POST | Add new student |
| `/admin/add_subject` | GET/POST | Add subject |
| `/admin/add_marks` | GET/POST | Add marks |
| `/admin/view_results` | GET | View all results |
| `/admin/logout` | GET | Logout |

## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd student-result-management
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔐 Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change the default admin password in production!

## 🧮 Grade Calculation

The grade is calculated based on percentage:

```python
percentage = (total_marks / (number_of_subjects * 100)) * 100

if percentage >= 90:
    grade = "A+"
elif percentage >= 75:
    grade = "A"
elif percentage >= 60:
    grade = "B"
elif percentage >= 50:
    grade = "C"
else:
    grade = "Fail"
```

## 🚀 Deployment on AWS EC2

### 1. Launch an EC2 instance
- Choose Ubuntu Server
- Configure security group to allow HTTP (80) and HTTPS (443) traffic

### 2. Connect to your EC2 instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 3. Install dependencies
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx -y
```

### 4. Clone and setup the application
```bash
git clone <repository-url>
cd student-result-management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### 5. Configure Gunicorn
Create `gunicorn_config.py`:
```python
bind = "127.0.0.1:8000"
workers = 3
```

### 6. Create a systemd service
Create `/etc/systemd/system/student-result.service`:
```ini
[Unit]
Description=Student Result Management System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/student-result-management
Environment="PATH=/home/ubuntu/student-result-management/venv/bin"
ExecStart=/home/ubuntu/student-result-management/venv/bin/gunicorn --config gunicorn_config.py app:app

[Install]
WantedBy=multi-user.target
```

### 7. Start the service
```bash
sudo systemctl start student-result
sudo systemctl enable student-result
```

### 8. Configure Nginx
Create `/etc/nginx/sites-available/student-result`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 9. Enable the site
```bash
sudo ln -s /etc/nginx/sites-available/student-result /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📝 Features

- ✅ Secure admin authentication with password hashing
- ✅ Student result viewing by roll number
- ✅ Complete CRUD operations for students, subjects, and marks
- ✅ Automatic grade calculation
- ✅ Responsive design
- ✅ Flash messages for user feedback
- ✅ Data validation on both client and server side

## 🔒 Security Notes

- Passwords are hashed using Werkzeug's password hashing
- Session management for admin authentication
- Input validation on all forms
- SQL injection protection via SQLAlchemy ORM

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created as part of a full-stack web development project.

---

**Note**: This is a development version. For production deployment, ensure to:
- Change the default admin credentials
- Use a strong SECRET_KEY
- Enable HTTPS
- Configure proper database backups
- Set up logging and monitoring

