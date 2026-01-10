"""
HM 
TDD Feature 1: Product Stock Validation
Red → Green → Refactor Cycle Documentation

Feature: Validate product stock availability before adding to cart
- Prevent adding out-of-stock items to cart
- Track stock quantities
- Provide clear error messages
"""
import pytest
from django.contrib.auth import get_user_model
from core.models import Item, OrderItem

User = get_user_model()


# =============================================================================
# CYCLE 1: RED - Write failing tests for stock tracking
# =============================================================================

@pytest.mark.tdd
class TestProductStockValidation:
    """TDD Cycle 1: Red - Failing tests"""
    
    @pytest.mark.django_db
    def test_item_has_stock_quantity_field(self):
        """Test that Item model has stock_quantity field"""
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
        assert item.stock_quantity == 10
    
    @pytest.mark.django_db
    def test_item_is_in_stock_method(self):
        """Test is_in_stock method returns True when stock available"""
        item = Item.objects.create(
            title='Test Product',
            price=29.99,
            category='S',
            label='P',
            slug='test-product',
            description='Test',
            image='test.jpg',
            stock_quantity=5
        )
        assert item.is_in_stock() is True
        
        # Test out of stock
        item.stock_quantity = 0
        item.save()
        assert item.is_in_stock() is False
    