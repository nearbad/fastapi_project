import pytest
from app import schemas


def test_get_all_tasks(authorized_client, test_tasks):
    res = authorized_client.get("/tasks/")

    def validate(task):
        return schemas.Task(**task)

    tasks_map = map(validate, res.json())
    tasks_list = list(tasks_map)

    assert len(res.json()) == len(test_tasks)
    assert res.status_code == 200


def test_unauthorized_user_get_all_tasks(client, test_tasks):
    res = client.get("/tasks/")
    assert res.status_code == 401


def test_unauthorized_user_get_one_task(client, test_tasks):
    res = client.get(f"/tasks/{test_tasks[0].id}")
    assert res.status_code == 401


def test_get_one_task_not_exist(authorized_client, test_tasks):
    res = authorized_client.get(f"/tasks/88888")
    assert res.status_code == 404


def test_get_one_post(authorized_client, test_tasks):
    res = authorized_client.get(f"/tasks/{test_tasks[0].id}")
    task = schemas.Task(**res.json())
    assert task.id == test_tasks[0].id
    assert task.content == test_tasks[0].content
    assert task.title == test_tasks[0].title


@pytest.mark.parametrize("title, content, published", [
    ("awesome new title", "awesome new content", True),
    ("favorite pizza", "i love pepperoni", False),
    ("tallest skyscrapers", "wahoo", True),
])
def test_create_task(authorized_client, test_user, test_tasks, title, content, published):
    res = authorized_client.post(
        "/tasks/", json={"title": title, "content": content, "published": published})

    created_task = schemas.Task(**res.json())
    assert res.status_code == 201
    assert created_task.title == title
    assert created_task.content == content
    assert created_task.published == published
    assert created_task.owner_id == test_user['id']


def test_create_task_default_published_true(authorized_client, test_user, test_tasks):
    res = authorized_client.post(
        "/tasks/", json={"title": "arbitrary title", "content": "aasdfjasdf"})

    created_task = schemas.Task(**res.json())
    assert res.status_code == 201
    assert created_task.title == "arbitrary title"
    assert created_task.content == "aasdfjasdf"
    assert created_task.published == True
    assert created_task.owner_id == test_user['id']


def test_unauthorized_user_create_task(client, test_user, test_tasks):
    res = client.post(
        "/tasks/", json={"title": "arbitrary title", "content": "aasdfjasdf"})
    assert res.status_code == 401


def test_unauthorized_user_delete_task(client, test_user, test_tasks):
    res = client.delete(
        f"/tasks/{test_tasks[0].id}")
    assert res.status_code == 401


def test_delete_task_success(authorized_client, test_user, test_tasks):
    res = authorized_client.delete(
        f"/tasks/{test_tasks[0].id}")

    assert res.status_code == 204


def test_delete_task_non_exist(authorized_client, test_user, test_tasks):
    res = authorized_client.delete(
        f"/tasks/8000000")

    assert res.status_code == 404


def test_delete_other_user_task(authorized_client, test_user, test_tasks):
    res = authorized_client.delete(
        f"/tasks/{test_tasks[3].id}")
    assert res.status_code == 403


def test_update_task(authorized_client, test_user, test_tasks):
    data = {
        "title": "updated title",
        "content": "updatd content",
        "id": test_tasks[0].id

    }
    res = authorized_client.put(f"/tasks/{test_tasks[0].id}", json=data)
    updated_task = schemas.Task(**res.json())
    assert res.status_code == 200
    assert updated_task.title == data['title']
    assert updated_task.content == data['content']


def test_update_other_user_task(authorized_client, test_user, test_user2, test_tasks):
    data = {
        "title": "updated title",
        "content": "updatd content",
        "id": test_tasks[3].id

    }
    res = authorized_client.put(f"/tasks/{test_tasks[3].id}", json=data)
    assert res.status_code == 403


def test_unauthorized_user_update_task(client, test_user, test_tasks):
    res = client.put(
        f"/tasks/{test_tasks[0].id}")
    assert res.status_code == 401


def test_update_task_non_exist(authorized_client, test_user, test_tasks):
    data = {
        "title": "updated title",
        "content": "updatd content",
        "id": test_tasks[3].id

    }
    res = authorized_client.put(
        f"/tasks/8000000", json=data)

    assert res.status_code == 404
