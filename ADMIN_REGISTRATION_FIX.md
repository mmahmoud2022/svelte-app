# Admin Registration - Quick Fix Reference

## ❌ Issue: 422 Unprocessable Entity Error

The error occurs because the admin registration endpoint expects specific field names.

## ✅ Correct Request Format

### Using cURL:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Admin123!",
    "first_name": "Admin",
    "last_name": "User",
    "admin_secret": "YOUR_ADMIN_SECRET"
  }'
```

### Required Fields:
- ✅ `email` (string, valid email format)
- ✅ `password` (string, min 8 chars, must include uppercase, lowercase, and number)
- ✅ `first_name` (string, min 1 char, max 100 chars)
- ✅ `last_name` (string, min 1 char, max 100 chars)
- ✅ `admin_secret` (string, must match ADMIN_SECRET in backend .env)

### Optional Fields:
- `phone` (string, max 20 chars)
- `gender` (string, max 20 chars)

## ⚠️ Common Mistakes

### ❌ Wrong:
```json
{
  "email": "admin@test.com",
  "password": "Admin123!",
  "full_name": "Admin User",  // ❌ Wrong field name
  "admin_secret": "secret"
}
```

### ✅ Correct:
```json
{
  "email": "admin@test.com",
  "password": "Admin123!",
  "first_name": "Admin",      // ✅ Separate first name
  "last_name": "User",         // ✅ Separate last name
  "admin_secret": "secret"
}
```

## 🔑 Getting Your Admin Secret

1. Check your backend `.env` file:
```bash
cd backend
grep ADMIN_SECRET .env
```

2. If not set, add it:
```bash
echo "ADMIN_SECRET=my-secure-secret-123" >> .env
```

3. Restart the backend after changing .env

## 🧪 Test Your Request

### Using Docker:
```bash
docker logs sante_backend 2>&1 | tail -20
```

### Check for these success indicators:
- Status code: `201 Created` (not 422)
- Response includes user data with `"role": "admin"`
- No validation errors in logs

## 📝 Password Requirements

Your password must:
- Be at least 8 characters long
- Contain at least one uppercase letter (A-Z)
- Contain at least one lowercase letter (a-z)
- Contain at least one number (0-9)

Examples:
- ✅ `Admin123!`
- ✅ `SecurePass1`
- ✅ `MyPassword2024`
- ❌ `admin123` (no uppercase)
- ❌ `ADMIN123` (no lowercase)
- ❌ `AdminPass` (no number)
- ❌ `Admin12` (too short)

## 🚀 Quick Test Command

Replace `YOUR_SECRET` with your actual admin secret:

```bash
curl -v -X POST http://localhost:8000/api/v1/auth/register/admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Admin123!",
    "first_name": "Admin",
    "last_name": "User",
    "admin_secret": "YOUR_SECRET"
  }'
```

The `-v` flag will show you detailed request/response information for debugging.

## ✅ Expected Success Response

```json
{
  "id": 1,
  "email": "admin@test.com",
  "full_name": "Admin User",
  "role": "ADMIN",
  "is_active": true,
  "email_verified": true,
  "admin_approved": true,
  "created_at": "2025-11-05T..."
}
```

## 🔧 Frontend Integration

The frontend API interface has been updated to match the backend:

```typescript
export interface AdminRegistrationData {
  email: string;
  password: string;
  first_name: string;      // ✅ Updated
  last_name: string;        // ✅ Updated
  phone?: string;           // ✅ Optional
  admin_secret: string;
}
```

If you're using the frontend to register admins programmatically, use:

```typescript
const adminData: AdminRegistrationData = {
  email: "admin@test.com",
  password: "Admin123!",
  first_name: "Admin",
  last_name: "User",
  admin_secret: "YOUR_SECRET"
};

const response = await registerAdmin(adminData);
```

## 📞 Need Help?

1. Verify your admin secret is set in `.env`
2. Check backend logs for detailed error messages
3. Ensure password meets all requirements
4. Verify JSON format is correct (no trailing commas, proper quotes)
5. Check that backend is running and accessible
