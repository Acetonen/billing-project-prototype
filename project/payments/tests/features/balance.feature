Feature: Balance

  Scenario Outline: Check balance
    Given I'm user with <sender_start> on my wallet

    When I request my balance

    Then Operation succeeded
    And There are <sender_result> in response with my wallet information

    Examples:
      | sender_start | sender_result |
      | 12.00        | 12.00         |
