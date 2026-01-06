import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from core.models import Item, UserProfile, Address, Coupon
from django_countries.fields import Country

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture to provide DRF API client"""
    return APIClient()


@pytest.fixture
def user(db):
    """Fixture to create a test user"""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!'
    )
    UserProfile.objects.get_or_create(user=user)
    return user


@pytest.fixture
def authenticated_client(api_client, user):
    """Fixture to provide authenticated API client"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def test_item(db):
    """Fixture to create a test product item"""
    item = Item.objects.create(
        title='Test Product',
        price=29.99,
        discount_price=24.99,
        category='S',
        label='P',
        slug='test-product',
        description='This is a test product',
        image='test.jpg'
    )
    return item


@pytest.fixture
def test_items(db):
    """Fixture to create multiple test items"""
    items = []
    for i in range(5):
        item = Item.objects.create(
            title=f'Test Product {i+1}',
            price=20.00 + i * 5,
            discount_price=15.00 + i * 5,
            category='S' if i % 2 == 0 else 'SW',
            label='P' if i % 3 == 0 else 'S',
            slug=f'test-product-{i+1}',
            description=f'Test product description {i+1}',
            image=f'test{i+1}.jpg'
        )
        items.append(item)
    return items


@pytest.fixture
def test_address(user, db):
    """Fixture to create a test address"""
    address = Address.objects.create(
        user=user,
        street_address='123 Test Street',
        apartment_address='Apt 4B',
        country='US',
        zip='12345',
        address_type='S',
        default=True
    )
    return address


@pytest.fixture
def test_billing_address(user, db):
    """Fixture to create a test billing address"""
    address = Address.objects.create(
        user=user,
        street_address='456 Billing Ave',
        apartment_address='Suite 100',
        country='US',
        zip='54321',
        address_type='B',
        default=True
    )
    return address


@pytest.fixture
def test_coupon(db):
    """Fixture to create a test coupon"""
    coupon = Coupon.objects.create(
        code='TESTCODE',
        amount=10.00
    )
    return coupon


@pytest.fixture
def chrome_driver():
    """Fixture to provide Chrome WebDriver for Selenium tests"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()


@pytest.fixture
def live_server_url(live_server):
    """Fixture to provide the live server URL"""
    return live_server.url
