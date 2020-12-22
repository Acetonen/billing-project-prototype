Feature: Make deposits

  Scenario Outline: Make deposits for self
    Given I'm user with <sender_start> on my wallet
    And There is no transactions in database

    When I make deposits <transfer> to my wallet

    Then Operation succeeded
    And My wallet balance is <sender_result>
    And There is one transaction record in database
    And There are <sender_result> in response with my wallet information

    Examples:
      | sender_start | sender_result | transfer |
      | 0            | 666.00        | 666.00   |


  Scenario Outline: Make deposits for another user
    Given We have user with <receiver_email> with <receiver_start> balance in database
    And There is no transactions in database

    When I make deposits <transfer> to his wallet

    Then Operation succeeded
    And His wallet balance is <receiver_result>
    And There is one transaction record in database
    And There are success response

    Examples:
      | receiver_start | transfer | receiver_result | receiver_email          |
      | 0              | 666.00   | 666.00          | receiver_email@test.com |