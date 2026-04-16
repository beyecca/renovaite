from datetime import date

from renovaite.models.project import Project
from renovaite.models.user import User
from renovaite.services.jwt import create_token_pair


def auth_headers(user: User) -> dict[str, str]:
    assert user.id is not None
    pair = create_token_pair(user.id)
    return {"Authorization": f"Bearer {pair['access']}"}


def make_project(db, user: User, **overrides) -> Project:
    assert user.id is not None
    project_data = {
        "user_id": user.id,
        "name": "Kitchen Remodel",
        "project_type": "kitchen_remodel",
        "description": "Replace cabinets and countertops.",
        "budget": 25000,
        "target_date": date(2026, 9, 1),
    }
    project_data.update(overrides)
    project = Project(**project_data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def test_create_project_success(client, user):
    resp = client.post(
        "/api/projects",
        json={
            "name": "Kitchen Remodel",
            "project_type": "kitchen_remodel",
            "description": "Replace cabinets and countertops.",
            "budget": 25000,
            "target_date": "2026-09-01",
        },
        headers=auth_headers(user),
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Kitchen Remodel"
    assert data["project_type"] == "kitchen_remodel"
    assert data["user_id"] == user.id
    assert data["is_deleted"] is False


def test_create_project_requires_auth(client):
    resp = client.post(
        "/api/projects",
        json={
            "name": "Kitchen Remodel",
            "project_type": "kitchen_remodel",
            "description": "Replace cabinets and countertops.",
        },
    )

    assert resp.status_code == 401
    assert resp.json()["detail"]["code"] == "UNAUTHORIZED"


def test_list_projects_returns_only_current_user_projects(client, db, user):
    other_user = User(email="other@example.com")
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    own_project = make_project(db, user)
    make_project(db, other_user, name="Bathroom Refresh")

    resp = client.get("/api/projects", headers=auth_headers(user))

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == own_project.id


def test_get_project_success(client, db, user):
    project = make_project(db, user)

    resp = client.get(f"/api/projects/{project.id}", headers=auth_headers(user))

    assert resp.status_code == 200
    assert resp.json()["id"] == project.id


def test_get_project_forbidden_for_other_user(client, db, user):
    other_user = User(email="other@example.com")
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    project = make_project(db, other_user)

    resp = client.get(f"/api/projects/{project.id}", headers=auth_headers(user))

    assert resp.status_code == 403
    assert resp.json()["detail"]["code"] == "FORBIDDEN"


def test_update_project_success(client, db, user):
    project = make_project(db, user)

    resp = client.patch(
        f"/api/projects/{project.id}",
        json={"name": "Kitchen Phase 1", "budget": 18000},
        headers=auth_headers(user),
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Kitchen Phase 1"
    assert data["budget"] == 18000


def test_delete_project_soft_deletes(client, db, user):
    project = make_project(db, user)

    delete_resp = client.delete(
        f"/api/projects/{project.id}",
        headers=auth_headers(user),
    )
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/api/projects/{project.id}", headers=auth_headers(user))
    assert get_resp.status_code == 404

    list_resp = client.get("/api/projects", headers=auth_headers(user))
    assert list_resp.status_code == 200
    assert list_resp.json() == []
