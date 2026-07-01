from httpx import AsyncClient

API = "/api/v1"
PW = "S3cure!pass"


async def _register(client: AsyncClient, email: str) -> None:
    await client.post(
        f"{API}/auth/register",
        json={"email": email, "password": PW, "full_name": "User"},
    )


async def _login(client: AsyncClient, email: str) -> dict[str, str]:
    res = await client.post(f"{API}/auth/login", json={"email": email, "password": PW})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


async def _register_login(client: AsyncClient, email: str) -> dict[str, str]:
    await _register(client, email)
    return await _login(client, email)


async def test_membership_and_tag_authorization(client: AsyncClient):
    owner = await _register_login(client, "owner@corp.com")
    await _register(client, "editor@corp.com")
    editor = await _login(client, "editor@corp.com")
    await _register(client, "viewer@corp.com")
    viewer = await _login(client, "viewer@corp.com")
    outsider = await _register_login(client, "outsider@corp.com")

    workspace_id = (
        await client.post(f"{API}/workspaces", json={"name": "WS"}, headers=owner)
    ).json()["id"]

    # Owner adds an editor and a viewer.
    res = await client.post(
        f"{API}/workspaces/{workspace_id}/members",
        json={"email": "editor@corp.com", "role": "editor"},
        headers=owner,
    )
    assert res.status_code == 201
    res = await client.post(
        f"{API}/workspaces/{workspace_id}/members",
        json={"email": "viewer@corp.com", "role": "viewer"},
        headers=owner,
    )
    assert res.status_code == 201

    # Member list has owner + editor + viewer.
    res = await client.get(f"{API}/workspaces/{workspace_id}/members", headers=owner)
    assert res.status_code == 200
    assert len(res.json()) == 3

    # Outsider cannot even see the workspace (hidden as 404).
    res = await client.get(f"{API}/workspaces/{workspace_id}", headers=outsider)
    assert res.status_code == 404

    # Editor (write role) can create a tag.
    res = await client.post(
        f"{API}/workspaces/{workspace_id}/tags",
        json={"name": "legal", "color": "#3B82F6"},
        headers=editor,
    )
    assert res.status_code == 201

    # Viewer (read-only) cannot create a tag.
    res = await client.post(
        f"{API}/workspaces/{workspace_id}/tags",
        json={"name": "finance"},
        headers=viewer,
    )
    assert res.status_code == 403

    # Any member can list tags.
    res = await client.get(f"{API}/workspaces/{workspace_id}/tags", headers=viewer)
    assert res.status_code == 200
    assert len(res.json()) == 1

    # Only the owner can manage members; an editor is forbidden.
    res = await client.post(
        f"{API}/workspaces/{workspace_id}/members",
        json={"email": "outsider@corp.com", "role": "viewer"},
        headers=editor,
    )
    assert res.status_code == 403


async def test_duplicate_member_conflict(client: AsyncClient):
    owner = await _register_login(client, "o2@corp.com")
    await _register(client, "m2@corp.com")
    workspace_id = (
        await client.post(f"{API}/workspaces", json={"name": "W2"}, headers=owner)
    ).json()["id"]

    payload = {"email": "m2@corp.com", "role": "editor"}
    assert (
        await client.post(
            f"{API}/workspaces/{workspace_id}/members", json=payload, headers=owner
        )
    ).status_code == 201
    # Adding the same user again conflicts.
    assert (
        await client.post(
            f"{API}/workspaces/{workspace_id}/members", json=payload, headers=owner
        )
    ).status_code == 409
