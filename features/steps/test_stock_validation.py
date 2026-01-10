"""Step definitions for Stock Validation BDD tests"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from django.contrib.auth.models import User
from core.models import Item, Order, OrderItem

# Load all scenarios from the feature file
scenarios('../stock_validation.feature')


@pytest.fixture
def context():
    """Shared context for storing test data between steps"""
    return {}


@pytest.fixture
def customer_user(db):
    """Create a customer user"""
    return User.objects.create_user(
        username='customer',
        email='customer@test.com',
        password='testpass123'
    )


@given(parsers.parse('a product "{product_name}" exists with stock quantity {quantity:d}'))
def create_product_with_stock(product_name, quantity, context, db):
    """Create a product with specified stock quantity"""
    product = Item.objects.create(
        title=product_name,
        price=39.99,
        category='S',
        label='P',
        slug=product_name.lower().replace(' ', '-'),
        description=f"Test product: {product_name}",
        stock_quantity=quantity
    )
    context['product'] = product


@given("I am a logged in customer")
def logged_in_customer(customer_user, context):
    """Set up a logged in customer"""
    context['user'] = customer_user


@when("I check if the product is in stock")
def check_stock_status(context):
    """Check if product is in stock"""
    product = context['product']
    context['is_available'] = product.is_in_stock()


@when(parsers.parse('the stock quantity is reduced to {new_quantity:d}'))
def reduce_stock_to_zero(new_quantity, context):
    """Reduce stock quantity"""
    product = context['product']
    product.stock_quantity = new_quantity
    product.save()


@when(parsers.parse('I restock the product with {quantity:d} units'))
def restock_product(quantity, context):
    """Restock the product"""
    product = context['product']
    product.increase_stock(quantity)


@when("I attempt to add the product to cart")
def attempt_add_to_cart_out_of_stock(context):
    """Attempt to add out of stock product to cart"""
    product = context['product']
    user = context['user']
    
    try:
        if not product.is_in_stock():
            context['error_message'] = "Product is out of stock"
            context['cart_add_failed'] = True
        else:
            # Create order and add item
            order, created = Order.objects.get_or_create(
                user=user,
                ordered=False
            )
            order_item, created = OrderItem.objects.get_or_create(
                item=product,
                user=user,
                ordered=False
            )
            order.items.add(order_item)
            context['order'] = order
            context['cart_add_failed'] = False
    except Exception as e:
        context['error_message'] = str(e)
        context['cart_add_failed'] = True


@when(parsers.parse('I add {quantity:d} units of the product to cart'))
def add_units_to_cart(quantity, context):
    """Add specific quantity to cart"""
    product = context['product']
    user = context['user']
    
    if product.is_in_stock() and product.can_fulfill(quantity):
        order, created = Order.objects.get_or_create(
            user=user,
            ordered=False
        )
        order_item, created = OrderItem.objects.get_or_create(
            item=product,
            user=user,
            ordered=False
        )
        order_item.quantity = quantity
        order_item.save()
        order.items.add(order_item)
        context['order'] = order
        context['order_item'] = order_item


@then("the product should be available")
def verify_product_available(context):
    """Verify product is available"""
    product = context['product']
    product.refresh_from_db()
    assert product.is_in_stock() is True


@then("the product should not be available")
def verify_product_not_available(context):
    """Verify product is not available"""
    product = context['product']
    product.refresh_from_db()
    assert product.is_in_stock() is False


@then(parsers.parse('the product stock quantity should be {expected_quantity:d}'))
def verify_stock_quantity(expected_quantity, context):
    """Verify the stock quantity"""
    product = context['product']
    product.refresh_from_db()
    assert product.stock_quantity == expected_quantity


@then(parsers.parse('I should see an error message "{expected_message}"'))
def verify_error_message(expected_message, context):
    """Verify error message is shown"""
    assert context.get('error_message') == expected_message


@then("the product should not be added to cart")
def verify_not_in_cart(context):
    """Verify product was not added to cart"""
    assert context.get('cart_add_failed') is True


@then("the product should be in my cart")
def verify_product_in_cart(context):
    """Verify product is in the cart"""
    order = context.get('order')
    product = context['product']
    assert order is not None
    assert order.items.filter(item=product).exists()


@then(parsers.parse('my cart should have {expected_quantity:d} units of the product'))
def verify_cart_quantity(expected_quantity, context):
    """Verify quantity in cart"""
    order_item = context.get('order_item')
    assert order_item is not None
    assert order_item.quantity == expected_quantity
