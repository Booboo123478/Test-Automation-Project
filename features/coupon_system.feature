Feature: Coupon System
  As a customer
  I want to apply discount coupons to my order
  So that I can save money on my purchase

  Scenario: Apply fixed amount coupon to order
    Given I have a cart with total value of 100.00
    And a fixed coupon "SAVE20" exists with discount value 20.00
    When I apply the coupon "SAVE20" to my order
    Then my order total should be 80.00
    And the coupon should be applied successfully

  Scenario: Apply percentage coupon to order
    Given I have a cart with total value of 100.00
    And a percentage coupon "SAVE10PCT" exists with discount value 10
    When I apply the coupon "SAVE10PCT" to my order
    Then my order total should be 90.00
    And the coupon should be applied successfully

  Scenario: Cannot apply coupon below minimum order amount
    Given I have a cart with total value of 30.00
    And a coupon "VIP50" exists with discount 10.00 and minimum order 50.00
    When I apply the coupon "VIP50" to my order
    Then I should see an error "Order does not meet minimum amount"
    And my order total should remain 30.00

  Scenario: Cannot apply expired coupon
    Given I have a cart with total value of 100.00
    And an expired coupon "EXPIRED" exists with discount 15.00
    When I apply the coupon "EXPIRED" to my order
    Then I should see an error "Coupon has expired"
    And my order total should remain 100.00

  Scenario: Cannot apply coupon that exceeded max uses
    Given I have a cart with total value of 100.00
    And a coupon "LIMITED" exists with max uses 2 and current uses 2
    When I apply the coupon "LIMITED" to my order
    Then I should see an error "Coupon has reached maximum uses"
    And my order total should remain 100.00

  Scenario: Apply coupon and calculate final total
    Given I have a cart with total value of 150.00
    And a percentage coupon "SPECIAL20" exists with discount value 20
    When I apply the coupon "SPECIAL20" to my order
    Then my order total should be 120.00
    And the discount amount should be 30.00

  Scenario: Remove applied coupon
    Given I have a cart with total value of 100.00
    And a coupon "REMOVE10" with discount 10.00 is applied to my order
    When I remove the coupon from my order
    Then my order total should be 100.00
    And no coupon should be applied
