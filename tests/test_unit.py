import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import (
    Item, OrderItem, Order, Address, Coupon, 
    Payment, UserProfile, Variation, ItemVariation
)

User = get_user_model()


@pytest.mark.unit
class TestUserProfileModel:
    """Test UserProfile model"""
    
    def test_user_profile_creation(self, user):
        """Test that user profile is created with user"""
        profile = UserProfile.objects.get(user=user)
        assert profile.user == user
        assert profile.one_click_purchasing == False
        assert str(profile) == user.username
    
    def test_user_profile_stripe_id(self, user):
        """Test setting stripe customer ID"""
        profile = UserProfile.objects.get(user=user)
        profile.stripe_customer_id = 'cus_test123'
        profile.save()
        
        profile.refresh_from_db()
        assert profile.stripe_customer_id == 'cus_test123'


@pytest.mark.unit
class TestItemModel:
    """Test Item model"""
    
    def test_item_creation(self, test_item):
        """Test creating a product item"""
        assert test_item.title == 'Test Product'
        assert test_item.price == 29.99
        assert test_item.slug == 'test-product'
        assert str(test_item) == 'Test Product'
    
    def test_item_get_absolute_url(self, test_item):
        """Test get_absolute_url method"""
        assert test_item.slug == 'test-product'
    
    def test_item_discount_price(self, test_item):
        """Test item with discount price"""
        assert test_item.discount_price == 24.99
        assert test_item.discount_price < test_item.price


@pytest.mark.unit
class TestOrderItemModel:
    """Test OrderItem model"""
    
    def test_order_item_creation(self, user, test_item):
        """Test creating an order item"""
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=2,
            ordered=False
        )
        
        assert order_item.user == user
        assert order_item.item == test_item
        assert order_item.quantity == 2
        assert str(order_item) == '2 of Test Product'
    
    def test_order_item_get_total_price(self, user, test_item):
        """Test calculating total item price"""
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=3
        )
        
        expected_price = test_item.price * 3
        assert order_item.get_total_item_price() == expected_price
    
    def test_order_item_get_discount_price(self, user, test_item):
        """Test calculating discounted item price"""
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=2
        )
        
        expected_price = test_item.discount_price * 2
        assert order_item.get_total_discount_item_price() == expected_price
    
    def test_order_item_final_price_with_discount(self, user, test_item):
        """Test final price uses discount when available"""
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=2
        )
        
        expected = test_item.discount_price * 2
        assert order_item.get_final_price() == expected


@pytest.mark.unit
class TestOrderModel:
    """Test Order model"""
    
    def test_order_creation(self, user):
        """Test creating an order"""
        order = Order.objects.create(user=user, ordered_date=timezone.now())
        
        assert order.user == user
        assert order.ordered == False
        assert order.items.count() == 0
        assert str(order) == user.username
    
    def test_order_get_total(self, user, test_item):
        """Test calculating order total"""
        order = Order.objects.create(user=user, ordered_date=timezone.now())
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=2
        )
        order.items.add(order_item)
        
        expected_total = test_item.discount_price * 2
        assert order.get_total() == expected_total
    
    def test_order_get_total_with_coupon(self, user, test_item, test_coupon):
        """Test order total with coupon applied"""
        order = Order.objects.create(user=user, coupon=test_coupon, ordered_date=timezone.now())
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=2
        )
        order.items.add(order_item)
        
        subtotal = test_item.discount_price * 2
        expected_total = subtotal - test_coupon.amount
        assert order.get_total() == expected_total


@pytest.mark.unit
class TestAddressModel:
    """Test Address model"""
    
    def test_address_creation(self, test_address):
        """Test creating an address"""
        assert test_address.street_address == '123 Test Street'
        assert test_address.country == 'US'
        assert test_address.address_type == 'S'
        assert test_address.default == True
    
    def test_address_str_representation(self, test_address):
        """Test address string representation"""
        address_str = str(test_address)
        assert 'testuser' in address_str
    
    def test_multiple_addresses_per_user(self, user):
        """Test user can have multiple addresses"""
        addr1 = Address.objects.create(
            user=user,
            street_address='123 Main St',
            country='US',
            zip='12345',
            address_type='S'
        )
        addr2 = Address.objects.create(
            user=user,
            street_address='456 Oak Ave',
            country='US',
            zip='54321',
            address_type='B'
        )
        
        assert Address.objects.filter(user=user).count() == 2


@pytest.mark.unit
class TestCouponModel:
    """Test Coupon model"""
    
    def test_coupon_creation(self, test_coupon):
        """Test creating a coupon"""
        assert test_coupon.code == 'TESTCODE'
        assert test_coupon.amount == 10.00
        assert str(test_coupon) == 'TESTCODE'
    
    def test_coupon_code_uniqueness(self, db):
        """Test coupon codes should be unique"""
        Coupon.objects.create(code='UNIQUE1', amount=5.00)
        
        coupon = Coupon.objects.get(code='UNIQUE1')
        assert coupon.amount == 5.00


@pytest.mark.unit
class TestVariationModel:
    """Test Variation and ItemVariation models"""
    
    def test_variation_creation(self, test_item):
        """Test creating a variation (e.g., size)"""
        variation = Variation.objects.create(
            item=test_item,
            name='Size'
        )
        
        assert variation.item == test_item
        assert variation.name == 'Size'
        assert str(variation) == 'Size'
    
    def test_item_variation_creation(self, test_item):
        """Test creating item variation values"""
        variation = Variation.objects.create(
            item=test_item,
            name='Size'
        )
        
        item_var = ItemVariation.objects.create(
            variation=variation,
            value='Large'
        )
        
        assert item_var.variation == variation
        assert item_var.value == 'Large'
        assert str(item_var) == 'Large'


@pytest.mark.unit
class TestPaymentModel:
    """Test Payment model"""
    
    def test_payment_creation(self, user):
        """Test creating a payment record"""
        payment = Payment.objects.create(
            user=user,
            stripe_charge_id='ch_test123',
            amount=50.00
        )
        
        assert payment.user == user
        assert payment.stripe_charge_id == 'ch_test123'
        assert payment.amount == 50.00
        assert str(payment) == user.username
