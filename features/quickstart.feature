Feature: Quickstart guide

    There should be a quick and easy way to set up workflows, and a simple
    demo workflow.

    Scenario: Easy set-up of for first-time users
        Given I have AWS credentials
        And I have not previously set up AWS infra for this tool
        When I use the quickstart command
        Then I should have a working workflow
