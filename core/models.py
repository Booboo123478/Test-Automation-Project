from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField


CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()
    stock_quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })
    
    # =============================================================================
    # TDD GREEN CYCLE - Feature 1: Product Stock Management
    # Tests: test_tdd_feature1_stock.py & test_tdd_feature1_refactor.py
    # =============================================================================
    
    def is_in_stock(self):
        """Check if item is in stock
        TDD: test_item_is_in_stock_method, test_item_is_out_of_stock
        """
        return self.stock_quantity > 0
    
    def can_fulfill(self, quantity):
        """Check if requested quantity can be fulfilled
        TDD: test_can_fulfill_quantity_method
        """
        return self.stock_quantity >= quantity
    
    def reduce_stock(self, quantity):
        """Reduce stock by quantity
        TDD: test_reduce_stock_method, test_cannot_reduce_stock_below_zero
        Raises ValueError if insufficient stock
        """
        if quantity > self.stock_quantity:
            raise ValueError("Insufficient stock available")
        self.stock_quantity -= quantity
        self.save()
    
    def increase_stock(self, quantity):
        """Increase stock by quantity (restocking)
        TDD: test_increase_stock_restocking
        """
        self.stock_quantity += quantity
        self.save()
    
    def get_stock_status(self):
        """Get stock status category
        TDD: test_stock_status_categories
        Returns: 'OUT_OF_STOCK', 'LOW_STOCK', or 'IN_STOCK'
        """
        if self.stock_quantity == 0:
            return 'OUT_OF_STOCK'
        elif self.stock_quantity <= 5:
            return 'LOW_STOCK'
        return 'IN_STOCK'


class Variation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # size

    class Meta:
        unique_together = (
            ('item', 'name')
        )

    def __str__(self):
        return self.name


class ItemVariation(models.Model):
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)
    value = models.CharField(max_length=50)  # S, M, L
    attachment = models.ImageField(blank=True)

    class Meta:
        unique_together = (
            ('variation', 'value')
        )

    def __str__(self):
        return self.value


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    item_variations = models.ManyToManyField(ItemVariation)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    # =============================================================================
    # TDD GREEN CYCLE - Feature 2 & 3: Order Totals & Cart Management
    # Tests: test_tdd_feature2_*.py & test_tdd_feature3_*.py
    # =============================================================================

    def get_subtotal(self):
        """Get order subtotal before discounts
        TDD: test_order_total_with_percentage_coupon, test_order_total_with_fixed_coupon
        """
        from decimal import Decimal
        total = Decimal('0')
        for order_item in self.items.all():
            total += Decimal(str(order_item.get_final_price()))
        return total

    def get_total(self):
        """Get order total with coupon discount applied
        TDD: test_order_total_with_percentage_coupon, test_coupon_cannot_exceed_order_total
        """
        from decimal import Decimal
        total = self.get_subtotal()
        
        if self.coupon:
            # Use new coupon system if available
            if hasattr(self.coupon, 'discount_type'):
                discount = self.coupon.calculate_discount(total)
                total -= discount
            else:
                # Fallback to old amount field
                total -= Decimal(str(self.coupon.amount))
        
        # Ensure total is not negative
        if total < Decimal('0'):
            total = Decimal('0')
        
        return total
    
    # =============================================================================
    # TDD GREEN CYCLE - Feature 3: Smart Cart Item Merging
    # Tests: test_tdd_feature3_cart.py & test_tdd_feature3_refactor.py
    # =============================================================================
    
    def add_to_cart(self, item, quantity=1):
        """Add item to cart or update quantity if exists
        TDD: test_adding_same_item_increases_quantity, test_cart_prevents_negative_quantities
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if not item.can_fulfill(quantity):
            raise ValueError(f"Insufficient stock available. Only {item.stock_quantity} in stock.")
        
        # Check if item already in cart
        order_item_qs = self.items.filter(item=item, ordered=False)
        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.quantity += quantity
            order_item.save()
        else:
            order_item = OrderItem.objects.create(
                user=self.user,
                item=item,
                quantity=quantity,
                ordered=False
            )
            self.items.add(order_item)
    
    def remove_from_cart(self, item):
        """Remove item completely from cart
        TDD: test_order_has_remove_from_cart_method
        """
        order_item_qs = self.items.filter(item=item, ordered=False)
        if order_item_qs.exists():
            order_item = order_item_qs.first()
            self.items.remove(order_item)
            order_item.delete()
    
    def clear_cart(self):
        """Remove all items from cart
        TDD: test_clear_cart_removes_all_items
        """
        for order_item in self.items.filter(ordered=False):
            order_item.delete()
        self.items.clear()


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# =============================================================================
# TDD GREEN CYCLE - Feature 2: Enhanced Coupon System
# Tests: test_tdd_feature2_coupons.py & test_tdd_feature2_refactor.py
# =============================================================================

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage'),
    )
    
    code = models.CharField(max_length=15)
    amount = models.FloatField()  # Keep for backwards compatibility
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='fixed')
    discount_value = models.FloatField(default=0)
    minimum_order_amount = models.FloatField(default=0.0)
    expiry_date = models.DateTimeField(blank=True, null=True)
    max_uses = models.IntegerField(blank=True, null=True)
    current_uses = models.IntegerField(default=0)

    def __str__(self):
        return self.code
    
    def calculate_discount(self, order_total):
        """Calculate discount amount based on type
        TDD: test_percentage_coupon_calculation, test_fixed_amount_coupon_calculation
        Supports both percentage and fixed amount discounts
        """
        from decimal import Decimal
        order_total = Decimal(str(order_total))
        
        if self.discount_type == 'percentage':
            discount = order_total * (Decimal(str(self.discount_value)) / Decimal('100'))
        else:  # fixed
            discount = Decimal(str(self.discount_value))
        
        # Ensure discount doesn't exceed order total
        if discount > order_total:
            discount = order_total
        
        return discount
    
    def is_valid_for_amount(self, amount):
        """Check if order amount meets minimum requirement
        TDD: test_coupon_minimum_order_requirement
        """
        from decimal import Decimal
        return Decimal(str(amount)) >= Decimal(str(self.minimum_order_amount))
    
    def is_active(self):
        """Check if coupon is active (not expired)
        TDD: test_coupon_expiration_date, test_expired_coupon_validation
        """
        if self.expiry_date is None:
            return True
        from django.utils import timezone
        return timezone.now() <= self.expiry_date
    
    def can_be_used(self):
        """Check if coupon has usage remaining
        TDD: test_coupon_usage_limit, test_coupon_usage_tracking_and_limits
        """
        if self.max_uses is None:
            return True
        return self.current_uses < self.max_uses
    
    def increment_usage(self):
        """Increment usage counter
        TDD: test_coupon_usage_tracking_and_limits
        """
        self.current_uses += 1
        self.save()


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
