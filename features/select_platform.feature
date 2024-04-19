Feature: Select platform to run on

    A user should be able to select the hardware that suits the needs of
    their run.

    Scenario: Running with large memory
        Given a workflow that requires and requests a large-memory host
        When I run the workflow
        Then it should run on the appropriate large-memory host

    Scenario: Running with a single CUDA GPU
        Given a workflow that requires and requests a single CUDA GPU
        When I run the workflow
        Then it should run on hardware with a GPU
        And my software should be able to interact with the CUDA drivers

    Scenario: Running with multiple GPUs
        Given a workflow that requires and request multiple GPUs
        When I run the workflow
        Then it should run on hardware with multiple GPUs
        And my software should be able to interact with all requested GPUs

    Scenario: Running with smaller hardware
        Given a workflow that requests lower-cost hardware
        When I run the workflow
        Then it should run on the appropriate hardware

    Scenario: Running with preemptible instances
        Given a workflow that can run on preemptible hosts
        When I run the workflow
        Then it should run on a preemptible host
        # NOTE: anything about recovering from preemption is the
        # responsibility of the workflow writer

    #Scenario: Running with ROCM stack
