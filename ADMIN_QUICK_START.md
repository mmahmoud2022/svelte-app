# 🚀 Quick Start Guide - Admin Dashboard

## Prerequisites
- Backend running on http://localhost:8000
- Frontend running on http://localhost:5173
- Admin secret configured in backend `.env` file

## Step 1: Create an Admin Account

### Option A: Using the Backend Directly

1. First, check your `.env` file in the backend directory for `ADMIN_SECRET`:
```bash
cd backend
grep ADMIN_SECRET .env
```

2. Create an admin account:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Admin123!",
    "first_name": "Admin",
    "last_name": "User",
    "admin_secret": "YOUR_ADMIN_SECRET_FROM_ENV"
  }'
```

### Option B: Using the Swagger UI

1. Go to http://localhost:8000/docs
2. Find `POST /api/v1/auth/register/admin`
3. Click "Try it out"
4. Fill in the request body:
```json
{
  "email": "admin@test.com",
  "password": "Admin123!",
  "first_name": "Admin",
  "last_name": "User",
  "admin_secret": "YOUR_ADMIN_SECRET_FROM_ENV"
}
```
5. Click "Execute"

## Step 2: Test Backend Endpoints (Optional)

Run the provided test script:
```bash
cd backend
./test_admin_endpoints.sh
```

This will verify all admin endpoints are working correctly.

## Step 3: Access the Admin Dashboard

1. Open your browser and go to: http://localhost:5173/login

2. Login with your admin credentials:
   - Email: `admin@test.com`
   - Password: `Admin123!`

3. You will be automatically redirected to: http://localhost:5173/admin/dashboard

4. You should see:
   - Statistics cards at the top
   - Tabs for different user views
   - User management table
   - Action buttons for each user

## Step 4: Test Admin Features

### Approve a Doctor
1. Create a doctor account (if you don't have one):
   - Go to http://localhost:5173/register/doctor
   - Fill in the registration form
   - Submit

2. In the Admin Dashboard:
   - Click on "Médecins en attente" tab
   - Find the new doctor
   - Click "✓ Approuver"
   - Confirm in the modal

### Suspend a User
1. Go to "Tous les utilisateurs" tab
2. Find a non-admin user
3. Click "⏸ Suspendre"
4. Enter a reason
5. Confirm

### Reactivate a User
1. Find a suspended user in the table
2. Click "▶ Activer"
3. Confirm

### Search Users
1. Type in the search box
2. Results filter in real-time
3. Works for email and name

## Troubleshooting

### Cannot Create Admin Account
**Problem**: Getting error "Invalid admin secret"
**Solution**: Check your `.env` file has `ADMIN_SECRET` set, or set it:
```bash
echo "ADMIN_SECRET=my-secure-secret-123" >> backend/.env
```
Then restart the backend.

### Cannot Access Dashboard
**Problem**: Redirects to login page
**Solution**: 
1. Make sure you're logged in as an admin
2. Check browser console for errors
3. Verify JWT token is in localStorage

### Backend Endpoints Not Working
**Problem**: Getting 404 or connection errors
**Solution**:
1. Make sure backend is running:
```bash
cd backend
python -m uvicorn app.main:app --reload
```
2. Check the API URL in frontend `.env`:
```bash
VITE_API_URL=http://localhost:8000
```

### Frontend Not Loading
**Problem**: White screen or errors
**Solution**:
1. Check npm dependencies are installed:
```bash
cd frontend
npm install
```
2. Restart dev server:
```bash
npm run dev
```
3. Check browser console for errors

## What You Can Do in the Admin Dashboard

### View Statistics
- Total users
- Total doctors  
- Total patients
- Pending doctor approvals

### Manage Users
- View all users
- Search by name or email
- Filter by role (Patient, Doctor, Admin)
- View user details

### Approve Doctors
- View pending doctor registrations
- Approve doctors (enables login, sends email)
- Reject doctors (deactivates account, sends email)

### User Account Management
- Suspend users (blacklists email, revokes tokens)
- Reactivate users (removes from blacklist)
- Delete users permanently (with warning)

### Security Features
- Cannot suspend admin accounts
- Cannot delete admin accounts
- Cannot suspend/delete your own account
- All actions require confirmation
- Email notifications sent to affected users

## Tips

1. **Use Search**: The search box filters in real-time, making it easy to find specific users

2. **Check Pending Tab**: Regularly check "Médecins en attente" to approve new doctors

3. **Suspend Before Delete**: Consider suspending users first before permanently deleting them

4. **Add Reasons**: Always provide clear reasons when suspending or rejecting to maintain good records

5. **Refresh Data**: Click the refresh button after making changes to ensure data is up-to-date

## Need Help?

- Check the full documentation: `ADMIN_DASHBOARD.md`
- View API documentation: http://localhost:8000/docs
- Run backend tests: `./backend/test_admin_endpoints.sh`

## Next Steps

Once you're comfortable with the admin dashboard, you can:
1. Customize email templates in `backend/app/templates/email_templates.py`
2. Adjust styling in `frontend/src/styles/admin.css`
3. Add more admin features as needed
4. Configure logging and monitoring for admin actions

Enjoy managing your healthcare platform! 🏥
