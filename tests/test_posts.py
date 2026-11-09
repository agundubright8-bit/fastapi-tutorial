import pytest
from app import schemas
from uuid import uuid4



def validate_post(post):
    """Validate an API response against the PostOut schema."""
    return schemas.PostOut(**post)


# -------------------- GET ALL POSTS --------------------

def test_get_posts(authorized_client, test_posts):
    response = authorized_client.get("/posts/")

    assert response.status_code == 200

    posts = [validate_post(post) for post in response.json()]

    assert len(posts) == len(test_posts)

    expected_posts = {post.id: post for post in test_posts}

    for post in posts:
        expected_post = expected_posts[post.id]

        assert post.title == expected_post.title
        assert post.content == expected_post.content
        assert post.published == expected_post.published


def test_get_all_posts_unauthorized(client, test_posts):
    response = client.get("/posts/")

    assert response.status_code == 200

    posts = [validate_post(post) for post in response.json()]

    assert len(posts) == len(test_posts)


# -------------------- GET LATEST POST --------------------

def test_get_latest_post(authorized_client, test_posts):
    response = authorized_client.get("/posts/latest")

    assert response.status_code == 200

    latest_post = validate_post(response.json())

    expected_post = test_posts[-1]

    assert latest_post.id == expected_post.id
    assert latest_post.title == expected_post.title
    assert latest_post.content == expected_post.content



def test_get_latest_post_no_posts(authorized_client):
    response = authorized_client.get("/posts/latest")

    assert response.status_code == 404


def test_get_latest_post_unauthorized(client):
    response = client.get("/posts/latest")

    assert response.status_code == 401

# -------------------- GET ONE POST --------------------

def test_get_one_post(authorized_client, test_posts):
    response = authorized_client.get(f"/posts/{test_posts[0].id}")

    assert response.status_code == 200

    post = validate_post(response.json())

    assert post.id == test_posts[0].id
    assert post.title == test_posts[0].title
    assert post.content == test_posts[0].content


def test_get_one_post_not_found(authorized_client, test_posts):
    invalid_id = max(post.id for post in test_posts) + 1

    response = authorized_client.get(f"/posts/{invalid_id}")

    assert response.status_code == 404


def test_get_one_post_unauthorized(client, test_posts):
    response = client.get(f"/posts/{test_posts[0].id}")

    assert response.status_code == 401


# -------------------- CREATE POSTS --------------------

@pytest.mark.parametrize("title, content, published", [
    ("Python Basics", "Learning Python", True),
    ("FastAPI Guide", "Building APIs", True),
    ("Docker Guide", "Learning containers", False),
])
def test_create_post(authorized_client, title, content, published):
    response = authorized_client.post(
        "/posts/",
        json={
            "title": title,
            "content": content,
            "published": published
        }
    )

    assert response.status_code == 201

    new_post = validate_post(response.json())

    assert new_post.title == title
    assert new_post.content == content
    assert new_post.published == published


def test_create_post_unauthorized(client):
    response = client.post(
        "/posts/",
        json={
            "title": "Unauthorized post",
            "content": "Testing authentication",
            "published": True
        }
    )

    assert response.status_code == 401


# -------------------- DELETE POSTS --------------------

def test_delete_post_unauthorized(client, test_posts):
    response = client.delete(f"/posts/{test_posts[0].id}")

    assert response.status_code == 401


def test_delete_post(authorized_client, test_posts):
    response = authorized_client.delete(
        f"/posts/{test_posts[0].id}"
    )

    assert response.status_code == 204

    # Confirm the post was actually deleted
    deleted_post = authorized_client.get(
        f"/posts/{test_posts[0].id}"
    )

    assert deleted_post.status_code == 404


def test_delete_nonexistent_post(authorized_client, test_posts):
    invalid_id = max(post.id for post in test_posts) + 1

    response = authorized_client.delete(
        f"/posts/{invalid_id}"
    )

    assert response.status_code == 404




def test_user_cannot_delete_another_users_post(client, test_posts):
    # Create another user
    email = f"{uuid4()}@example.com"

    new_user = client.post(
        "/users/",
        json={
            "email": email,
            "password": "password"
        }
    )
    assert new_user.status_code == 201

    # Log in as the other user
    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    # Attempt to delete a post belonging to the original test user
    response = client.delete(f"/posts/{test_posts[0].id}")

    assert response.status_code == 403
# -------------------- UPDATE POSTS --------------------

def test_update_post(authorized_client, test_posts):
    updated_data = {
        "title": "Updated Python Guide",
        "content": "Learning advanced Python",
        "published": False
    }

    response = authorized_client.put(
        f"/posts/{test_posts[0].id}",
        json=updated_data
    )

    assert response.status_code == 200
    updated_post = validate_post(response.json())
    assert updated_post.id == test_posts[0].id
    assert updated_post.title == updated_data["title"]
    assert updated_post.content == updated_data["content"]
    assert updated_post.published == updated_data["published"]

def test_update_post_unauthorized(client, test_posts):
    response = client.put(
        f"/posts/{test_posts[0].id}",
        json={
            "title": "Updated title",
            "content": "Updated content",
            "published": True
        }
    )

    assert response.status_code == 401


def test_user_cannot_update_another_users_post(client, test_posts):
    email = f"{uuid4()}@example.com"

    new_user = client.post(
        "/users/",
        json={
            "email": email,
            "password": "password"
        }
    )
    assert new_user.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    response = client.put(
        f"/posts/{test_posts[0].id}",
        json={
            "title": "Updated title",
            "content": "Updated content",
            "published": True
        }
    )

    assert response.status_code == 403



def test_update_nonexistent_post(authorized_client, test_posts):
    invalid_id = max(post.id for post in test_posts) + 1

    response = authorized_client.put(
        f"/posts/{invalid_id}",
        json={
            "title": "Updated title",
            "content": "Updated content",
            "published": True
        }
    )

    assert response.status_code == 404


