Feature:

    Scenario: Manual kill
        Given a long-running workflow
        And I am logged in as an authorized user
        And the workflow is running
        When I kill the workflow using the GitHub UI
        Then the workflow should stop
        And the instance should terminate
