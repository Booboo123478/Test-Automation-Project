import pytest
from rest_framework import status
from core.models import OrderItem, Order
from django.utils import timezone


@pytest.mark.api
class TestProductAPI:
    """Test product listing and detail endpoints"""
    
    def test_list_products(self, api_client, test_items):
        """View product list"""
        url = '/api/products/'
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5
        
        product = response.data[0]
        assert 'id' in product
        assert 'title' in product
        assert 'price' in product
        assert 'slug' in product
    
    def test_product_detail(self, api_client, test_item):
        """View product details"""
        url = f'/api/products/{test_item.id}/'
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Product'
        assert response.data['slug'] == 'test-product'
        assert 'description' in response.data
        assert 'image' in response.data
    
    @pytest.mark.django_db
    def test_product_not_found(self, api_client):
        """Product detail returns 404 for non-existent product"""
        url = '/api/products/99999/'
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
class TestShoppingCartAPI:
    """Test shopping cart operations"""
    
    def test_add_to_cart_authenticated(self, authenticated_client, test_item):
        """Add product to cart while authenticated"""
        url = '/api/add-to-cart/'
        data = {
            'slug': test_item.slug,
            'variations': []
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        assert OrderItem.objects.filter(
            item=test_item,
            ordered=False
        ).exists()
    
    def test_add_to_cart_unauthenticated(self, api_client, test_item):
        """Cannot add to cart without authentication"""
        url = '/api/add-to-cart/'
        data = {
            'slug': test_item.slug,
            'variations': []
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_add_same_item_increases_quantity(self, authenticated_client, test_item, user):
        """Adding same item twice increases quantity"""
        url = '/api/add-to-cart/'
        data = {
            'slug': test_item.slug,
            'variations': []
        }
        
        authenticated_client.post(url, data, format='json')
        
        authenticated_client.post(url, data, format='json')
        
        order_item = OrderItem.objects.get(
            item=test_item,
            user=user,
            ordered=False
        )
        assert order_item.quantity == 2
    
    def test_view_order_summary(self, authenticated_client, test_item, user):
        """View cart/order summary"""
        OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=2,
            ordered=False
        )
        order = Order.objects.create(user=user, ordered=False, ordered_date=timezone.now())
        order.items.add(OrderItem.objects.get(user=user))
        
        url = '/api/order-summary/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'order_items' in response.data
        assert len(response.data['order_items']) > 0
    
    def test_view_empty_cart(self, authenticated_client):
        """View empty cart returns 404"""
        url = '/api/order-summary/'
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_item_from_cart(self, authenticated_client, test_item, user):
        """Remove product from cart"""
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=1,
            ordered=False
        )
        order = Order.objects.create(user=user, ordered=False, ordered_date=timezone.now())
        order.items.add(order_item)
        
        url = f'/api/order-items/{order_item.id}/delete/'
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not OrderItem.objects.filter(id=order_item.id).exists()
    
    def test_update_item_quantity(self, authenticated_client, test_item, user):
        """Update product quantity in cart"""
        order_item = OrderItem.objects.create(
            user=user,
            item=test_item,
            quantity=3,
            ordered=False
        )
        order = Order.objects.create(user=user, ordered=False, ordered_date=timezone.now())
        order.items.add(order_item)
        
        url = '/api/order-item/update-quantity/'
        data = {'slug': test_item.slug}
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        order_item.refresh_from_db()
        assert order_item.quantity == 2


@pytest.mark.api  
class TestCartWithVariations:
    """Test cart with product variations"""
    
    def test_add_items_with_different_variations(self, authenticated_client, test_item, user, db):
        """Different variations create separate cart items"""
        from core.models import Variation, ItemVariation
        
        size_variation = Variation.objects.create(item=test_item, name='Size')
        small = ItemVariation.objects.create(variation=size_variation, value='Small')
        large = ItemVariation.objects.create(variation=size_variation, value='Large')
        
        url = '/api/add-to-cart/'
        
        data1 = {
            'slug': test_item.slug,
            'variations': [small.id]
        }
        authenticated_client.post(url, data1, format='json')
        
        data2 = {
            'slug': test_item.slug,
            'variations': [large.id]
        }
        authenticated_client.post(url, data2, format='json')
        
        order_items = OrderItem.objects.filter(user=user, ordered=False)
        assert order_items.count() == 2
