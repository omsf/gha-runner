# NVIDIA Brev Setup Instructions

Use [start-brev-gha-runner](https://github.com/omsf-eco-infra/start-brev-gha-runner)
and [stop-brev-gha-runner](https://github.com/omsf-eco-infra/stop-brev-gha-runner)
to create ephemeral, repository-scoped GitHub Actions runners on
[NVIDIA Brev](https://docs.nvidia.com/brev/). The actions use the Brev CLI and
the `gha-runner` deployment and teardown lifecycle.

The start action provisions instances, installs the GitHub Actions runner, and
waits for registration. Each runner accepts one job. The stop action removes
the runner registrations and **permanently deletes the Brev instances and their
storage**; it does not use `brev stop`, which retains billable storage.

## Prerequisites

- A Brev organization with access to the instance types you want to use.
- Permission to manage self-hosted runners in the target GitHub repository.
- A Linux GitHub-hosted runner, such as `ubuntu-latest`, to run these
  Docker-based actions for provisioning and cleanup.

## Setup

### Create a Brev API key

1. In the Brev organization that will own the runners, create a
   [Brev API key](https://docs.nvidia.com/brev/guides/api-keys) with
   **Read & Write** access.
2. Copy the full key when it is shown. Brev displays it only once, and it
   expires on the date you configure.
3. In your GitHub repository, go to **Settings → Secrets and variables →
   Actions** and add a repository secret named `BREV_API_KEY`.

Both actions log in with this key, which selects its Brev organization
automatically. Use a key for the same organization when starting and deleting
instances.

### Create a GitHub access token

Create a token that can manage repository self-hosted runners:

- A fine-grained personal access token with access to the target repository
  and repository **Administration: Read and write** permission; or
- A classic personal access token with the `repo` scope.

The token owner must have the required repository administration access. If
your organization requires token approval or SSO authorization, complete that
before using the token. Save it as the repository secret `GH_PAT`.

Pass `GH_PAT` to both actions; the workflow's automatic `GITHUB_TOKEN` is not a
replacement for a token able to manage repository runners.

### Choose an instance type

Use the [Brev CLI](https://docs.nvidia.com/brev/) locally to run `brev search`
and choose an available instance type. Set `brev_instance_type` to a single
type, or a comma-separated capacity fallback chain, for example
`g5.xlarge,g6.xlarge`. Availability depends on your organization and current
capacity; these example types are not guaranteed to be available.

The actions include the CLI, so you do not need to install it in the workflow.
The startup script installs the GitHub runner, not your project's dependencies;
install those in your job as needed.

## Action inputs and outputs

### Start action

| Input | Required from caller | Default | Description |
| --- | --- | --- | --- |
| `brev_instance_type` | yes | — | Instance type or comma-separated fallback chain. |
| `brev_timeout` | no | `600` | Provisioning timeout in seconds for each instance. |
| `extra_gh_labels` | no | — | Additional comma-separated GitHub runner labels. |
| `instance_count` | no | `1` | Number of runners to create. |
| `repo` | no | Current repository | Target repository in `owner/repository` format. |
| `gh_timeout` | no | `1200` | Timeout in seconds waiting for each GitHub runner to register. |

Both `BREV_API_KEY` and `GH_PAT` must be passed as environment variables.

| Output | Description |
| --- | --- |
| `mapping` | JSON object mapping Brev instance names to GitHub runner labels. Pass this to the stop action. |
| `instances` | JSON array of the generated runner labels. Use this to route jobs to the provisioned runners. |

For the default `instance_count: 1`, use
`runs-on: ${{ fromJSON(needs.start-brev-runner.outputs.instances) }}`.
If you provision multiple runners, use a job matrix over `instances` and select
one label per matrix job. A `runs-on` array means a runner must match **all**
labels; it does not distribute jobs across those runners. Each ephemeral runner
can execute only one job.

### Stop action

| Input | Required from caller | Default | Description |
| --- | --- | --- | --- |
| `instance_mapping` | yes | — | The start action's `mapping` output, a non-empty JSON object. |
| `repo` | no | Current repository | Repository containing the runner registrations, in `owner/repository` format. |

Pass `BREV_API_KEY` and `GH_PAT` as environment variables here too. If you set
`repo` on the start action, use the same value on the stop action.

## Example workflow

Save the following as `.github/workflows/brev-runner.yml`. It starts one runner,
runs a GPU check, and deletes the instance even if the test fails. The action
references are pinned to the repositories' `v1` commit SHAs.

```yaml
name: Test Brev Self-Hosted Runner

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  start-brev-runner:
    runs-on: ubuntu-latest
    outputs:
      mapping: ${{ steps.brev-start.outputs.mapping }}
      instances: ${{ steps.brev-start.outputs.instances }}
    steps:
      - name: Create Brev runner
        id: brev-start
        uses: omsf-eco-infra/start-brev-gha-runner@8caae6a56ffe6f455278dea33e20b9b8dc003d4e # v1
        with:
          brev_instance_type: g5.xlarge,g6.xlarge
          instance_count: 1
        env:
          BREV_API_KEY: ${{ secrets.BREV_API_KEY }}
          GH_PAT: ${{ secrets.GH_PAT }}

  test:
    needs: start-brev-runner
    runs-on: ${{ fromJSON(needs.start-brev-runner.outputs.instances) }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - name: Check GPU access
        run: nvidia-smi

  stop-brev-runner:
    runs-on: ubuntu-latest
    needs: [start-brev-runner, test]
    if: ${{ always() && needs.start-brev-runner.outputs.mapping != '' }}
    steps:
      - name: Delete Brev runner
        uses: omsf-eco-infra/stop-brev-gha-runner@4b88a4d25877aafb37ca29f5f49996ab0af76ab6 # v1
        with:
          instance_mapping: ${{ needs.start-brev-runner.outputs.mapping }}
        env:
          BREV_API_KEY: ${{ secrets.BREV_API_KEY }}
          GH_PAT: ${{ secrets.GH_PAT }}
```

## Cleanup and troubleshooting

- **Keep cleanup on a GitHub-hosted runner.** An ephemeral Brev runner exits
  after its job and cannot run a subsequent cleanup job.
- **Keep the mapping guard.** `always()` allows cleanup after a failed test;
  the additional check avoids calling the stop action with an empty mapping
  when startup did not produce outputs.
- **Check Brev after failed provisioning or interrupted cleanup.** A failure
  before the start action emits `mapping` can leave instances without cleanup
  outputs. Workflow cancellation or cleanup failure can also leave resources
  behind. Inspect your Brev organization and delete leftover instances
  manually; do not treat this workflow as a billing safeguard.
- **Missing GitHub registration does not prevent instance deletion.** The stop
  action uses the supplied mapping even if an ephemeral runner has already
  unregistered itself.
- **Registration timeout:** check the Brev instance's startup logs and network
  access to GitHub. Increase `brev_timeout` for slow provisioning or
  `gh_timeout` for slow runner registration as appropriate.
- **Authentication failure:** check API-key expiration, its organization and
  Read & Write access, and the GitHub token's repository access and permissions.

Run only trusted code on these self-hosted runners. Do not expose the workflow
or its credentials to untrusted pull requests. Upload any needed artifacts
before cleanup: deleting an instance also deletes its storage.

## Useful resources

- [NVIDIA Brev documentation](https://docs.nvidia.com/brev/)
- [Brev API keys](https://docs.nvidia.com/brev/guides/api-keys)
- [Start action source and README](https://github.com/omsf-eco-infra/start-brev-gha-runner)
- [Stop action source and README](https://github.com/omsf-eco-infra/stop-brev-gha-runner)
- [GitHub self-hosted runner security](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#hardening-for-self-hosted-runners)
