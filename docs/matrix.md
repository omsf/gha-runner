# Matrix Testing with Reusable Workflows

This document explains how to use a matrix strategy with reusable workflows to run isolated test environments on AWS. Each reusable workflow manages its own `start -> test -> always-cleanup` lifecycle. This ensures that instance mappings are not lost through matrix job outputs and that each matrix job runs on its own isolated runner labels.

## Overview

The matrix strategy allows you to run the same test across multiple configurations. When using ephemeral runners, it is important that each matrix job has its own lifecycle. A monolithic workflow with a single start and stop job is not suitable for a matrix because the instance mappings would be shared or lost.

The recommended pattern is:

1. A **caller workflow** defines the matrix and invokes a reusable workflow for each matrix entry.
2. The **reusable workflow** contains the complete lifecycle: `start-aws-runner`, `test`, and `stop-aws-runner`.
3. The instance mapping is passed directly from the start job to the stop job within the reusable workflow, so it is never lost.

## Caller Workflow

The caller workflow uses a matrix strategy and calls the reusable workflow. It preserves secret passing with `secrets: inherit` and grants the necessary OIDC permissions.

```yaml
name: Matrix Test Caller

on:
  workflow_dispatch:

jobs:
  matrix-test:
    name: Run Matrix Test
    strategy:
      fail-fast: false
      matrix:
        # Use GPU instances for GPU tests to avoid advertising GPU-only tests on CPU instances.
        instance_type: ["g4dn.xlarge"]
    uses: ./.github/workflows/reusable-matrix-test.yaml
    permissions:
      id-token: write
      contents: read
    with:
      instance_type: ${{ matrix.instance_type }}
    secrets: inherit
```

## Reusable Workflow

The reusable workflow contains the full lifecycle. It accepts the `instance_type` as an input, starts the runner, runs the test on the isolated runner labels, and always stops the runner, even if the test fails.

```yaml
name: Reusable Matrix Test

on:
  workflow_call:
    inputs:
      instance_type:
        required: true
        type: string

jobs:
  start-aws-runner:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    outputs:
      mapping: ${{ steps.aws-start.outputs.mapping }}
      instances: ${{ steps.aws-start.outputs.instances }}
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd # v6.3.0
        with:
          role-to-assume: ${{ secrets.AWS_ROLE }}
          aws-region: us-east-1
      - name: Create cloud runner
        id: aws-start
        uses: omsf/start-aws-gha-runner@8523c3b2474a899636f06e6cab4829c853e107dc # v1.4.0
        with:
          aws_image_name: <The name of your AMI you want to use>
          aws_image_id: latest
          aws_instance_type: ${{ inputs.instance_type }}
          aws_home_dir: /home/ubuntu
        env:
          GH_PAT: ${{ secrets.GH_PAT }}
  test:
    runs-on: ${{ fromJSON(needs.start-aws-runner.outputs.instances) }}
    needs:
      - start-aws-runner
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - name: Run test
        run: |
          # Add your test commands here. For GPU instances, you can use nvidia-smi.
          # Avoid running GPU-only tests on CPU instances.
          echo "Running test on ${{ inputs.instance_type }}"
  stop-aws-runner:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    needs:
      - start-aws-runner
      - test
    if: ${{ always() }}
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd # v6.3.0
        with:
          role-to-assume: ${{ secrets.AWS_ROLE }}
          aws-region: us-east-1
      - name: Stop instances
        uses: omsf/stop-aws-gha-runner@a3d2e34cba8571eaf9b40ae00705d6b2b77402f6 # v1.0.0
        with:
          instance_mapping: ${{ needs.start-aws-runner.outputs.mapping }}
        env:
          GH_PAT: ${{ secrets.GH_PAT }}
```

## Key Considerations

- **fail-fast: false**: The matrix strategy uses `fail-fast: false` so that a failure in one matrix job does not cancel other jobs. Each job manages its own lifecycle independently.
- **Cleanup after test failure**: The `stop-aws-runner` job uses `if: ${{ always() }}` to ensure cleanup happens even if the test fails.
- **Isolated runner labels**: The `test` job uses `runs-on: ${{ fromJSON(needs.start-aws-runner.outputs.instances) }}` to run on the specific instances provisioned for that matrix job.
- **No lost mappings**: The `mapping` output is used directly within the reusable workflow. It is never passed as an output of the matrix job, so it cannot be lost or overwritten by other matrix jobs.
- **Secrets**: The caller uses `secrets: inherit` to pass the required secrets to the reusable workflow. The reusable workflow accesses `secrets.AWS_ROLE` and `secrets.GH_PAT`.
- **OIDC permissions**: Both the start and stop jobs have `id-token: write` permissions to allow the AWS actions to assume the role via OIDC.
- **Pinned SHAs**: All third-party actions are pinned to specific commit SHAs for security and reproducibility.
- **GPU-only tests**: If you need to run GPU-only tests, restrict the matrix to GPU instance types. Avoid advertising or running GPU-only tests on CPU instances.
