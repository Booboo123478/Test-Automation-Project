"""Step definitions for Coupon System BDD tests"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from core.models import Item, Order, OrderItem, Coupon

# Load all scenarios from the feature file
scenarios('../coupon_system.feature')


@pytest.fixture
def context():
    """Shared context for storing test data between steps"""
    return {}


@pytest.fixture
def customer_user(db):
    """Create a customer user"""
    return User.objects.create_user(
        username='coupon_customer',
        email='coupon@test.com',
        password='testpass123'
    )


@given(parsers.parse('I have a cart with total value of {amount:f}'))
def create_cart_with_value(amount, context, customer_user, db):
    """Create a cart with items totaling the given amount"""
    order = Order.objects.create(
        user=customer_user,
        ordered=False
    )
    
    item = Item.objects.create(
        title='Test Product',
        price=amount,
        category='S',
        label='P',
        slug='test-product',
        description='Test product',
        stock_quantity=10
    )
    
    order_item = OrderItem.objects.create(
        user=customer_user,
        item=item,
        quantity=1,
        ordered=False
    )
    order.items.add(order_item)
    
    context['order'] = order
    context['user'] = customer_user
    context['initial_total'] = Decimal(str(amount))


@given(parsers.parse('a fixed coupon "{code}" exists with discount value {discount:f}'))
def create_fixed_coupon(code, discount, context, db):
    """Create a fixed amount discount coupon"""
    coupon = Coupon.objects.create(
        code=code,
        discount_type='fixed',
        discount_value=discount
    )
    context['coupon'] = coupon


@given(parsers.parse('a percentage coupon "{code}" exists with discount value {discount:d}'))
def create_percentage_coupon(code, discount, context, db):
    """Create a percentage discount coupon"""
    coupon = Coupon.objects.create(
        code=code,
        discount_type='percentage',
        discount_value=discount
    )
    context['coupon'] = coupon


@given(parsers.parse('a coupon "{code}" exists with discount {discount:f} and minimum order {minimum:f}'))
def create_coupon_with_minimum(code, discount, minimum, context, db):
    """Create a coupon with minimum order amount"""
    coupon = Coupon.objects.create(
        code=code,
        discount_type='fixed',
        discount_value=discount,
        minimum_order_amount=minimum
    )
    context['coupon'] = coupon


@given(parsers.parse('an expired coupon "{code}" exists with discount {discount:f}'))
def create_expired_coupon(code, discount, context, db):
    """Create an expired coupon"""
    expired_date = timezone.now() - timedelta(days=1)
    coupon = Coupon.objects.create(
        code=code,
        discount_type='fixed',
        discount_value=discount,
        expiry_date=expired_date
    )
    context['coupon'] = coupon


@given(parsers.parse('a coupon "{code}" exists with max uses {max_uses:d} and current uses {current_uses:d}'))
def create_coupon_max_uses(code, max_uses, current_uses, context, db):
    """Create a coupon with usage limits"""
    coupon = Coupon.objects.create(
        code=code,
        discount_type='fixed',
        discount_value=10.0,
        max_uses=max_uses,
        current_uses=current_uses
    )
    context['coupon'] = coupon


@given(parsers.parse('a coupon "{code}" with discount {discount:f} is applied to my order'))
def coupon_already_applied(code, discount, context, customer_user, db):
    """Create order with coupon already applied"""
    order = Order.objects.create(
        user=customer_user,
        ordered=False
    )
    
    item = Item.objects.create(
        title='Test Product',
        price=100.0,
        category='S',
        label='P',
        slug='test-product',
        description='Test',
        stock_quantity=10
    )
    
    order_item = OrderItem.objects.create(
        user=customer_user,
        item=item,
        quantity=1,
        ordered=False
    )
    order.items.add(order_item)
    
    coupon = Coupon.objects.create(
        code=code,
        discount_type='fixed',
        discount_value=discount
    )
    order.coupon = coupon
    order.save()
    
    context['order'] = order
    context['coupon'] = coupon
    context['user'] = customer_user


@when(parsers.parse('I apply the coupon "{code}" to my order'))
def apply_coupon_to_order(code, context):
    """Apply coupon to the order"""
    order = context['order']
    coupon = context['coupon']
    
    try:
        if hasattr(coupon, 'expiry_date') and coupon.expiry_date:
            if timezone.now() > coupon.expiry_date:
                context['error'] = "Coupon has expired"
                return
        
        if hasattr(coupon, 'max_uses') and coupon.max_uses:
            if coupon.current_uses >= coupon.max_uses:
                context['error'] = "Coupon has reached maximum uses"
                return
        
        if hasattr(coupon, 'minimum_order_amount') and coupon.minimum_order_amount:
            if order.get_subtotal() < Decimal(str(coupon.minimum_order_amount)):
                context['error'] = "Order does not meet minimum amount"
                return
        
        order.coupon = coupon
        order.save()
        context['coupon_applied'] = True
    except Exception as e:
        context['error'] = str(e)


@when("I remove the coupon from my order")
def remove_coupon_from_order(context):
    """Remove coupon from order"""
    order = context['order']
    order.coupon = None
    order.save()


@then(parsers.parse('my order total should be {expected_total:f}'))
def verify_order_total(expected_total, context):
    """Verify the order total"""
    order = context['order']
    order.refresh_from_db()
    actual_total = float(order.get_total())
    assert abs(actual_total - expected_total) < 0.01, f"Expected {expected_total}, got {actual_total}"


@then(parsers.parse('my order total should remain {expected_total:f}'))
def verify_order_total_unchanged(expected_total, context):
    """Verify order total hasn't changed"""
    order = context['order']
    order.refresh_from_db()
    actual_total = float(order.get_total())
    assert abs(actual_total - expected_total) < 0.01


@then("the coupon should be applied successfully")
def verify_coupon_applied(context):
    """Verify coupon was applied"""
    assert context.get('coupon_applied') is True or context['order'].coupon is not None


@then(parsers.parse('I should see an error "{expected_error}"'))
def verify_error_message(expected_error, context):
    """Verify error message"""
    assert context.get('error') == expected_error


@then(parsers.parse('the discount amount should be {expected_discount:f}'))
def verify_discount_amount(expected_discount, context):
    """Verify the discount amount"""
    order = context['order']
    order.refresh_from_db()
    
    subtotal = order.get_subtotal()
    total = order.get_total()
    actual_discount = float(subtotal - total)
    
    assert abs(actual_discount - expected_discount) < 0.01


@then("no coupon should be applied")
def verify_no_coupon_applied(context):
    """Verify no coupon is applied"""
    order = context['order']
    order.refresh_from_db()
    assert order.coupon is None
