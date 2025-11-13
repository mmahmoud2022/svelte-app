#!/usr/bin/env python3
"""
Validation script to verify backend-frontend endpoint synchronization
"""
import sys
import json
from pathlib import Path

def check_frontend_api_files():
    """Check that frontend API files exist and have expected structure"""
    frontend_path = Path("frontend/src/lib")
    
    checks = {
        "api.ts exists": (frontend_path / "api.ts").exists(),
        "api-doctor.ts exists": (frontend_path / "api-doctor.ts").exists(),
    }
    
    # Check for new API functions in api.ts
    if checks["api.ts exists"]:
        api_content = (frontend_path / "api.ts").read_text()
        checks["verifyEmail function"] = "verifyEmail" in api_content
        checks["resetPassword function"] = "resetPassword" in api_content
        checks["requestPasswordReset function"] = "requestPasswordReset" in api_content
        checks["changePassword function"] = "changePassword" in api_content
        checks["getAllDoctors function"] = "getAllDoctors" in api_content
        checks["getUserDetails function"] = "getUserDetails" in api_content
        checks["MessageResponse type"] = "MessageResponse" in api_content
    
    # Check that unused functions are removed from api-doctor.ts
    if checks["api-doctor.ts exists"]:
        api_doctor_content = (frontend_path / "api-doctor.ts").read_text()
        checks["createAppointment removed"] = "createAppointment" not in api_doctor_content
        checks["getPatientAppointments removed"] = "getPatientAppointments" not in api_doctor_content
    
    return checks

def check_new_pages():
    """Check that new pages exist"""
    routes_path = Path("frontend/src/routes")
    
    return {
        "VerifyEmail.svelte exists": (routes_path / "VerifyEmail.svelte").exists(),
        "RequestPasswordReset.svelte exists": (routes_path / "RequestPasswordReset.svelte").exists(),
        "ResetPassword.svelte exists": (routes_path / "ResetPassword.svelte").exists(),
    }

def check_routing():
    """Check that App.svelte has new routes"""
    app_file = Path("frontend/src/App.svelte")
    
    if not app_file.exists():
        return {"App.svelte exists": False}
    
    app_content = app_file.read_text()
    
    return {
        "App.svelte exists": True,
        "VerifyEmail route": "VerifyEmail" in app_content,
        "RequestPasswordReset route": "RequestPasswordReset" in app_content,
        "ResetPassword route": "ResetPassword" in app_content,
        "verify-email path": "/verify-email" in app_content,
        "forgot-password path": "/forgot-password" in app_content,
        "reset-password path": "/reset-password" in app_content,
    }

def check_backend_endpoints():
    """Check that backend endpoint files exist"""
    backend_path = Path("backend/app/api/v1/endpoints")
    
    return {
        "auth.py exists": (backend_path / "auth.py").exists(),
        "admin.py exists": (backend_path / "admin.py").exists(),
        "doctor.py exists": (backend_path / "doctor.py").exists(),
    }

def check_gitignore():
    """Check that .gitignore exists and has expected patterns"""
    gitignore = Path(".gitignore")
    
    if not gitignore.exists():
        return {".gitignore exists": False}
    
    content = gitignore.read_text()
    
    return {
        ".gitignore exists": True,
        "__pycache__ pattern": "__pycache__" in content,
        "node_modules pattern": "node_modules" in content,
        ".venv pattern": ".venv" in content,
        "dist pattern": "dist/" in content,
    }

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("Backend-Frontend Synchronization Validation")
    print("=" * 60)
    print()
    
    all_checks = {}
    
    # Run all checks
    checks_to_run = [
        ("Frontend API Files", check_frontend_api_files),
        ("New Pages", check_new_pages),
        ("Routing", check_routing),
        ("Backend Endpoints", check_backend_endpoints),
        (".gitignore", check_gitignore),
    ]
    
    for section_name, check_func in checks_to_run:
        print(f"{section_name}:")
        checks = check_func()
        all_checks.update(checks)
        
        for check_name, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
        print()
    
    # Summary
    total = len(all_checks)
    passed = sum(1 for v in all_checks.values() if v)
    failed = total - passed
    
    print("=" * 60)
    print(f"Summary: {passed}/{total} checks passed")
    print("=" * 60)
    
    if failed > 0:
        print(f"\n⚠️  {failed} checks failed")
        return 1
    else:
        print("\n✅ All validation checks passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
