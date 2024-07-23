# AWS Setup Instructions
The goal of this document is to provide a guide on how to set up the GitHub Action runner on AWS. This document will guide you through the account setup required to use this action with AWS.

## Prerequisites
- An AWS account

## Setup
0. Set up the OpenID Connect (OIDC) Provider
    1. Sign into your AWS Management Console.
    2. Go to the IAM Console.
    3. In the navigation pane, choose "Identity Provider".
    4. Click "Add Provider".
    5. Select "OpenID Connect" and add the following
        - Provider URL - `https://token.actions.githubusercontent.com`
        - Audience - `sts.amazonaws.com`
    6. Click "Add Provider" at the bottom of the page to assign it.
1. Prepare a Policy
    1. Sign in to your AWS Management Console.
    2. Go to the IAM console.
    3. In the navigation pane, choose "Policies" and click "Create Policy".
    4. Select the "JSON" tab, paste the following JSON, and click "Next":
        ```json
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": [
                "ec2:RunInstances",
                "ec2:TerminateInstances",
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceStatus"
              ],
              "Resource": "*"
            }
          ]
        }
        ```
    5. Name the policy (e.g., `gha-runner-policy`) and click "Create Policy".
2. Create an IAM role
    1. Sign into your AWS Management Console.
    2. Go to the IAM Console.
    3. In the navigation pane, select "Role" and then click "Create Role".
    4. Select "Web Identity" for the trusted entity type.
    5. Set your identity provider to "tokens.actions.githubusercontent.com"
    6. Set the audience to `sts.amazonaws.com`
    7. Set your GitHub auth rules:
        - GitHub organization - This would be your org or username for example, `omsf-eco-infra`. This limits it so that credentials are only given to this organization.
        - GitHub repository - This would limit the scope of this authentication to a given repo. You may choose to set or extend this in the future.
        - GitHub branch - This further restricts usage to a single branch.
    8. Click "Next".
    9. Now find and select the policy created earlier (if you used above, this would be `gha-runner-policy`) and then click "Next".
    10. Add a role name and description.
    11. Select your newly named role and copy the ARN, we will use this later.
3. Create your GitHub Access Token
    1. This can be done with either a Personal Access Token or a Fine-Grained Personal Access Token.
    2. Go to your GitHub account settings.
    3. Click on "Developer settings".
    4. Create a new token with `repo` scope.
    5. Save and/or copy the token.
4. Add your credentials to your repository secrets
    1. Go to your repository on GitHub.
    2. Click on "Settings", then "Secrets and Variables", and then "Actions".
    3. Click "New repository secret".
    4. Add the following secrets:
      - `GH_PAT` - The GitHub token you copied earlier.
5. Choose an (or create) an AMI
    - We recommend Ubuntu 22.04 to stay in-line with [GitHub Actions](https://github.com/actions/runner-images#available-images)
    - To ensure compatibility, ensure that `docker` and `git` are installed on this machine
    - To create your own AMI please review these [AWS docs](https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/tkv-create-ami-from-instance.html)
    - Please see below for more information on recommendations for GPU instances

**NOTE**: If you are already using AWS for EC2, you may consider creating a [VPC](https://docs.aws.amazon.com/vpc/latest/userguide/create-vpc.html), [subnet](https://docs.aws.amazon.com/vpc/latest/userguide/create-subnets.html), and a [security group](https://docs.aws.amazon.com/vpc/latest/userguide/working-with-security-groups.html) with outbound traffic on port 443 to isolate your runners from the rest of your AWS account.

You are now ready to start using this action with AWS!

### GPU Instance Recommendations
We recommend the use of the `g4dn.xlarge` instance type as it is a good mix of AMI compatibility with the [Amazon Deep Learning AMI](https://aws.amazon.com/blogs/machine-learning/get-started-with-deep-learning-using-the-aws-deep-learning-ami/) and low cost. The Amazon Deep Learning AMI ships with `docker`, `git`, and CUDA 12 which helps to reduce the need for developing a custom AMI for usage.


## Additional notes for requesting GPU instances on new accounts
By default, AWS accounts have [a quota of 0 for vCPUS for GPU instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-on-demand-instances.html#ec2-on-demand-instances-limits). To increase your quota, use [this AWS doc](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-resource-limits.html#request-increase). If you are going to use this action with G instances, you will want to increase your vCPU quota for G instance types, four is the minimum needed to run the `g4dn` instance.

## Example: Ubuntu
```yaml
name: Test Self-Hosted Runner
on:
  workflow_dispatch:

jobs:
  start-aws-runner:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    outputs:
      mapping: ${{ steps.aws-start.outputs.mapping }}
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: <your-IAM-Role-ARN>
          aws-region: <your-region-here>
      - name: Create cloud runner
        id: aws-start
        uses: omsf-eco-infra/gha-runner@v0.2.0
        with:
          provider: "aws"
          action: "start"
          aws_image_id: ami-XXXXXXXXXXXXXXXXX
          aws_instance_type: <your instance type here>
          aws_region_name: us-east-1
          aws_home_dir: /home/ubuntu
        env:
          GH_PAT: ${{ secrets.GH_PAT }}
  self-hosted-test:
    runs-on: self-hosted
    needs:
      - start-aws-runner
    steps:
      - uses: actions/checkout@v4
      - name: Print disk usage
        run: "df -h"
      - name: Print Docker details
        run: "docker version || true"
  stop-aws-runner:
    runs-on: ubuntu-latest
    permissions:
        id-token: write
        contents: read
    needs:
      - start-aws-runner
      - self-hosted-test
    if: ${{ always() }}
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: <your-IAM-Role-ARN>
          aws-region: us-east-1
      - name: Stop instances
        uses: omsf-eco-infra/gha-runner@v0.2.0
        with:
          provider: "aws"
          action: "stop"
          instance_mapping: ${{ needs.start-aws-runner.outputs.mapping }}
          aws_region_name: us-east-1
        env:
          GH_PAT: ${{ secrets.GH_PAT }}

```

## Useful Resources
- [AWS - Creating IAM Policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_create.html)
- [AWS - Creating an IAM User in your AWS account](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html)
- [AWS - Create a VPC](https://docs.aws.amazon.com/vpc/latest/userguide/create-vpc.html)
- [AWS - Create a subnet](https://docs.aws.amazon.com/vpc/latest/userguide/create-subnets.html)
- [AWS - Work with security groups](https://docs.aws.amazon.com/vpc/latest/userguide/working-with-security-groups.html)
- [AWS - Create an AMI from an Amazon EC2 Instance](https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/tkv-create-ami-from-instance.html)
- [AWS - On-Demand Instance Quotas](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-on-demand-instances.html#ec2-on-demand-instances-limits)
- [AWS - Request Increase](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-resource-limits.html#request-increase)
- [AWS - Get Started with Deep Learning Using the AWS Deep Learning AMI](https://aws.amazon.com/blogs/machine-learning/get-started-with-deep-learning-using-the-aws-deep-learning-ami/)
- [GitHub - Configuring OpenID Connect in Amazon Web Services](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [AltF4 - Using IAM the secure way in GitHub Actions](https://altf4.blog/blog/2024-03-03-using-iam-the-secure-way-in-github-actions/)
