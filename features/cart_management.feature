Feature: Smart Cart Management
  As a customer
  I want to manage items in my shopping cart
  So that I can prepare my order before checkout

  Scenario: Add item to empty cart
    Given I am logged in as a customer
    And a product "Blue T-Shirt" exists with price 29.99 and stock 10
    When I add the product to my cart
    Then my cart should contain 1 item
    And the cart total should be 29.99

  Scenario: Add same item twice merges quantities
    Given I am logged in as a customer
    And a product "Red Hoodie" exists with price 49.99 and stock 20
    And the product is already in my cart with quantity 2
    When I add the product to my cart again
    Then my cart should contain 1 unique item
    And the item quantity should be 3
    And the cart total should be 149.97

  Scenario: Add multiple different items to cart
    Given I am logged in as a customer
    And a product "Sneakers" exists with price 79.99 and stock 15
    And a product "Socks" exists with price 9.99 and stock 50
    When I add "Sneakers" to my cart
    And I add "Socks" to my cart
    Then my cart should contain 2 unique items
    And the cart total should be 89.98

  Scenario: Update item quantity in cart
    Given I am logged in as a customer
    And a product "Jacket" exists with price 99.99 and stock 10
    And the product is in my cart with quantity 1
    When I update the cart item quantity to 3
    Then the item quantity should be 3
    And the cart total should be 299.97

  Scenario: Remove item from cart
    Given I am logged in as a customer
    And a product "Hat" exists with price 19.99 and stock 25
    And the product is in my cart with quantity 2
    When I remove the product from my cart
    Then my cart should be empty
    And the cart total should be 0.00

  Scenario: Clear entire cart
    Given I am logged in as a customer
    And multiple products are in my cart
    When I clear my cart
    Then my cart should be empty
    And the cart total should be 0.00

  Scenario: Cannot add negative quantity
    Given I am logged in as a customer
    And a product "Scarf" exists with price 24.99 and stock 10
    When I try to add the product with quantity -1
    Then I should see an error "Quantity must be positive"
    And my cart should be empty

  Scenario: Cannot add more items than stock available
    Given I am logged in as a customer
    And a product "Limited Edition" exists with price 199.99 and stock 2
    When I try to add 5 units of the product to my cart
    Then I should see an error "Insufficient stock available"
    And my cart should be empty

  Scenario: View cart summary
    Given I am logged in as a customer
    And a product "Shirt" exists with price 39.99 and stock 10
    And a product "Pants" exists with price 59.99 and stock 10
    And "Shirt" is in my cart with quantity 2
    And "Pants" is in my cart with quantity 1
    When I view my cart
    Then I should see 2 items in cart
    And the subtotal should be 139.97
