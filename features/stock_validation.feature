Feature: Product Stock Validation
  As a customer
  I want to know if products are in stock
  So that I don't try to purchase unavailable items

  Scenario: Check product with available stock
    Given a product "Blue Sneakers" exists with stock quantity 10
    When I check if the product is in stock
    Then the product should be available

  Scenario: Check product out of stock
    Given a product "Red Hat" exists with stock quantity 0
    When I check if the product is in stock
    Then the product should not be available

  Scenario: Verify product stock quantity
    Given a product "Green Backpack" exists with stock quantity 25
    Then the product stock quantity should be 25

  Scenario: Product becomes out of stock
    Given a product "Yellow Socks" exists with stock quantity 3
    When the stock quantity is reduced to 0
    Then the product should not be available

  Scenario: Restock a product
    Given a product "Black Jacket" exists with stock quantity 0
    When I restock the product with 15 units
    Then the product should be available
    And the product stock quantity should be 15

  Scenario: Cannot add out of stock item to cart
    Given a product "White Shoes" exists with stock quantity 0
    And I am a logged in customer
    When I attempt to add the product to cart
    Then I should see an error message "Product is out of stock"
    And the product should not be added to cart

  Scenario: Add in-stock item to cart
    Given a product "Purple Shirt" exists with stock quantity 50
    And I am a logged in customer
    When I add 2 units of the product to cart
    Then the product should be in my cart
    And my cart should have 2 units of the product
