import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Verify that the base health check endpoint is operational."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


@pytest.mark.asyncio
async def test_user_registration_and_login(async_client: AsyncClient):
    """Test student registration and subsequent login token retrieval."""
    # 1. Register Student
    signup_payload = {
        "email": "test_student_1@campus.edu",
        "password": "Password123!",
        "full_name": "Test Student One",
        "role": "STUDENT",
        "uid": "STU1001",
    }
    signup_res = await async_client.post("/api/v1/auth/signup", json=signup_payload)
    assert signup_res.status_code == 201
    assert signup_res.json()["email"] == "test_student_1@campus.edu"

    # 2. Login
    login_payload = {
        "email": "test_student_1@campus.edu",
        "password": "Password123!",
    }
    login_res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()
    assert login_res.json()["token_type"].lower() == "bearer"


@pytest.mark.asyncio
async def test_complaint_creation_and_ai_triage(async_client: AsyncClient):
    """Test submitting a complaint and verifying automated AI field enrichment."""
    # 1. Register & Login as Admin
    admin_signup = {
        "email": "admin_triage@campus.edu",
        "password": "AdminPassword123!",
        "full_name": "Admin Tester",
        "role": "ADMIN",
        "uid": "ADM1001",
    }
    await async_client.post("/api/v1/auth/signup", json=admin_signup)

    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin_triage@campus.edu", "password": "AdminPassword123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Complaint
    complaint_payload = {
        "title": "Severe pipe leakage in 2nd floor restroom",
        "description": "Water overflowing from main supply line near sinks.",
        "location": "Science Block, Restroom 2A",
    }
    create_res = await async_client.post(
        "/api/v1/complaints/",
        json=complaint_payload,
        headers=headers,
    )
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["title"] == complaint_payload["title"]
    assert data["category"] in ["Plumbing", "Facility", "Unclassified"]
    assert data["priority"] in ["HIGH", "CRITICAL", "MEDIUM", "LOW"]


@pytest.mark.asyncio
async def test_rbac_status_update(async_client: AsyncClient):
    """Verify role-based access control: Students cannot update status; Admins can."""
    # 1. Create & Login Student
    student_signup = {
        "email": "student_rbac_test@campus.edu",
        "password": "Password123!",
        "full_name": "Student RBAC",
        "role": "STUDENT",
        "uid": "STU2001",
    }
    await async_client.post("/api/v1/auth/signup", json=student_signup)
    student_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "student_rbac_test@campus.edu", "password": "Password123!"},
    )
    student_token = student_login.json()["access_token"]

    # 2. Create & Login Admin
    admin_signup = {
        "email": "admin_rbac_test@campus.edu",
        "password": "Password123!",
        "full_name": "Admin RBAC",
        "role": "ADMIN",
        "uid": "ADM2001",
    }
    await async_client.post("/api/v1/auth/signup", json=admin_signup)
    admin_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin_rbac_test@campus.edu", "password": "Password123!"},
    )
    admin_token = admin_login.json()["access_token"]

    # 3. Create a ticket as Student
    create_res = await async_client.post(
        "/api/v1/complaints/",
        json={"title": "Light bulb flickering", "description": "Flickering in Room 101", "location": "Room 101"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert create_res.status_code == 201
    complaint_id = create_res.json()["id"]

    # 4. Student attempts status update -> Expected: 403 Forbidden
    student_patch = await async_client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={"status": "RESOLVED"},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert student_patch.status_code == 403

    # 5. Admin updates status -> Expected: 200 OK
    admin_patch = await async_client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={"status": "RESOLVED"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_patch.status_code == 200
    assert admin_patch.json()["status"] == "RESOLVED"