# =============================================================================
# REFACTOR - Add expiration and usage tracking
# =============================================================================

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from core.models import Item, Order, OrderItem, Coupon

User = get_user_model()

#WB

@pytest.mark.django_db
class TestCouponSystemRefactored:
    """Refactored coupon system tests with edge cases and best practices"""
    
    @pytest.fixture
    def user(self):
        """Create test user"""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def item_50(self):
        """Create item priced at $50"""
        return Item.objects.create(
            title='Mid-price Product',
            price=Decimal('50.00'),
            category='S',
            label='P',
            slug='mid-price',
            description='Test product',
            stock_quantity=20
        )
    
    @pytest.fixture
    def percentage_coupon(self):
        """Create 25% discount coupon"""
        return Coupon.objects.create(
            code='PERCENT25',
            discount_type='percentage',
            discount_value=25,
            minimum_order_amount=Decimal('50.00'),
            expiry_date=timezone.now() + timedelta(days=30)
        )
    
    def test_expired_coupon_validation(self, user, item_50):
        """Test that expired coupons cannot be applied"""
        order = Order.objects.create(user=user, ordered_date=timezone.now())
        OrderItem.objects.create(user=user, item=item_50, order=order, quantity=2)
        
        expired_coupon = Coupon.objects.create(
            code='EXPIRED',
            discount_type='percentage',
            discount_value=30,
            minimum_order_amount=Decimal('0.00'),
            expiry_date=timezone.now() - timedelta(days=1)
        )
        
        assert expired_coupon.is_active() is False
    
    def test_coupon_usage_tracking_and_limits(self):
        """Test coupon tracks usage and respects max_uses"""
        coupon = Coupon.objects.create(
            code='LIMITED3',
            discount_type='percentage',
            discount_value=15,
            minimum_order_amount=Decimal('0.00'),
            max_uses=3,
            current_uses=0
        )
        
        # Should allow usage
        assert coupon.can_be_used() is True
        
        # Increment usage
        coupon.increment_usage()
        assert coupon.current_uses == 1
        
        # Reach limit
        coupon.current_uses = 3
        coupon.save()
        assert coupon.can_be_used() is False
