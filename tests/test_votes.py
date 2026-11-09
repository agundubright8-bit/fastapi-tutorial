def test_vote_on_post(authorized_client, test_posts):
    response = authorized_client.post(
        "/votes/",
        json={"post_id": test_posts[0].id, "dir": 1}
    )

    assert response.status_code == 201
    assert response.json() == {"message": "successfully added vote"}


def test_vote_twice_on_post(authorized_client, test_posts, test_vote):
    response = authorized_client.post(
        "/votes/",
        json={"post_id": test_posts[0].id, "dir": 1}
    )

    assert response.status_code == 409


def test_delete_vote(authorized_client, test_posts, test_vote):
    response = authorized_client.post(
        "/votes/",
        json={"post_id": test_posts[0].id, "dir": 0}
    )

    assert response.status_code == 201
    assert response.json() == {"message": "successfully deleted vote"}


def test_delete_nonexistent_vote(authorized_client, test_posts):
    response = authorized_client.post(
        "/votes/",
        json={"post_id": test_posts[0].id,  "dir": 0}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vote does not exist"


def test_vote_on_nonexistent_post(authorized_client, test_posts):
    invalid_id = max(post.id for post in test_posts) + 1

    response = authorized_client.post(
        "/votes/",
        json={"post_id": invalid_id, "dir": 1}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == f"Post with id {invalid_id} does not exist"



def test_vote_without_authentication(client, test_posts):
    response = client.post(
        "/votes/",
        json={"post_id": test_posts[0].id, "dir": 1}
    )

    assert response.status_code == 401