# =============================================================================
# REFACTOR - Enhanced cart operations
# =============================================================================

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import Item, Order, OrderItem

User = get_user_model()


@pytest.mark.django_db
class TestCartOperationsRefactored:
    """Refactored cart operations with advanced scenarios"""
    
    @pytest.fixture
    def user(self):
        """Create test user"""
        return User.objects.create_user(
            username='cartuser',
            email='cart@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def item_shirt(self):
        """Create shirt item"""
        return Item.objects.create(
            title='T-Shirt',
            price=25.00,
            category='S',
            label='P',
            slug='t-shirt',
            description='Cotton t-shirt',
            stock_quantity=50
        )
    
    @pytest.fixture
    def cart_order(self, user):
        """Create empty cart order"""
        return Order.objects.create(
            user=user,
            ordered_date=timezone.now()
        )
    
    def test_clear_cart_removes_all_items(self, cart_order, item_shirt):
        """Test clearing cart removes all items"""
        cart_order.add_to_cart(item_shirt, quantity=2)
        
        assert cart_order.items.count() == 1
        
        cart_order.clear_cart()
        
        assert cart_order.items.count() == 0
    
    def test_cart_prevents_negative_quantities(self, cart_order, item_shirt):
        """Test cart validation prevents negative quantities"""
        with pytest.raises(ValueError, match="quantity|positive"):
            cart_order.add_to_cart(item_shirt, quantity=-1)
