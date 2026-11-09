import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from app import models
from app.config import settings
from app.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.database_username,
    password=settings.database_password,
    host=settings.database_hostname,
    port=int(settings.database_port),
    database="fastapi_test",
)

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


#This fixture creates a test user by sending a POST request to the /users/ endpoint with the specified email and password. It returns the JSON response containing the created user's details. To be used in other test functions that require a test user.
@pytest.fixture
def test_user(client):
    response = client.post("/users/", json={"email": "test@example.com", "password": "password"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def token(client, test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": test_user["email"],
            "password": "password"
        }
    )

    return response.json()["access_token"]


@pytest.fixture
def authorized_client(client, token):
    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return client



@pytest.fixture
def test_posts(session, test_user):
    posts = [
        models.Post(
            title="Python Basics",
            content="Learning Python",
            user_id=test_user["id"]
        ),
        models.Post(
            title="FastAPI Guide",
            content="Building APIs",
            user_id=test_user["id"]
        ),
        models.Post(
            title="SQLAlchemy Tutorial",
            content="Working with databases",
            user_id=test_user["id"]
        ),
        models.Post(
            title="Docker Fundamentals",
            content="Containerizing applications",
            user_id=test_user["id"]
        )
    ]

    session.add_all(posts)
    session.commit()

    return posts


@pytest.fixture
def test_vote(authorized_client, test_posts):
    response = authorized_client.post(
        "/votes/",
        json={"post_id": test_posts[0].id, "dir": 1}
    )

    assert response.status_code == 201
    return response