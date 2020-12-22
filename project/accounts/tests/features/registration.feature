Feature: Registration
    Scenario: New user registration
        Given I'm a new user
        Then There is no users and wallets in database yet

        When I send registrations credentials

        Then I should registered success
        And There are one user and one wallet in database