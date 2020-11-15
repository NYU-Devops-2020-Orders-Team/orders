Feature: The orders service back-end
  As a Orders manager
  I need a RESTful ordering service
  So that I can place, ship, cancel or deliver orders

  Background:
    Given the following orders
      | customer_id | order_items                                 |
      | 101         | 1234,2,35.1,SHIPPED&3456,1,1000.2,DELIVERED |
      | 102         | 4567,3,5.60,CANCELLED                       |
      | 103         | 7890,10,10,PLACED                           |

  Scenario: The Server is running
    When I visit the "Home Page"
    Then I should see "Order RESTful Service" in the title
    And I should not see "404 Not Found"

  Scenario: List all orders
    When I visit the "Home Page"
    And I press the "List-All" button
    Then I should see the message "Success"
    And I should see order for customer_id "101" in the results
    And I should see order for customer_id "102" in the results
    And I should see order for customer_id "103" in the results
    And I should not see order for customer_id "999" in the results

  Scenario: List all orders for a customer id
    When I visit the "Home Page"
    And I set the "customer_id" to "101"
    And I press the "find-by-customer-id" button
    Then I should see order for customer_id "101" in the results
    And I should not see order for customer_id "102" in the results
    And I should not see order for customer_id "103" in the results
    And I should not see order for customer_id "999" in the results

  Scenario: List all orders for an invalid customer id
    When I visit the "Home Page"
    And I set the "customer_id" to "999"
    And I press the "find-by-customer-id" button
    Then I should not see order for customer_id "999" in the results
    And I should not see order for customer_id "102" in the results
    And I should not see order for customer_id "103" in the results
    And I should not see order for customer_id "101" in the results

  Scenario: Read an order by id
    When I visit the "Home Page"
    And I press the "List-All" button
    And I copy the "id" field
    And I press the "Reset-Form" button
    Then the "id" field should be empty
    And the "customer_id" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "101" in the "customer_id" field
    And I should see "1234" in the "item0_product_id" field
    And I should see "2" in the "item0_quantity" field
    And I should see "35.1" in the "item0_price" field
    And I should see "SHIPPED" in the "item0_status" field
    And I should see "3456" in the "item1_product_id" field
    And I should see "1" in the "item1_quantity" field
    And I should see "1000.2" in the "item1_price" field
    And I should see "DELIVERED" in the "item1_status" field


  Scenario: Read an order for an invalid id
    When I visit the "Home Page"
    And I set the "id" to "0"
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found: Order with id '0' was not found."
    And the "customer_id" field should be empty