from httpx import AsyncClient

API = "/api/v1"
CREDS = {"email": "user@corp.com", "password": "S3cure!pass", "full_name": "Jane"}


async def _register_and_login(client: AsyncClient) -> dict[str, str]:
    await client.post(f"{API}/auth/register", json=CREDS)
    res = await client.post(
        f"{API}/auth/login",
        json={"email": CREDS["email"], "password": CREDS["password"]},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_register_login_me(client: AsyncClient):
    res = await client.post(f"{API}/auth/register", json=CREDS)
    assert res.status_code == 201
    assert res.json()["email"] == CREDS["email"]

    res = await client.post(
        f"{API}/auth/login",
        json={"email": CREDS["email"], "password": CREDS["password"]},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]

    res = await client.get(
        f"{API}/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["email"] == CREDS["email"]


async def test_me_requires_auth(client: AsyncClient):
    res = await client.get(f"{API}/users/me")
    assert res.status_code == 401


async def test_duplicate_email_conflict(client: AsyncClient):
    await client.post(f"{API}/auth/register", json=CREDS)
    res = await client.post(f"{API}/auth/register", json=CREDS)
    assert res.status_code == 409


async def test_weak_password_rejected(client: AsyncClient):
    res = await client.post(
        f"{API}/auth/register",
        json={"email": "w@corp.com", "password": "weak", "full_name": "W"},
    )
    assert res.status_code == 422


async def test_login_wrong_password(client: AsyncClient):
    await client.post(f"{API}/auth/register", json=CREDS)
    res = await client.post(
        f"{API}/auth/login",
        json={"email": CREDS["email"], "password": "WrongPass1!"},
    )
    assert res.status_code == 401


async def test_workspace_crud_flow(client: AsyncClient):
    headers = await _register_and_login(client)

    # Create
    res = await client.post(
        f"{API}/workspaces", json={"name": "Legal", "description": "docs"},
        headers=headers,
    )
    assert res.status_code == 201
    workspace_id = res.json()["id"]

    # List (member sees exactly one)
    res = await client.get(f"{API}/workspaces", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] == 1

    # Read
    res = await client.get(f"{API}/workspaces/{workspace_id}", headers=headers)
    assert res.status_code == 200

    # Update
    res = await client.patch(
        f"{API}/workspaces/{workspace_id}", json={"name": "Legal Team"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Legal Team"

    # Delete
    res = await client.delete(f"{API}/workspaces/{workspace_id}", headers=headers)
    assert res.status_code == 204


async def test_workspace_requires_auth(client: AsyncClient):
    res = await client.get(f"{API}/workspaces")
    assert res.status_code == 401
