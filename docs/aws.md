# AWS Setup Instructions
The goal of this document is to provide a guide on how to set up the GitHub Action runner on AWS. This document will guide you through the account setup required to use this action with AWS.

## Prerequisites
- An AWS account

## Setup
1. Prepare an IAM user with AWS access keys
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
    6. In the navigation pane, choose "Users" and click "Add user".
    7. Enter a username (e.g., `gha-runner-user`) and ensure "Provide user access to the AWS Management Console" is unchecked.
    8. Select "Attach policies directly", search for the policy you created (`gha-runner-policy`), and select it.
    9. Click "Create user".
    10. Click on the newly created user, go to the "Security credentials" tab, and click "Create access key".
    11. Choose "Other", click "Next", and then copy the Access Key and Secret Access Key (or download the CSV file). These keys will not be shown again.
2. Create your GitHub Access Token
    1. This can be done with either a Personal Access Token or a Fine-Grained Personal Access Token.
    2. Go to your GitHub account settings.
    3. Click on "Developer settings".
    4. Create a new token with `repo` scope.
    5. Save and/or copy the token.
3. Add your credentials to your repository secrets
    1. Go to your repository on GitHub.
    2. Click on "Settings", then "Secrets and Variables", and then "Actions".
    3. Click "New repository secret".
    4. Add the following secrets:
      - `AWS_ACCESS_KEY_ID` - The Access Key you copied earlier.
      - `AWS_SECRET_ACCESS_KEY` - The Secret Access Key you copied earlier.
      - `GITHUB_TOKEN` - The GitHub token you copied earlier.
4. Choose an (or create) an AMI
    - We recommend Ubuntu 22.04 to stay in-line with [GitHub Actions](https://github.com/actions/runner-images#available-images)
    - To ensure compatibility, ensure that `docker` and `git` are installed on this machine
    - To create your own AMI please review these [AWS docs](https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/tkv-create-ami-from-instance.html)
    - Please see below for more information on recommendations for GPU instances

**NOTE**: If you are already using AWS for EC2, you may consider creating a [VPC](https://docs.aws.amazon.com/vpc/latest/userguide/create-vpc.html), [subnet](https://docs.aws.amazon.com/vpc/latest/userguide/create-subnets.html), and a [security group](https://docs.aws.amazon.com/vpc/latest/userguide/working-with-security-groups.html) with outbound traffic on port 443 to isolate your runners from the rest of your AWS account.

You are now ready to start using this action with AWS!

### GPU Instance Recommendations
- If you are using almost anything other than the P2 instance type, we recommend the use of [Amazon Deep Learning AMI](https://aws.amazon.com/blogs/machine-learning/get-started-with-deep-learning-using-the-aws-deep-learning-ami/)
    - For compatibility and recommendation from AWS, see [here](https://docs.aws.amazon.com/dlami/latest/devguide/gpu.html)
- The cheapest GPU option available (from P instance types) is the `p2.xlarge` however, these instances do not have support from AWS for the new Deep Learning AMI. We have created and hosted an AMI with the proper CUDA installed with Docker pre-bundled. See below for those AMIs.
- **P2 instances use version 470 for the Nvidia kernel driver. As a result, we only ship CUDA v11.4 in the AMI(s) above. You _must_ pin your `cudatoolkit` to be 11.4 to use this instance type.**
#### OMSF p2.xlarge AMI Table
| AMI | Region | Instance Type |
|-----|--------|---------------|
| ami-073f98140576b5a81 | us-east-1 | p2 |



## Additional notes for requesting GPU instances on new accounts
By default, AWS accounts have [a quota of 0 for GPU instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-on-demand-instances.html#ec2-on-demand-instances-limits). To increase your quota, use [this AWS doc](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-resource-limits.html#request-increase).


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
