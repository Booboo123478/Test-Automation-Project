# =============================================================================
# REFACTOR - Improve implementation with edge cases
# =============================================================================

import pytest
from django.contrib.auth import get_user_model
from core.models import Item, OrderItem

User = get_user_model()


@pytest.mark.django_db
class TestStockManagementRefactored:
    """HM Refactored stock management tests with edge cases and DRY principles"""
    
    @pytest.fixture
    def user(self):
        """Create test user"""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def item_with_stock(self):
        """Create item with initial stock"""
        return Item.objects.create(
            title='Test Product',
            price=50.0,
            category='S',
            label='P',
            slug='test-product',
            description='Test description',
            stock_quantity=10
        )
    
    @pytest.fixture
    def out_of_stock_item(self):
        """Create item with zero stock"""
        return Item.objects.create(
            title='Out of Stock Product',
            price=30.0,
            category='S',
            label='P',
            slug='out-of-stock',
            description='No stock',
            stock_quantity=0
        )
    
    def test_stock_status_categories(self, item_with_stock, out_of_stock_item):
        """Test stock status returns correct categories"""
        # Test IN_STOCK status
        item_with_stock.stock_quantity = 10
        item_with_stock.save()
        assert item_with_stock.get_stock_status() == 'IN_STOCK'
        
        # Test LOW_STOCK status
        item_with_stock.stock_quantity = 3
        item_with_stock.save()
        assert item_with_stock.get_stock_status() == 'LOW_STOCK'
        
        # Test OUT_OF_STOCK status
        assert out_of_stock_item.get_stock_status() == 'OUT_OF_STOCK'
    
    def test_increase_stock_restocking(self, out_of_stock_item):
        """Test restocking increases inventory"""
        out_of_stock_item.increase_stock(20)
        assert out_of_stock_item.stock_quantity == 20
        assert out_of_stock_item.is_in_stock()
    
    def test_multiple_stock_operations(self, item_with_stock):
        """Test series of stock operations"""
        item_with_stock.reduce_stock(3)
        assert item_with_stock.stock_quantity == 7
        
        item_with_stock.increase_stock(5)
        assert item_with_stock.stock_quantity == 12
        
        item_with_stock.reduce_stock(12)
        assert item_with_stock.stock_quantity == 0
