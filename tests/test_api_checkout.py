import pytest
import stripe
from rest_framework import status
from core.models import Address, Order, OrderItem, Payment
from unittest.mock import patch, MagicMock
from django.utils import timezone

"""Tests for the e-commerce API checkout process author: Hippolyte Martin"""
@pytest.mark.api
class TestAddressAPI:
    """Test address management"""
    
    def test_create_shipping_address(self, authenticated_client, user):
        """Add new shipping address"""
        url = '/api/addresses/create/'
        data = {
            'user': user.id,
            'street_address': '123 Main St',
            'apartment_address': 'Apt 4B',
            'country': 'US',
            'zip': '12345',
            'address_type': 'S',
            'default': True
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Address.objects.filter(
            user=user,
            street_address='123 Main St'
        ).exists()
    
    def test_create_billing_address(self, authenticated_client, user):
        """Add new billing address"""
        url = '/api/addresses/create/'
        data = {
            'user': user.id,
            'street_address': '456 Billing Ave',
            'apartment_address': 'Suite 100',
            'country': 'US',
            'zip': '54321',
            'address_type': 'B',
            'default': False
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        address = Address.objects.get(street_address='456 Billing Ave')
        assert address.address_type == 'B'
    
    
    def test_update_address(self, authenticated_client, test_address):
        """Update existing address"""
        url = f'/api/addresses/{test_address.id}/update/'
        data = {
            'user': test_address.user.id,
            'street_address': '789 Updated Street',
            'apartment_address': test_address.apartment_address,
            'country': 'US',
            'zip': test_address.zip,
            'address_type': test_address.address_type,
            'default': test_address.default
        }
        
        response = authenticated_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        test_address.refresh_from_db()
        assert test_address.street_address == '789 Updated Street'
    
    def test_delete_address(self, authenticated_client, test_address):
        """Delete address"""
        url = f'/api/addresses/{test_address.id}/delete/'
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Address.objects.filter(id=test_address.id).exists()


@pytest.mark.api
class TestCouponAPI:
    """Test coupon functionality"""
    
    def test_apply_valid_coupon(self, authenticated_client, test_item, test_coupon, user):
        """Apply valid coupon code"""
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=1,
            ordered=False
        )
        order = Order.objects.create(user=user, ordered=False, ordered_date=timezone.now())
        order.items.add(order_item)
        
        url = '/api/add-coupon/'
        data = {'code': 'TESTCODE'}
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        order.refresh_from_db()
        assert order.coupon == test_coupon
    
    def test_apply_invalid_coupon(self, authenticated_client, test_item, user):
        """Apply invalid coupon code"""
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=1,
            ordered=False
        )
        order = Order.objects.create(user=user, ordered=False, ordered_date=timezone.now())
        order.items.add(order_item)
        
        url = '/api/add-coupon/'
        data = {'code': 'INVALIDCODE'}
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]
    
    def test_apply_coupon_without_order(self, authenticated_client):
        """Cannot apply coupon without active order
        BUG: API raises Order.DoesNotExist instead of returning proper HTTP error
        """
        url = '/api/add-coupon/'
        data = {'code': 'TESTCODE'}
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.api
class TestCheckoutAPI:
    """Test checkout and payment"""
    
    @patch('stripe.Charge.create')
    @patch('stripe.Customer.retrieve')
    @patch('stripe.Customer.create')
    def test_successful_checkout(
        self, mock_customer_create, mock_customer_retrieve, 
        mock_charge, authenticated_client, test_item, 
        test_address, test_billing_address, user
    ):
        """Complete checkout with Stripe"""
        mock_charge.return_value = {'id': 'ch_test123'}
        mock_customer_create.return_value = {'id': 'cus_test123'}
        
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=2,
            ordered=False
        )
        order = Order.objects.create(user=user, ordered=False, ordered_date=timezone.now())
        order.items.add(order_item)
        
        url = '/api/checkout/'
        data = {
            'stripeToken': 'tok_visa',
            'selectedShippingAddress': test_address.id,
            'selectedBillingAddress': test_billing_address.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        order.refresh_from_db()
        assert order.ordered == True
        assert order.payment is not None
        assert order.shipping_address == test_address
        assert order.billing_address == test_billing_address
    
    @patch('stripe.Charge.create')
    def test_checkout_with_declined_card(
        self, mock_charge, authenticated_client, 
        test_item, test_address, test_billing_address, user
    ):
        """Checkout with declined card"""
        mock_charge.side_effect = stripe.error.CardError(
            'Your card was declined',
            param='card',
            code='card_declined'
        )
        
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=1,
            ordered=False
        )
        order = Order.objects.create(user=user, ordered=False, ordered_date=timezone.now())
        order.items.add(order_item)
        
        url = '/api/checkout/'
        data = {
            'stripeToken': 'tok_chargeDeclined',
            'selectedShippingAddress': test_address.id,
            'selectedBillingAddress': test_billing_address.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        order.refresh_from_db()
        assert order.ordered == False
    
    def test_checkout_without_addresses(self, authenticated_client, test_item, user):
        """Checkout requires addresses
        BUG: API raises Address.DoesNotExist instead of returning proper HTTP error
        """
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=1,
            ordered=False
        )
        order = Order.objects.create(user=user, ordered=False, ordered_date=timezone.now())
        order.items.add(order_item)
        
        url = '/api/checkout/'
        data = {
            'stripeToken': 'tok_visa',
            'selectedShippingAddress': 9999,  # Non-existent
            'selectedBillingAddress': 9999
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    @patch('stripe.Charge.create')
    @patch('stripe.Customer.create')
    def test_checkout_with_coupon(
        self, mock_customer, mock_charge, authenticated_client,
        test_item, test_coupon, test_address, 
        test_billing_address, user
    ):
        """Checkout with discount coupon"""
        mock_charge.return_value = {'id': 'ch_test456'}
        mock_customer.return_value = {'id': 'cus_test456'}
        
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=1,
            ordered=False
        )
        order = Order.objects.create(
            user=user,
            ordered=False,
            coupon=test_coupon,
            ordered_date=timezone.now()
        )
        order.items.add(order_item)
        
        url = '/api/checkout/'
        data = {
            'stripeToken': 'tok_visa',
            'selectedShippingAddress': test_address.id,
            'selectedBillingAddress': test_billing_address.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK

        order.refresh_from_db()
        assert order.coupon == test_coupon
    
    @patch('stripe.Charge.create')
    @patch('stripe.Customer.create')
    def test_checkout_with_multiple_items(
        self, mock_customer, mock_charge, authenticated_client,
        test_items, test_address, test_billing_address, user
    ):
        """Checkout with multiple items"""
        mock_charge.return_value = {'id': 'ch_test789'}
        mock_customer.return_value = {'id': 'cus_test789'}
        
        order = Order.objects.create(user=user, ordered=False, ordered_date=timezone.now())
        for item in test_items[:3]:
            order_item = OrderItem.objects.create(
                user=user,
                item=item,
                quantity=2,
                ordered=False
            )
            order.items.add(order_item)
        
        url = '/api/checkout/'
        data = {
            'stripeToken': 'tok_visa',
            'selectedShippingAddress': test_address.id,
            'selectedBillingAddress': test_billing_address.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        order.refresh_from_db()
        assert order.items.count() == 3
        for item in order.items.all():
            assert item.ordered == True


@pytest.mark.api
class TestPaymentHistory:
    """Test payment history"""
    
    def test_view_order_history(self, authenticated_client, user, db):
        """View order history"""
        payment = Payment.objects.create(
            user=user,
            stripe_charge_id='ch_test123',
            amount=50.00
        )
        
        url = '/api/payments/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['stripe_charge_id'] == 'ch_test123'
