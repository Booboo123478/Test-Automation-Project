"""
TDD Feature 2: Enhanced Coupon System
Red → Green → Refactor Cycle Documentation

Feature: Calculate order totals with percentage-based coupon discounts
- Support both fixed amount and percentage discount coupons
- Apply minimum order requirements for coupons
- Calculate accurate totals with tax
"""
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from core.models import Item, Order, OrderItem, Coupon

User = get_user_model()

# WB

# =============================================================================
# CYCLE 1: RED - Write failing tests for percentage coupons
# =============================================================================

@pytest.mark.tdd
class TestCouponSystem:
    """TDD Cycle 1: Red - Failing tests for coupon system"""
    
    @pytest.mark.django_db
    def test_coupon_has_discount_type_field(self):
        """Test that Coupon model has discount_type field"""
        coupon = Coupon.objects.create(
            code='SAVE20',
            discount_type='percentage',
            discount_value=20,
            minimum_order_amount=Decimal('50.00'),
            amount=0
        )
        assert coupon.discount_type == 'percentage'
        assert coupon.discount_value == 20
    
    @pytest.mark.django_db
    def test_percentage_coupon_calculation(self):
        """Test percentage discount calculation"""
        coupon = Coupon.objects.create(
            code='SAVE20',
            discount_type='percentage',
            discount_value=20,
            minimum_order_amount=Decimal('0.00'),
            amount=0
        )
        
        order_total = Decimal('100.00')
        discount = coupon.calculate_discount(order_total)
        assert discount == Decimal('20.00')
        
        # Test fixed amount
        fixed_coupon = Coupon.objects.create(
            code='SAVE10',
            discount_type='fixed',
            discount_value=10,
            minimum_order_amount=Decimal('0.00'),
            amount=0
        )
        discount_fixed = fixed_coupon.calculate_discount(order_total)
        assert discount_fixed == Decimal('10.00')