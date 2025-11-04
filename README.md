# gha-runner
![PyPI - Version](https://img.shields.io/pypi/v/gha-runner)

A simple library for building infrastructure provisioning GitHub Actions via Docker in Python. This project provides scaffolds for starting and stopping cloud instances and all the required interactions to register with the GitHub API. Additionally, we provide some helper functions for environment variable parsing and GitHub Actions native logging.

Documentation for GHA Runner may be found at: [https://gha-runner.readthedocs.io/en/latest/aws/](https://gha-runner.readthedocs.io/en/latest/aws/)

## Implementations
- [start-aws-gha-runner](https://github.com/omsf/start-aws-gha-runner) and [stop-aws-gha-runner](https://github.com/omsf/stop-aws-gha-runner) (to see this in action take a look at the example used on [AWS](docs/aws.md))

## Acknowledgements
This action was heavily inspired by the [ec2-github-runner](https://github.com/machulav/ec2-github-runner). This library takes much of its inspiration around architecture from the `ec2-github-runner` itself. Thank you to the authors of that action for providing a solid foundation to build upon.
