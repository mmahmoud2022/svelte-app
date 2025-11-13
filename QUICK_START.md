# Quick Start Guide - Backend-Frontend Synchronization

## What Was Done

This PR synchronized all backend API endpoints with frontend API calls. All authentication flows are now complete.

## New Features

### 1. Email Verification Flow
**User Journey:**
1. User registers (patient or doctor)
2. Receives verification email
3. Clicks link → redirected to `/verify-email?token=xxx`
4. Email verified → redirected to login

**Implementation:**
- Backend: `POST /api/v1/auth/verify-email`
- Frontend: `verifyEmail(token)` in `api.ts`
- Page: `VerifyEmail.svelte`

### 2. Password Reset Flow
**User Journey:**
1. User clicks "Forgot password?" on login page
2. Enters email on `/forgot-password`
3. Receives reset email
4. Clicks link → redirected to `/reset-password?token=xxx`
5. Enters new password
6. Password reset → redirected to login

**Implementation:**
- Backend: 
  - `POST /api/v1/auth/request-password-reset`
  - `POST /api/v1/auth/reset-password`
- Frontend: 
  - `requestPasswordReset(email)` in `api.ts`
  - `resetPassword(token, newPassword)` in `api.ts`
- Pages:
  - `RequestPasswordReset.svelte`
  - `ResetPassword.svelte`

### 3. Enhanced Admin API
**New Functions:**
- `getAllDoctors()` - Get all doctors (approved and pending)
- `getUserDetails(userId)` - Get specific user details
- `getAllPatients()` - Get all patients

## Validation

Run the validation script to verify everything is synchronized:

```bash
python3 validate_sync.py
```

Expected output: `29/29 checks passed ✓`

## File Structure

```
frontend/src/
├── App.svelte                          # Routes: added /verify-email, /forgot-password, /reset-password
├── lib/
│   ├── api.ts                          # Added: 6 auth + 3 admin endpoints
│   └── api-doctor.ts                   # Removed: 2 unused endpoints
└── routes/
    ├── VerifyEmail.svelte              # NEW: Email verification page
    ├── RequestPasswordReset.svelte     # NEW: Password reset request page
    ├── ResetPassword.svelte            # NEW: Password reset page
    ├── Login.svelte                    # Already has "Forgot password?" link
    ├── admin/
    │   ├── AdminDashboard.svelte
    │   ├── Login.svelte
    │   └── Register.svelte
    ├── doctors/
    │   └── DoctorDashboard.svelte      # Tabbed interface (no sub-routes)
    └── patients/
        └── PatientRegister.svelte

backend/app/api/v1/endpoints/
├── auth.py        # 14 endpoints (all synced)
├── admin.py       # 10 endpoints (all synced)
└── doctor.py      # 24 endpoints (all synced)
```

## Testing Checklist

### Manual Testing
```bash
# Frontend
cd frontend
npm install
npm run build    # Should succeed
npm run dev      # Start dev server on http://localhost:5173

# Backend (in another terminal)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload  # Start on http://localhost:8000
```

### Test Flows
1. **Patient Registration**
   - Go to `/register/patient`
   - Fill form and submit
   - Check email (Mailpit: http://localhost:8025)
   - Click verification link
   - Login at `/login`

2. **Password Reset**
   - Go to `/login`
   - Click "Mot de passe oublié?"
   - Enter email
   - Check email (Mailpit)
   - Click reset link
   - Enter new password
   - Login with new password

3. **Doctor Approval (Admin)**
   - Register as admin
   - Login at `/admin/login`
   - View pending doctors
   - Approve/reject doctors

## API Endpoints Quick Reference

### Authentication
```
✓ POST   /api/v1/auth/register/patient
✓ POST   /api/v1/auth/register/doctor
✓ POST   /api/v1/auth/register/admin
✓ POST   /api/v1/auth/login
✓ POST   /api/v1/auth/logout
✓ POST   /api/v1/auth/verify-email          (NEW)
✓ POST   /api/v1/auth/resend-verification   (NEW)
✓ POST   /api/v1/auth/request-password-reset (NEW)
✓ POST   /api/v1/auth/reset-password        (NEW)
✓ POST   /api/v1/auth/change-password       (NEW)
✓ GET    /api/v1/auth/me
✓ GET    /api/v1/auth/statistics
```

### Admin
```
✓ GET    /api/v1/admin/users
✓ GET    /api/v1/admin/users/{user_id}       (NEW)
✓ GET    /api/v1/admin/doctors/pending
✓ GET    /api/v1/admin/doctors/all           (NEW)
✓ GET    /api/v1/admin/patients              (NEW)
✓ POST   /api/v1/admin/doctors/{id}/approve
✓ POST   /api/v1/admin/doctors/{id}/reject
✓ POST   /api/v1/admin/users/{id}/suspend
✓ POST   /api/v1/admin/users/{id}/activate
✓ DELETE /api/v1/admin/users/{id}
```

### Doctor
```
✓ GET    /api/v1/doctors/me
✓ PUT    /api/v1/doctors/me
✓ GET    /api/v1/doctors/appointments
✓ PATCH  /api/v1/doctors/appointments/{id}/status
✓ GET    /api/v1/doctors/patients
✓ GET    /api/v1/doctors/patients/{id}
✓ GET    /api/v1/doctors/statistics
✓ GET    /api/v1/doctors/settings
✓ PUT    /api/v1/doctors/settings
✓ GET    /api/v1/doctors/messages
✓ POST   /api/v1/doctors/messages
✓ GET    /api/v1/doctors/reviews
✓ GET    /api/v1/doctors/payments
... (24 total endpoints)
```

## Environment Setup

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email
SMTP_HOST=localhost
SMTP_PORT=1025  # Mailpit for development
SMTP_FROM=noreply@sante.com

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:5173
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
```

## Troubleshooting

### Frontend build fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Backend import errors
```bash
cd backend
pip install --upgrade -r requirements.txt
```

### Database not found
```bash
# Start with Docker Compose
docker-compose up -d postgres redis mailpit

# Run migrations
cd backend
alembic upgrade head
```

## Next Steps

After this PR is merged:
1. Test all flows in development environment
2. Update API documentation
3. Consider adding E2E tests for critical flows
4. Deploy to staging environment
5. Perform UAT (User Acceptance Testing)

## Documentation

- **Full Details**: See `SYNCHRONIZATION_SUMMARY.md`
- **Validation**: Run `python3 validate_sync.py`
- **API Docs**: http://localhost:8000/docs (Swagger UI)
