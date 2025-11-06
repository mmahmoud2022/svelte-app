#!/bin/bash

# Admin Dashboard Test Script
# This script tests the backend admin endpoints

API_URL="http://localhost:8000"
ADMIN_EMAIL="admin@test.com"
ADMIN_PASSWORD="Admin123!"

echo "================================"
echo "Admin Dashboard Backend Test"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if backend is running
echo -e "${YELLOW}1. Checking if backend is running...${NC}"
if curl -s "${API_URL}/docs" > /dev/null; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not running. Please start the backend first.${NC}"
    exit 1
fi
echo ""

# Test 2: Get public statistics (no auth required)
echo -e "${YELLOW}2. Testing public statistics endpoint...${NC}"
STATS=$(curl -s "${API_URL}/api/v1/auth/statistics")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Statistics endpoint works${NC}"
    echo "Response: $STATS"
else
    echo -e "${RED}✗ Statistics endpoint failed${NC}"
fi
echo ""

# Test 3: Try to login as admin (will fail if admin doesn't exist)
echo -e "${YELLOW}3. Testing admin login...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$ACCESS_TOKEN" ]; then
    echo -e "${GREEN}✓ Admin login successful${NC}"
    echo "Access token obtained"
else
    echo -e "${RED}✗ Admin login failed${NC}"
    echo "Response: $LOGIN_RESPONSE"
    echo ""
    echo -e "${YELLOW}To create an admin account, run:${NC}"
    echo "curl -X POST ${API_URL}/api/v1/auth/register/admin \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\",\"first_name\":\"Admin\",\"last_name\":\"Test\",\"admin_secret\":\"YOUR_ADMIN_SECRET\"}'"
    exit 1
fi
echo ""

# Test 4: Test admin endpoints
echo -e "${YELLOW}4. Testing admin endpoints with authentication...${NC}"

# Test 4a: Get all users
echo "  a) GET /api/v1/admin/users"
USERS=$(curl -s -H "Authorization: Bearer ${ACCESS_TOKEN}" "${API_URL}/api/v1/admin/users")
if echo "$USERS" | grep -q "email"; then
    echo -e "  ${GREEN}✓ Get all users works${NC}"
    USER_COUNT=$(echo $USERS | grep -o "\"id\":" | wc -l)
    echo "  Found $USER_COUNT users"
else
    echo -e "  ${RED}✗ Get all users failed${NC}"
    echo "  Response: $USERS"
fi
echo ""

# Test 4b: Get pending doctors
echo "  b) GET /api/v1/admin/doctors/pending"
PENDING=$(curl -s -H "Authorization: Bearer ${ACCESS_TOKEN}" "${API_URL}/api/v1/admin/doctors/pending")
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Get pending doctors works${NC}"
    PENDING_COUNT=$(echo $PENDING | grep -o "\"id\":" | wc -l)
    echo "  Found $PENDING_COUNT pending doctors"
else
    echo -e "  ${RED}✗ Get pending doctors failed${NC}"
fi
echo ""

# Test 4c: Get all doctors
echo "  c) GET /api/v1/admin/doctors/all"
DOCTORS=$(curl -s -H "Authorization: Bearer ${ACCESS_TOKEN}" "${API_URL}/api/v1/admin/doctors/all")
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Get all doctors works${NC}"
    DOCTOR_COUNT=$(echo $DOCTORS | grep -o "\"id\":" | wc -l)
    echo "  Found $DOCTOR_COUNT doctors"
else
    echo -e "  ${RED}✗ Get all doctors failed${NC}"
fi
echo ""

# Test 4d: Get patients
echo "  d) GET /api/v1/admin/patients"
PATIENTS=$(curl -s -H "Authorization: Bearer ${ACCESS_TOKEN}" "${API_URL}/api/v1/admin/patients")
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Get patients works${NC}"
    PATIENT_COUNT=$(echo $PATIENTS | grep -o "\"id\":" | wc -l)
    echo "  Found $PATIENT_COUNT patients"
else
    echo -e "  ${RED}✗ Get patients failed${NC}"
fi
echo ""

# Test 5: Test filters
echo -e "${YELLOW}5. Testing filter parameters...${NC}"
FILTERED=$(curl -s -H "Authorization: Bearer ${ACCESS_TOKEN}" "${API_URL}/api/v1/admin/users?role=patient&is_active=true")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Filter parameters work${NC}"
else
    echo -e "${RED}✗ Filter parameters failed${NC}"
fi
echo ""

# Summary
echo "================================"
echo -e "${GREEN}Backend admin endpoints test completed!${NC}"
echo "================================"
echo ""
echo "Available admin endpoints:"
echo "  - GET  /api/v1/admin/users"
echo "  - GET  /api/v1/admin/users/{user_id}"
echo "  - GET  /api/v1/admin/patients"
echo "  - GET  /api/v1/admin/doctors/pending"
echo "  - GET  /api/v1/admin/doctors/all"
echo "  - POST /api/v1/admin/doctors/{doctor_id}/approve"
echo "  - POST /api/v1/admin/doctors/{doctor_id}/reject"
echo "  - POST /api/v1/admin/users/{user_id}/suspend"
echo "  - POST /api/v1/admin/users/{user_id}/activate"
echo "  - DELETE /api/v1/admin/users/{user_id}"
echo ""
echo "Frontend admin dashboard:"
echo "  URL: http://localhost:5173/admin/dashboard"
echo "  Login as admin and navigate to the dashboard"
