Feature: Invoices

  Scenario Outline: Create invoice
    Given I'm user with <sender_start> on my wallet
    And We have user with <receiver_email> with <receiver_start> balance in database

    When I create invoice for <transfer> to this user

    Then Operation succeeded
    And My wallet balance is <sender_result>
    And His wallet balance is <receiver_result>
    And There is one invoice record in database
    And There are invoice information in response with <transfer> sum

    Examples:
      | sender_start | receiver_start | transfer | sender_result | receiver_result | receiver_email          |
      | 100.00       | 100.00         | 100.00   | 100.00        | 100.00          | receiver_email@test.com |


  Scenario Outline: Pay for invoice succeed
    Given I'm user with <sender_start> on my wallet
    And We have user with <receiver_email> with <receiver_start> balance in database
    And He create invoice with <transfer> sum for me

    When I pay invoice to this user

    Then Operation succeeded
    And My wallet balance is <sender_result>
    And His wallet balance is <receiver_result>
    And There is no invoice record in database
    And There is one transaction record in database
    And My wallet balance is <sender_result>

    Examples:
      | sender_start | receiver_start | transfer | sender_result | receiver_result | receiver_email          |
      | 100.00       | 100.00         | 50.00    | 50.00         | 150.00          | receiver_email@test.com |


  Scenario Outline: Not enough money to pay invoice
    Given I'm user with <sender_start> on my wallet
    And We have user with <receiver_email> with <receiver_start> balance in database
    And He create invoice with <transfer> sum for me

    When I pay invoice to this user

    Then Operation isn't succeeded
    And My wallet balance is <sender_result>
    And His wallet balance is <receiver_result>
    And There is one invoice record in database
    And There are 'not enough money' error message in response

    Examples:
      | sender_start | receiver_start | transfer | sender_result | receiver_result | receiver_email          |
      | 100.00       | 100.00         | 150.00   | 100.00        | 100.00          | receiver_email@test.com |