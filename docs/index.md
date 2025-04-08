# `gha_runner`

## Overview

The `gha_runner` is a flexible, cloud-native solution for dynamically provisioning self-hosted GitHub Action runners from Python. Designed to address the complexities of scaling and managing GitHub Actions infrastructure, this tool enables teams to create, manage, and terminate runners programmatically. This library aims to simplify the ability for developers wanting to build solutions for GitHub-native runner scaling.

## Key Features

- **Cloud Provider Support**: Designed for multi-cloud development
- **Dynamic Runner Provisioning**: Spin up and tear down runners on-demand

## Implementations
- **AWS** - [start-aws-gha-runner](https://github.com/omsf/start-aws-gha-runner) and [stop-aws-gha-runner](https://github.com/omsf/stop-aws-gha-runner). For more information, see [our AWS docs](aws.md)

## Using this library
You can install this library from [PyPI](https://pypi.org/project/gha-runner/).
```sh
pip install gha-runner
```
