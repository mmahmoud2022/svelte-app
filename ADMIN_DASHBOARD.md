# Admin Dashboard - API Endpoints Documentation

## Backend Endpoints Available

### Admin Statistics
- **GET** `/api/v1/auth/statistics`
  - Public endpoint
  - Returns platform statistics

### Admin User Management

#### List Users
- **GET** `/api/v1/admin/users`
  - Requires: Admin authentication
  - Query params: `role`, `is_active`, `is_verified`, `admin_approved`, `skip`, `limit`
  - Returns: List of all users with filters

#### Get User Details
- **GET** `/api/v1/admin/users/{user_id}`
  - Requires: Admin authentication
  - Returns: Detailed user information

#### List Patients
- **GET** `/api/v1/admin/patients`
  - Requires: Admin authentication
  - Query params: `is_active`, `is_verified`, `skip`, `limit`
  - Returns: List of all patients

#### Suspend User
- **POST** `/api/v1/admin/users/{user_id}/suspend`
  - Requires: Admin authentication
  - Body: `{ "reason": "string" }`
  - Actions: Deactivates account, adds to blacklist, revokes tokens, sends email
  - Returns: AdminActionResponse

#### Activate User
- **POST** `/api/v1/admin/users/{user_id}/activate`
  - Requires: Admin authentication
  - Actions: Reactivates account, removes from blacklist, sends email
  - Returns: AdminActionResponse

#### Delete User
- **DELETE** `/api/v1/admin/users/{user_id}`
  - Requires: Admin authentication
  - Actions: Permanently deletes user, adds to blacklist, deletes tokens
  - Returns: AdminActionResponse
  - ⚠️ WARNING: Irreversible action

### Doctor Approval Management

#### Get Pending Doctors
- **GET** `/api/v1/admin/doctors/pending`
  - Requires: Admin authentication
  - Returns: List of doctors awaiting approval

#### Get All Doctors
- **GET** `/api/v1/admin/doctors/all`
  - Requires: Admin authentication
  - Returns: List of all doctors (approved and pending)

#### Approve Doctor
- **POST** `/api/v1/admin/doctors/{doctor_id}/approve`
  - Requires: Admin authentication
  - Actions: Approves doctor account, sends approval email
  - Returns: AdminActionResponse

#### Reject Doctor
- **POST** `/api/v1/admin/doctors/{doctor_id}/reject`
  - Requires: Admin authentication
  - Actions: Deactivates account, sends rejection email
  - Returns: AdminActionResponse

## Frontend Implementation

### Components Created

1. **AdminDashboard.svelte** (`/frontend/src/routes/AdminDashboard.svelte`)
   - Main admin dashboard component
   - Features:
     - Statistics cards (total users, doctors, patients, pending doctors)
     - Tabbed interface (Pending Doctors, All Users, Patients, Doctors)
     - User table with search functionality
     - Action buttons (Approve, Reject, Suspend, Activate, Delete)
     - Confirmation modals
     - Success/error message notifications
     - Auto-refresh capability

2. **admin.css** (`/frontend/src/styles/admin.css`)
   - Complete styling for admin dashboard
   - Responsive design
   - Professional healthcare color scheme
   - Smooth animations and transitions

### Routes Added

- `/admin` → AdminDashboard
- `/admin/dashboard` → AdminDashboard

### API Functions Added

All admin API functions are available in `/frontend/src/lib/api.ts`:
- `getAllUsers()`
- `getPendingDoctors()`
- `approveDoctor(doctorId)`
- `rejectDoctor(doctorId, reason)`
- `suspendUser(userId, reason)`
- `activateUser(userId)`
- `deleteUser(userId)`
- `getStatistics()`

## Access Control

The admin dashboard checks for:
1. User must be logged in
2. User role must be 'ADMIN'
3. If not, redirects to login page

All backend endpoints use the `require_admin` dependency which:
1. Verifies authentication token
2. Checks user role === ADMIN
3. Returns 403 Forbidden if not admin

## Features

### Dashboard Statistics
- Total Users
- Total Doctors
- Total Patients  
- Pending Doctor Approvals

### User Management
- View all users with filtering
- Search by name or email
- Filter by role (Patient, Doctor, Admin)
- Suspend/Activate accounts
- Delete users permanently
- View user details

### Doctor Approval Workflow
- View pending doctor registrations
- Approve doctors (sends approval email)
- Reject doctors (sends rejection email, deactivates account)
- All approved doctors show in doctors list

### Actions with Confirmation
- Approve Doctor: Enables login, sends email
- Reject Doctor: Deactivates account, sends email
- Suspend User: Deactivates, blacklists email, revokes tokens, sends email
- Activate User: Reactivates, removes from blacklist, sends email
- Delete User: Permanent deletion, blacklists email, sends email

## Security Features

- Cannot suspend or delete admin accounts
- Cannot suspend or delete own account
- All actions are logged with admin email
- Email notifications sent for all major actions
- Tokens revoked on suspension
- Email blacklisting on suspension/deletion

## Testing the Admin Dashboard

### 1. Create an Admin Account
```bash
# Using the backend API
curl -X POST http://localhost:8000/api/v1/auth/register/admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123!",
    "first_name": "Admin",
    "last_name": "User",
    "admin_secret": "your-admin-secret-from-env"
  }'
```

### 2. Login as Admin
- Go to `/login`
- Enter admin credentials
- Will redirect to `/admin/dashboard`

### 3. Test Features
- View pending doctors
- Approve/reject doctor accounts
- Search and filter users
- Suspend/activate user accounts
- View statistics

## Next Steps

Optional enhancements:
1. Add pagination for large user lists
2. Add sorting by columns
3. Add export to CSV functionality
4. Add audit log viewer
5. Add user activity monitoring
6. Add email template customization
7. Add bulk actions (approve multiple doctors)
8. Add advanced search filters
