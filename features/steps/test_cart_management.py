"""Step definitions for Cart Management BDD tests"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from django.contrib.auth.models import User
from decimal import Decimal
from core.models import Item, Order, OrderItem

# Load all scenarios from the feature file
scenarios('../cart_management.feature')


@pytest.fixture
def context():
    """Shared context for storing test data between steps"""
    return {}


@pytest.fixture
def cart_customer(db):
    """Create a customer user for cart tests"""
    return User.objects.create_user(
        username='cart_user',
        email='cart@test.com',
        password='testpass123'
    )


@given("I am logged in as a customer")
def logged_in_customer(cart_customer, context):
    """Set up a logged in customer with empty cart"""
    order, created = Order.objects.get_or_create(
        user=cart_customer,
        ordered=False
    )
    context['user'] = cart_customer
    context['order'] = order


@given(parsers.parse('a product "{product_name}" exists with price {price:f} and stock {stock:d}'))
def create_product(product_name, price, stock, context, db):
    """Create a product with specified details"""
    product = Item.objects.create(
        title=product_name,
        price=price,
        category='S',
        label='P',
        slug=product_name.lower().replace(' ', '-'),
        description=f"Product: {product_name}",
        stock_quantity=stock
    )
    context[product_name] = product
    if 'products' not in context:
        context['products'] = {}
    context['products'][product_name] = product


@given(parsers.parse('the product is already in my cart with quantity {quantity:d}'))
def product_in_cart(quantity, context):
    """Add product to cart with specified quantity"""
    products = context.get('products', {})
    if products:
        product = list(products.values())[-1]
        order = context['order']
        user = context['user']
        
        order_item = OrderItem.objects.create(
            user=user,
            item=product,
            quantity=quantity,
            ordered=False
        )
        order.items.add(order_item)


@given(parsers.parse('the product is in my cart with quantity {quantity:d}'))
def product_is_in_cart(quantity, context):
    """Same as product_in_cart"""
    product_in_cart(quantity, context)


@given("multiple products are in my cart")
def multiple_products_in_cart(context, db):
    """Add multiple products to cart"""
    user = context['user']
    order = context['order']
    
    for i in range(3):
        item = Item.objects.create(
            title=f'Item {i+1}',
            price=29.99,
            category='S',
            label='P',
            slug=f'item-{i+1}',
            description=f'Test item {i+1}',
            stock_quantity=10
        )
        order_item = OrderItem.objects.create(
            user=user,
            item=item,
            quantity=1,
            ordered=False
        )
        order.items.add(order_item)


@given(parsers.parse('"{product_name}" is in my cart with quantity {quantity:d}'))
def specific_product_in_cart(product_name, quantity, context):
    """Add a specific named product to cart"""
    product = context['products'][product_name]
    order = context['order']
    user = context['user']
    
    order_item = OrderItem.objects.create(
        user=user,
        item=product,
        quantity=quantity,
        ordered=False
    )
    order.items.add(order_item)


@when("I add the product to my cart")
def add_product_to_cart(context):
    """Add product to cart"""
    products = context.get('products', {})
    if products:
        product = list(products.values())[-1]
        order = context['order']
        
        try:
            order.add_to_cart(product, quantity=1)
        except Exception as e:
            context['error'] = str(e)


@when("I add the product to my cart again")
def add_product_again(context):
    """Add same product to cart again"""
    add_product_to_cart(context)


@when(parsers.parse('I add "{product_name}" to my cart'))
def add_named_product_to_cart(product_name, context):
    """Add a specific product to cart"""
    product = context['products'][product_name]
    order = context['order']
    
    try:
        order.add_to_cart(product, quantity=1)
    except Exception as e:
        context['error'] = str(e)


@when(parsers.parse('I update the cart item quantity to {new_quantity:d}'))
def update_cart_quantity(new_quantity, context):
    """Update quantity of item in cart"""
    order = context['order']
    order_item = order.items.first()
    if order_item:
        order_item.quantity = new_quantity
        order_item.save()


@when("I remove the product from my cart")
def remove_product_from_cart(context):
    """Remove product from cart"""
    order = context['order']
    products = context.get('products', {})
    if products:
        product = list(products.values())[-1]
        order.remove_from_cart(product)


@when("I clear my cart")
def clear_cart(context):
    """Clear all items from cart"""
    order = context['order']
    order.clear_cart()


@when(parsers.parse('I try to add the product with quantity {quantity:d}'))
def try_add_with_quantity(quantity, context):
    """Try to add product with specific quantity"""
    products = context.get('products', {})
    if products:
        product = list(products.values())[-1]
        order = context['order']
        
        try:
            order.add_to_cart(product, quantity=quantity)
        except Exception as e:
            context['error'] = str(e)


@when(parsers.parse('I try to add {quantity:d} units of the product to my cart'))
def try_add_units(quantity, context):
    """Try to add multiple units to cart"""
    try_add_with_quantity(quantity, context)


@when("I view my cart")
def view_cart(context):
    """View cart - no action needed"""
    pass


@then(parsers.parse('my cart should contain {count:d} item'))
@then(parsers.parse('my cart should contain {count:d} unique item'))
@then(parsers.parse('my cart should contain {count:d} unique items'))
def verify_cart_item_count(count, context):
    """Verify number of unique items in cart"""
    order = context['order']
    order.refresh_from_db()
    actual_count = order.items.count()
    assert actual_count == count, f"Expected {count} items, got {actual_count}"


@then(parsers.parse('the cart total should be {expected_total:f}'))
def verify_cart_total(expected_total, context):
    """Verify cart total"""
    order = context['order']
    order.refresh_from_db()
    actual_total = float(order.get_total())
    assert abs(actual_total - expected_total) < 0.01, f"Expected {expected_total}, got {actual_total}"


@then(parsers.parse('the item quantity should be {expected_quantity:d}'))
def verify_item_quantity(expected_quantity, context):
    """Verify quantity of cart item"""
    order = context['order']
    order.refresh_from_db()
    order_item = order.items.first()
    assert order_item is not None
    assert order_item.quantity == expected_quantity


@then("my cart should be empty")
def verify_cart_empty(context):
    """Verify cart has no items"""
    order = context['order']
    order.refresh_from_db()
    assert order.items.count() == 0


@then(parsers.parse('I should see an error "{expected_error}"'))
def verify_error_message_cart(expected_error, context):
    """Verify error message contains expected text"""
    error = context.get('error', '')
    assert expected_error in error, f"Expected '{expected_error}' in error, got '{error}'"


@then(parsers.parse('I should see {count:d} items in cart'))
def verify_items_count(count, context):
    """Verify number of items in cart"""
    order = context['order']
    order.refresh_from_db()
    assert order.items.count() == count


@then(parsers.parse('the subtotal should be {expected_subtotal:f}'))
def verify_subtotal(expected_subtotal, context):
    """Verify cart subtotal"""
    order = context['order']
    order.refresh_from_db()
    actual_subtotal = float(order.get_subtotal())
    assert abs(actual_subtotal - expected_subtotal) < 0.01
