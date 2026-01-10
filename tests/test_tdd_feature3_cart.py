"""
TDD Feature 3: Smart Cart Item Merging
Red → Green → Refactor Cycle Documentation

Feature: Automatically merge duplicate items in cart
- Merge items with same product and variations
- Update quantities when adding existing items
- Handle cart item removal and quantity updates
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import Item, Order, OrderItem

User = get_user_model()


# =============================================================================
# CYCLE 1: RED - Write failing tests for cart item merging
# =============================================================================

@pytest.mark.tdd
class TestCartItemMerging:
    """TDD Cycle 1: Red - Failing tests for cart merging"""
    
    @pytest.mark.django_db
    def test_adding_same_item_increases_quantity(self):
        """Test that adding same item merges quantities"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        item = Item.objects.create(
            title='Test Product',
            price=29.99,
            category='S',
            label='P',
            slug='test-product',
            description='Test',
            image='test.jpg',
            stock_quantity=10
        )
        
        order = Order.objects.create(
            user=user,
            ordered_date=timezone.now()
        )
        
        order.add_to_cart(item, quantity=2)
        order.add_to_cart(item, quantity=3)
        assert order.items.count() == 1
        
        order_item = order.items.first()
        assert order_item.quantity == 5
    
    @pytest.mark.django_db
    def test_order_has_remove_from_cart_method(self):
        """Test Order has remove_from_cart method"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        item = Item.objects.create(
            title='Test Product',
            price=29.99,
            category='S',
            label='P',
            slug='test-product',
            description='Test',
            image='test.jpg',
            stock_quantity=10
        )
        
        order = Order.objects.create(
            user=user,
            ordered_date=timezone.now()
        )
        
        order.add_to_cart(item, quantity=3)
        assert order.items.count() == 1
        
        order.remove_from_cart(item)
        assert order.items.count() == 0
