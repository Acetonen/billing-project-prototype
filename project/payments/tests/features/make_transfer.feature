Feature: Make transfer

  Scenario Outline: Transfer to another user success
    Given I'm user with <sender_start> on my wallet
    And We have user with <receiver_email> with <receiver_start> balance in database

    When I send <transfer> to his wallet

    Then Operation succeeded
    And My wallet balance is <sender_result>
    And His wallet balance is <receiver_result>
    And There is one transaction record in database
    And There are <sender_result> in response with my wallet information

    Examples:
      | sender_start | receiver_start | transfer | sender_result | receiver_result | receiver_email          |
      | 100.00       | 0              | 70.00    | 30.00         | 70.00           | receiver_email@test.com |


  Scenario Outline: Not enough money to make transfer
    Given I'm user with <sender_start> on my wallet
    And We have user with <receiver_email> with <receiver_start> balance in database

    When I send <transfer> to his wallet

    Then Operation isn't succeeded
    And My wallet balance is <sender_result>
    And His wallet balance is <receiver_result>
    And There is no transactions in database
    And There are 'not enough money' error message in response

    Examples:
      | sender_start | receiver_start | transfer | sender_result | receiver_result | receiver_email          |
      | 100.00       | 0              | 150.00   | 100           | 0               | receiver_email@test.com |


  Scenario Outline: Can't transfer to yourself
    Given I'm user with <sender_start> on my wallet

    When I send <transfer> to myself

    Then Operation isn't succeeded
    And My wallet balance is <sender_result>
    And There is no transactions in database
    And There are 'can't receive to yourself' error message in response

    Examples:
      | sender_start | transfer | sender_result |
      | 100.00       | 150.00   | 100           |