Feature: The orders service back-end
    As a Orders manager
    I need a RESTful ordering service
    So that I can place, ship, cancel or deliver orders

Background:
    Given the following orders
        | id            | customer_id   | order_items   |
        | 1             | 101           | [11, 12]      |
        | 2             | 102           | [21, 22, 23]  |
        | 3             | 103           | [31, 32]      |

    Given the following order_items
        | item_id   | product_id    | quantity  | price     | status    | order_id  |
        | 11        | 1234          | 2         | 35.10     | SHIPPED   | 1         |
        | 12        | 2345          | 1         | 1.5       | PLACED    | 1         |
        | 21        | 3456          | 3         | 12.2      | CANCELLED | 2         |
        | 22        | 4567          | 1         | 5.99      | SHIPPED   | 2         |
        | 23        | 5678          | 2         | 34.19     | SHIPPED   | 2         |
        | 31        | 6789          | 7         | 3.59      | DELIVERED | 3         | 
        | 32        | 7890          | 1         | 6.90      | PLACED    | 3         |     