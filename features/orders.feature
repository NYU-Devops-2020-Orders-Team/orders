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
      | 104         | 1000,10,10,DELIVERED                        |

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
    And I set the "customer_id" to "101"
    And I press the "find-by-customer-id" button
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


  Scenario: Create an Order
    When I visit the "Home Page"
    And I set the "customer_id" to "145"
    And I set the "item0_product_id" to "21"
    And I set the "item0_quantity" to "5"
    And I set the "item0_price" to "10.99"
    And I select "Placed" in the "item0_status" dropdown
    And I press the "add-row" button
    And I set the "item1_product_id" to "123"
    And I set the "item1_quantity" to "1"
    And I set the "item1_price" to "18"
    And I select "Shipped" in the "item1_status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Reset-Form" button
    Then the "id" field should be empty
    And the "customer_id" field should be empty
    And the "item0_product_id" field should be empty
    And the "item0_quantity" field should be empty
    And the "item0_price" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "145" in the "customer_id" field
    And I should see "21" in the "item0_product_id" field
    And I should see "5" in the "item0_quantity" field
    And I should see "10.99" in the "item0_price" field
    And I should see "Placed" in the "item0_status" dropdown
    And I should see "123" in the "item1_product_id" field
    And I should see "1" in the "item1_quantity" field
    And I should see "18" in the "item1_price" field
    And I should see "Shipped" in the "item1_status" dropdown

  Scenario: Create an Order for an invalid customer id
    When I visit the "Home Page"
    And I set the "customer_id" to "abc"
    And I set the "item0_product_id" to "21"
    And I set the "item0_quantity" to "5"
    And I set the "item0_price" to "10.99"
    And I select "Placed" in the "item0_status" dropdown
    And I press the "Create" button
    Then I should see the message "Customer Id must be integer"

  Scenario: Create an Order missing customer id
    When I visit the "Home Page"
    And I set the "customer_id" to "abc"
    And I set the "item0_product_id" to "21"
    And I set the "item0_quantity" to "5"
    And I set the "item0_price" to "10.99"
    And I select "Placed" in the "item0_status" dropdown
    And I press the "Create" button
    Then I should see the message "Customer Id must be integer"

  Scenario: Create an Order missing order items
    When I visit the "Home Page"
    And I set the "customer_id" to "123"
    And I press the "Create" button
    Then I should see the message "Invalid order: invalid product ID"

  Scenario: Create an Order missing product id
    When I visit the "Home Page"
    And I set the "customer_id" to "123"
    And I set the "item0_quantity" to "5"
    And I set the "item0_price" to "10.99"
    And I select "Placed" in the "item0_status" dropdown
    And I press the "Create" button
    Then I should see the message "Invalid order: invalid product ID"

  Scenario: Create an Order missing quantity
    When I visit the "Home Page"
    And I set the "customer_id" to "123"
    And I set the "item0_product_id" to "21"
    And I set the "item0_price" to "10.99"
    And I select "Placed" in the "item0_status" dropdown
    And I press the "Create" button
    Then I should see the message "Invalid order: invalid quantity"

  Scenario: Create an Order missing price
    When I visit the "Home Page"
    And I set the "customer_id" to "123"
    And I set the "item0_product_id" to "21"
    And I set the "item0_quantity" to "5"
    And I select "Placed" in the "item0_status" dropdown
    And I press the "Create" button
    Then I should see the message "Invalid order: invalid price"

  Scenario: Create an Order missing status
    When I visit the "Home Page"
    And I set the "customer_id" to "123"
    And I set the "item0_product_id" to "21"
    And I set the "item0_quantity" to "5"
    And I set the "item0_price" to "10.99"
    And I press the "Create" button
    Then I should see the message "Invalid order: invalid status"


  Scenario: Cancel an Order with placed items
    When I visit the "Home Page"
    And I set the "customer_id" to "103"
    And I press the "find-by-customer-id" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Reset-Form" button
    Then the "id" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "Placed" in the "item0_status" dropdown
    When I press the "cancel" button
    Then I should see the message "Success"
    And I should see "Cancelled" in the "item0_status" dropdown

  Scenario: Cancel an Order with shipped/delivered items
    When I visit the "Home Page"
    And I set the "customer_id" to "101"
    And I press the "find-by-customer-id" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Reset-Form" button
    Then the "id" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "Shipped" in the "item0_status" dropdown
    And I should see "Delivered" in the "item1_status" dropdown
    When I press the "cancel" button
    Then I should see the message "All the items have been shipped/delivered. Nothing to cancel"

  Scenario: Cancel an Order with cancelled items
    When I visit the "Home Page"
    And I set the "customer_id" to "102"
    And I press the "find-by-customer-id" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Reset-Form" button
    Then the "id" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "Cancelled" in the "item0_status" dropdown
    When I press the "cancel" button
    Then I should see the message "Success"


  Scenario: Delete an order by id
    When I visit the "Home Page"
    And I press the "List-All" button
    Then I should see the message "Success"
    And I should see order for customer_id "101" in the results
    And I should see order for customer_id "102" in the results
    And I should see order for customer_id "103" in the results
    When I copy the "id" field
    And I press the "Reset-Form" button
    Then the "id" field should be empty
    And the "customer_id" field should be empty
    When I paste the "id" field
    And I press the "Delete" button
    And I press the "List-All" button
    Then I should see the message "Success"
    And I should see order for customer_id "102" in the results
    And I should see order for customer_id "103" in the results
    And I should not see order for customer_id "101" in the results

  Scenario: Delete an order by id missing id
    When I visit the "Home Page"
    And I press the "List-All" button
    Then I should see the message "Success"
    And I should see order for customer_id "101" in the results
    And I should see order for customer_id "102" in the results
    And I should see order for customer_id "103" in the results
    And I should not see order for id "999" in the results
    When I press the "Reset-Form" button
    Then the "id" field should be empty
    And the "customer_id" field should be empty
    When I set the "id" to "999"
    And I press the "Delete" button
    And I press the "List-All" button
    Then I should see the message "Success"
    And I should see order for customer_id "101" in the results
    And I should see order for customer_id "102" in the results
    And I should see order for customer_id "103" in the results
    And I should not see order for id "999" in the results


  Scenario: Deliver order with shipped 
    When I visit the "Home Page"
    And I set the "customer_id" to "145"
    And I set the "item0_product_id" to "21"
    And I set the "item0_quantity" to "5"
    And I set the "item0_price" to "10.99"
    And I select "Shipped" in the "item0_status" dropdown
    And I press the "add-row" button
    And I set the "item1_product_id" to "123"
    And I set the "item1_quantity" to "1"
    And I set the "item1_price" to "18"
    And I select "Shipped" in the "item1_status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Reset-form" button
    And I paste the "id" field
    And I press the "Retrieve" button
    And I press the "Deliver" button
    Then I should see "145" in the "customer_id" field
    And I should see "21" in the "item0_product_id" field
    And I should see "5" in the "item0_quantity" field
    And I should see "10.99" in the "item0_price" field
    And I should see "Delivered" in the "item0_status" dropdown
    And I should see "123" in the "item1_product_id" field
    And I should see "1" in the "item1_quantity" field
    And I should see "18" in the "item1_price" field
    And I should see "Delivered" in the "item1_status" dropdown

  Scenario: Deliver order with placed and delivered
    When I visit the "Home Page"
    And I set the "customer_id" to "145"
    And I set the "item0_product_id" to "21"
    And I set the "item0_quantity" to "5"
    And I set the "item0_price" to "10.99"
    And I select "Shipped" in the "item0_status" dropdown
    And I press the "add-row" button
    And I set the "item1_product_id" to "123"
    And I set the "item1_quantity" to "1"
    And I set the "item1_price" to "18"
    And I select "Placed" in the "item1_status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I paste the "id" field
    And I press the "Deliver" button
    Then I should see the message "At least one item in this order is PLACED, order cannot be delivered."

  Scenario: Deliver order with all cancelled
    When I visit the "Home Page"
    And I set the "customer_id" to "145"
    And I set the "item0_product_id" to "21"
    And I set the "item0_quantity" to "5"
    And I set the "item0_price" to "10.99"
    And I select "Cancelled" in the "item0_status" dropdown
    And I press the "add-row" button
    And I set the "item1_product_id" to "123"
    And I set the "item1_quantity" to "1"
    And I set the "item1_price" to "18"
    And I select "Cancelled" in the "item1_status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I paste the "id" field
    And I press the "Deliver" button
    Then I should see the message "All the items in this order are CANCELLED, no items can be delivered."

  Scenario: Deliver order with all delivered
    When I visit the "Home Page"
    And I set the "customer_id" to "145"
    And I set the "item0_product_id" to "21"
    And I set the "item0_quantity" to "5"
    And I set the "item0_price" to "10.99"
    And I select "Delivered" in the "item0_status" dropdown
    And I press the "add-row" button
    And I set the "item1_product_id" to "123"
    And I set the "item1_quantity" to "1"
    And I set the "item1_price" to "18"
    And I select "Delivered" in the "item1_status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I paste the "id" field
    And I press the "Deliver" button
    Then I should see "145" in the "customer_id" field
    And I should see "21" in the "item0_product_id" field
    And I should see "5" in the "item0_quantity" field
    And I should see "10.99" in the "item0_price" field
    And I should see "Delivered" in the "item0_status" dropdown
    And I should see "123" in the "item1_product_id" field
    And I should see "1" in the "item1_quantity" field
    And I should see "18" in the "item1_price" field
    And I should see "Delivered" in the "item1_status" dropdown


  Scenario: Ship an Order with placed items
    When I visit the "Home Page"
    And I set the "customer_id" to "103"
    And I press the "find-by-customer-id" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Reset-Form" button
    Then the "id" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    And I press the "ship" button
    Then I should see "Shipped" in the "item0_status" dropdown

  Scenario: Ship an Order with some shipped and delivered items
    When I visit the "Home Page"
    And I set the "customer_id" to "101"
    And I press the "find-by-customer-id" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Reset-Form" button
    Then the "id" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "Shipped" in the "item0_status" dropdown
    And I should see "Delivered" in the "item1_status" dropdown
    When I press the "ship" button
    Then I should see the message "Success"

  Scenario: Ship an Order with all delivered items
    When I visit the "Home Page"
    And I set the "customer_id" to "104"
    And I press the "find-by-customer-id" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Reset-Form" button
    Then the "id" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    When I press the "ship" button
    Then I should see the message "All the items in this order are DELIVERED/SHIPPED/CANCELED, no items can be shipped."

  Scenario: Ship an Order with all cancelled items
    When I visit the "Home Page"
    And I set the "customer_id" to "102"
    And I press the "find-by-customer-id" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Reset-Form" button
    Then the "id" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "Cancelled" in the "item0_status" dropdown
    When I press the "ship" button
    Then I should see the message "All the items in this order are DELIVERED/SHIPPED/CANCELED, no items can be shipped."
