# College Staff Scheduling System - Project Structure

## Folder Structure

\`\`\`
college-scheduling-system/
│
├── app.py                      # Main Flask application
├── college_staff.db            # SQLite database (auto-created)
├── requirements.txt            # Python dependencies
│
├── templates/                  # HTML templates
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── add_staff.html
│   ├── view_staff.html
│   ├── create_timetable.html
│   ├── view_timetable.html
│   ├── edit_timetable.html
│   ├── view_leaves.html
│   ├── view_logins.html
│   ├── staff_login.html
│   ├── staff_dashboard.html
│   ├── mark_attendance.html
│   └── view_schedule.html
│
└── README.md                   # This file

\`\`\`

## Database Schema

### Tables:

1. **admins**
   - id (PRIMARY KEY)
   - username (UNIQUE)
   - password (hashed)
   - email
   - created_at

2. **staff**
   - id (PRIMARY KEY)
   - name
   - email (UNIQUE)
   - password (hashed)
   - department
   - phone
   - is_active
   - created_at

3. **timetable**
   - id (PRIMARY KEY)
   - staff_id (FOREIGN KEY)
   - day
   - start_time
   - end_time
   - location
   - class_name
   - created_at

4. **attendance**
   - id (PRIMARY KEY)
   - staff_id (FOREIGN KEY)
   - date
   - status (present/absent)
   - reason
   - created_at

5. **login_logs**
   - id (PRIMARY KEY)
   - staff_id (FOREIGN KEY)
   - admin_id (FOREIGN KEY)
   - login_time
   - logout_time
   - session_type (staff/admin)

6. **leave_requests**
   - id (PRIMARY KEY)
   - staff_id (FOREIGN KEY)
   - leave_date
   - reason
   - status (pending/approved/rejected)
   - created_at

7. **reassignments**
   - id (PRIMARY KEY)
   - original_staff_id (FOREIGN KEY)
   - new_staff_id (FOREIGN KEY)
   - timetable_id (FOREIGN KEY)
   - leave_date
   - created_at

## Key Features

1. **Admin Portal**
   - Admin login/logout
   - Add new staff members
   - View all staff details
   - Create and edit timetables
   - Approve/reject leave requests
   - View real-time login activity
   - Monitor staff statistics

2. **Staff Portal**
   - Staff login/logout
   - Mark attendance (present/absent)
   - Apply for leave
   - View personal schedule
   - See reassignment notifications

3. **Auto-Rescheduling Logic**
   - When leave is approved, the system automatically:
     - Finds the staff member's assigned periods
     - Searches for available alternative staff (not on leave, not already scheduled)
     - Reassigns the periods to the alternative staff
     - Updates the timetable instantly
     - Logs the reassignment

4. **Real-Time Monitoring**
   - Admin dashboard shows live staff login status
   - Tracks login/logout times
   - Displays pending leave requests
   - Shows total and logged-in staff count

## Running the Project Locally

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- VS Code (optional, any text editor works)

### Installation Steps

1. **Create a project directory**
   \`\`\`bash
   mkdir college-scheduling
   cd college-scheduling
   \`\`\`

2. **Copy all files into the directory**
   - Place `app.py` in the root directory
   - Create a `templates` folder and add all HTML files
   - Place `requirements.txt` in the root directory

3. **Create a virtual environment** (Recommended)
   \`\`\`bash
   python -m venv venv
   \`\`\`

4. **Activate the virtual environment**
   - On Windows:
     \`\`\`bash
     venv\Scripts\activate
     \`\`\`
   - On macOS/Linux:
     \`\`\`bash
     source venv/bin/activate
     \`\`\`

5. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

6. **Run the application**
   \`\`\`bash
   python app.py
   \`\`\`

7. **Access the application**
   - Open your browser and go to: `http://localhost:5000`
   - Admin Portal: `http://localhost:5000/admin/login`
   - Staff Portal: `http://localhost:5000/staff/login`

### Default Admin Credentials
- **Username:** admin
- **Password:** admin123

## Deploying to Render.com

### Prerequisites
- GitHub account
- Render.com account (free tier available)

### Deployment Steps

1. **Prepare your repository on GitHub**
   \`\`\`bash
   git init
   git add .
   git commit -m "Initial commit: College scheduling system"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   \`\`\`

2. **Create a `.gitignore` file**
   \`\`\`
   venv/
   *.pyc
   __pycache__/
   *.db
   .DS_Store
   \`\`\`

3. **Push to GitHub**
   \`\`\`bash
   git push
   \`\`\`

4. **On Render.com Dashboard**
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name:** college-scheduling-system
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app`
   - Click "Create Web Service"

5. **Install Gunicorn** (add to requirements.txt)
   \`\`\`
   Flask==2.3.0
   Werkzeug==2.3.0
   gunicorn==21.2.0
   \`\`\`

6. **Wait for deployment**
   - Render will build and deploy your application
   - Your app will be available at: `https://your-app-name.onrender.com`

### Important Notes for Production

1. **Update Flask Configuration** in `app.py`:
   \`\`\`python
   app.run(debug=False)  # Changed from debug=True
   \`\`\`

2. **Environment Variables** on Render:
   - Set `FLASK_ENV=production`
   - You can add custom environment variables in Render dashboard

3. **Database Persistence**:
   - Render provides persistent storage for databases
   - SQLite file will persist between deployments

4. **Security**:
   - Change the `app.secret_key` to a random string
   - Consider implementing HTTPS (Render provides this by default)

## Usage Guide

### For Administrators

1. **Login** with credentials (admin/admin123)
2. **Add Staff** - Create new staff members with email and password
3. **Create Timetable** - Assign classes and periods to staff
4. **Manage Leaves** - View and approve/reject leave requests
5. **Monitor Activity** - Check real-time login activity and staff statistics

### For Staff Members

1. **Login** with your email and assigned password
2. **View Schedule** - See your assigned classes and periods
3. **Mark Attendance** - Record your presence or apply for leave
4. **Check Updates** - View if any classes were reassigned due to leaves

## Troubleshooting

### Common Issues

1. **"Module not found" error**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **"Address already in use" error**
   - The port 5000 is already in use
   - Change port in `app.py`: `app.run(debug=True, port=5001)`

3. **Database error**
   - Delete `college_staff.db` file
   - Run the app again to recreate the database

4. **Deployment issues on Render**
   - Check build logs in Render dashboard
   - Ensure all dependencies are in `requirements.txt`
   - Make sure `gunicorn` is in requirements.txt

## Support & Contact

For issues or questions, refer to Flask documentation:
https://flask.palletsprojects.com/

For Render deployment help:
https://render.com/docs

---

**Version:** 1.0
**Last Updated:** December 2025
