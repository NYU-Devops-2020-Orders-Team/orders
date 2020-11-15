Feature: The orders service back-end
    As a Orders manager
    I need a RESTful ordering service
    So that I can place, ship, cancel or deliver orders

Background:
    Given the following orders
        | id            | customer_id   | order_items                                     |
        | 1             | 101           | 1234,2,35.10,SHIPPED&3456,1,1000.20,DELIVERED   |
        | 2             | 102           | 4567,3,5.60,CANCELLED                           |
        | 3             | 103           | 7890,10,10,PLACED                               |


Scenario: The Server is running
    When I visit the "Home Page"
    Then I should see "Order RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: List all orders
    When I visit the "Home Page"
    And I press the "List-All" button
    Then I should see order for customer_id "101" in the results
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