import pytest
import os

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.auth import get_current_user
from app.models import User

load_dotenv(Path(__file__).resolve().parent / ".env.test")

TEST_DATABASE_URL = (f"postgresql+psycopg2://"
                     f"{os.getenv('TEST_DB_USER')}:"
                     f"{os.getenv('TEST_DB_PASSWORD')}@"
                     f"{os.getenv('TEST_DB_HOST')}:"
                     f"{os.getenv('TEST_DB_PORT')}/"
                     f"{os.getenv('TEST_DB_NAME')}") # test database

test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture()
def test_db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture()
def client(test_db):
    def override_get_db():
        yield test_db

    def override_auth():
        return User(user_id = 1, email = "random@email.com", hashed_password = "fake-test!fake?test#fake%test", is_active = True, role = "admin")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_auth

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture()
def create_category(client):
    payload = {
        "name": "Test_Category"
    }

    response = client.post("/categories", json=payload)
    assert response.status_code == 201
    return response.json()

@pytest.fixture()
def create_product(client, create_category):
    payload = {
        "category_id": create_category["category_id"],
        "name": "test_product",
        "description": "test description",
        "price": "1099.99",
        "quantity": "999"
    }

    response = client.post("/products", json=payload)
    assert response.status_code == 201
    return response.json()

@pytest.fixture()
def create_cart(client):
    response = client.post("/cart")
    assert response.status_code == 201
    return response.json()

@pytest.fixture()
def create_cart_item(client, create_cart, create_product):
    payload = {
        "cart_id": create_cart["cart_id"],
        "product_id": create_product["product_id"],
        "quantity": 10
    }

    response = client.post("/cart/items", json=payload)
    assert response.status_code == 201
    return response.json()

@pytest.fixture()
def create_order(client):
    response = client.post("/orders")
    assert response.status_code == 201
    return response.json()