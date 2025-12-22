# College Staff Scheduling System

A complete web-based staff scheduling solution with automatic rescheduling capabilities, built with Flask and SQLite.

## Features

### Admin Features
- ✅ Secure admin authentication
- ✅ Add and manage staff members
- ✅ Create and edit timetables
- ✅ Real-time monitoring of staff logins
- ✅ View staff attendance and leave requests
- ✅ Automatic leave approval with staff reassignment
- ✅ View total and logged-in staff count
- ✅ Complete staff details management

### Staff Features
- ✅ Secure staff login
- ✅ View personal schedule
- ✅ Mark attendance (present/absent)
- ✅ Apply for leave with auto-reassignment
- ✅ See schedule updates and reassignments

### System Features
- ✅ **Automatic Rescheduling**: When a staff member is approved for leave, the system automatically:
  - Identifies their assigned periods
  - Finds available alternative staff members
  - Reassigns classes to available staff
  - Updates the timetable in real-time
- ✅ Real-time login tracking
- ✅ Leave request management
- ✅ Persistent data storage with SQLite
- ✅ Responsive design for all devices

## Tech Stack

- **Backend:** Python Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS
- **Security:** Werkzeug password hashing

## Quick Start

### Local Development

\`\`\`bash
# 1. Clone/Download the project
cd college-scheduling

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py

# 6. Open browser
# Go to: http://localhost:5000
\`\`\`

### Default Credentials
- **Admin Username:** admin
- **Admin Password:** admin123

## Project Structure

\`\`\`
college-scheduling-system/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── college_staff.db            # SQLite database (auto-created)
├── templates/                  # HTML templates (11 pages)
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
└── README.md
\`\`\`

## Database Schema

### 7 Main Tables
1. **admins** - Admin users
2. **staff** - Staff members
3. **timetable** - Class schedules
4. **attendance** - Attendance records
5. **login_logs** - Login activity
6. **leave_requests** - Leave applications
7. **reassignments** - Schedule reassignments

## Auto-Rescheduling Logic

\`\`\`
Staff applies for leave
    ↓
Admin approves leave
    ↓
System checks staff's assigned periods
    ↓
Search for available staff:
  - Not on leave
  - Not already scheduled in that time slot
    ↓
If available staff found:
  - Create reassignment record
  - Update timetable with new staff
  - Staff can see reassignment on schedule
    ↓
Timetable updated instantly
\`\`\`

## Deployment to Render.com

### Prerequisites
- GitHub account
- Render.com account

### Steps

1. **Push code to GitHub**
   \`\`\`bash
   git init
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   \`\`\`

2. **Create Render Web Service**
   - Go to Render.com Dashboard
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn app:app`

3. **Update requirements.txt**
   \`\`\`
   Flask==2.3.0
   Werkzeug==2.3.0
   gunicorn==21.2.0
   \`\`\`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build and deployment
   - Access at: `https://your-app-name.onrender.com`

## Admin Dashboard

- **Total Staff Count** - Real-time stat
- **Logged-In Staff Count** - Active sessions
- **Recent Logins** - Last 10 login activities
- **Pending Leave Requests** - Quick approval/rejection

## Staff Management

- Add staff with department assignment
- Track phone numbers and emails
- Manage active/inactive status
- View complete staff directory

## Timetable Management

- Create schedule entries by day and time
- Assign classrooms/locations
- Specify subject/class names
- Edit existing schedule entries
- Auto-reassign on leave approval

## Attendance Tracking

- Mark daily attendance
- Apply for leave with reasons
- Track presence records
- Monitor leave history

## Real-Time Monitoring

- Track active login sessions
- View login timestamps
- Monitor staff activity
- Differentiate admin and staff logins

## Security Features

- Password hashing with Werkzeug
- Session management
- Protected routes (login required)
- Role-based access control

## Responsive Design

- Works on desktop, tablet, mobile
- Adaptive navigation
- Mobile-friendly forms and tables

## Troubleshooting

### Issue: "Module not found"
**Solution:** Ensure virtual environment is activated

### Issue: "Port 5000 already in use"
**Solution:** Change port in app.py or kill the process using port 5000

### Issue: Database errors
**Solution:** Delete `college_staff.db` and restart the app

### Issue: Render deployment failed
**Solution:** Check build logs, ensure gunicorn is in requirements.txt

## Future Enhancements

- Email notifications for leave approvals
- SMS reminders for schedule changes
- Advanced reporting and analytics
- Multi-year schedule planning
- API endpoints for mobile app
- User role customization
- Export schedules to PDF/Excel

## License

Open source - Available for educational and commercial use

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Flask documentation: https://flask.palletsprojects.com/
3. For Render issues: https://render.com/docs

---

**Created:** December 2025  
**Version:** 1.0  
**Fully Functional & Production Ready**
