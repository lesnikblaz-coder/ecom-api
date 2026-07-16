import os
import pytest_asyncio

from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from app.database import Base, get_db
from app.models import User, Order
from app.main import app
from app.auth import get_current_user
from app.dependencies import get_payment_service
from app.integrations.mock_payment_gateway import SuccessPaymentGateway, FailPaymentGateway
from app.services.payment_services import PaymentService
from app.enums import UserRole, OrderStatus

load_dotenv(Path(__file__).resolve().parent / ".env.test")

TEST_DATABASE_URL = (f"postgresql+asyncpg://"
                     f"{os.getenv('TEST_DB_USER')}:"
                     f"{os.getenv('TEST_DB_PASSWORD')}@"
                     f"{os.getenv('TEST_DB_HOST')}:"
                     f"{os.getenv('TEST_DB_PORT')}/"
                     f"{os.getenv('TEST_DB_NAME')}") # test database

async_test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
AsyncSessionLocal = async_sessionmaker(
    bind=async_test_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with async_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def test_db():
    async with async_test_engine.connect() as connection:
        transaction = await connection.begin()

        session = AsyncSessionLocal(bind=connection)

        await connection.begin_nested()

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()

@pytest_asyncio.fixture()
async def auth_user(test_db) -> User:
    user = User(
        email="test@test.com",
        hashed_password="fake_hash",
        role=UserRole.ADMIN,
        is_active=True
    )
    test_db.add(user)
    await test_db.flush()
    return user

@pytest_asyncio.fixture()
async def client(test_db: AsyncSession, auth_user: User):
    async def override_get_db():
        yield test_db

    def override_auth():
        return auth_user

    def override_payment_service():
        return PaymentService(SuccessPaymentGateway())

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_auth
    app.dependency_overrides[get_payment_service] = override_payment_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

@pytest_asyncio.fixture()
async def client_fail(test_db: AsyncSession, auth_user: User):
    async def override_get_db():
        yield test_db

    def override_auth():
        return auth_user

    def override_payment_service():
        return PaymentService(FailPaymentGateway())

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_auth
    app.dependency_overrides[get_payment_service] = override_payment_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

###

@pytest_asyncio.fixture()
async def create_category(client):
    payload = {
        "name": "Test_Category"
    }

    response = await client.post("/categories", json=payload)
    assert response.status_code == 201
    return response.json()

@pytest_asyncio.fixture()
async def create_product(client, create_category):
    payload = {
        "category_id": create_category["category_id"],
        "name": "test_product",
        "description": "test description",
        "price": "1099.99",
        "quantity": "999"
    }

    response = await client.post("/products", json=payload)
    assert response.status_code == 201
    return response.json()

@pytest_asyncio.fixture()
async def create_cart_item(client, create_product):
    payload = {
        "product_id": create_product["product_id"],
        "quantity": 10
    }

    response = await client.post("/cart/items", json=payload)
    assert response.status_code == 201
    return response.json()

@pytest_asyncio.fixture()
async def create_order(client, create_cart_item):
    response = await client.post("/orders", json={
        "delivery_address": "123 Test Street, Test City"
    })
    assert  response.status_code == 201
    return response.json()

@pytest_asyncio.fixture()
async def create_order_pending(client_fail, create_cart_item):
    response = await client_fail.post("/orders", json={
        "delivery_address": "123 Test Street, Test City"
    })
    assert response.status_code == 201
    return response.json()

@pytest_asyncio.fixture()
async def create_order_shipped(client, create_order, test_db):
    result = await test_db.execute(select(Order).where(Order.order_id == create_order["order_id"]))
    order = result.scalar_one()

    order.status = OrderStatus.SHIPPED
    await test_db.flush()

    return create_order