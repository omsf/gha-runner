Feature: Safeguards to prevent abuse of self-hosted runners

    Compute resources should be protected from abuse by malicious actors.
    This includes preventing forks from accessing our resources and includes
    preventing runs on untrusted PRs.

    Scenario: Forks should not be able to use our runners
        # This should be guaranteed by the fact that secrets don't propagate
        # to forks.
        Given a malicious actor's fork of our repository
        When the actor tries to run using workflow dispatch
        Then the workflow should give an error due to authorization
        And the workflow should fail to start instances on AWS

    Scenario: Pull requests from first-time contributors should not start runners
        # With default repo settings, first-time contributors should require
        # approval to run CI at all.
        Given a malicious actor's fork of our repository
        And the actor has not previously contributed to our repository
        And the actor has changed our workflow to run on PRs
        When the actor creates a pull request to our repository
        Then the workflow should give an error due to authorization
        And the workflow should fail to start instances on AWS

    Scenario: Pull requests from previous contributors should not start runners
        # With default repo settings, an external contributor who has
        # previously contributed no longer requires approval for CI to run.
        # However, this should be guaranteed because PRs from forks don't
        # have access to secrets.
        Given a malicious actor's fork of our repository
        And the actor has previously contributed to our repository
        And the actor has changed our workflow to run on PRs
        When the actor creates a pull request to our repository
        Then the workflow should give an error due to authorization
        And the workflow should fail to start instances on AWS

    # Non-tested scenario: AWS tokens (as secrets) should not leak in PRs
    # from forks because forks don't see secrets. (Leaking AWS tokens is
    # a different attack vector from the ones described above.)
