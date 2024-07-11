# AWS Setup Instructions
The goal of this document is to provide a guide on how to set up the GitHub Action runner on AWS. This document will guide you through the account setup required to use this action with AWS.

## Prerequisites
- An AWS account

## Setup
1. Prepare an IAM user with AWS access keys
    1. Go to the AWS Management Console and sign in to your account.
    2. Go to the IAM console.
    3. In the navigation pane, choose Policies.
    4. Create a new policy by clicking "Create Policy".
    5. Next, click JSON and paste the following JSON with the required permissions and then click "Next".
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
    6. Name the policy (for example: `gha-runner-policy`) and select "Create Policy".
    7. Now select "Users" in the navigation pane and click "Add user".
    8. Enter a username (for example: `gha-runner-user`) and ensure that "Provide user access to the AWS Management Console" is unchecked.
    9. Select "Attach policies directly" and search for the policy you created earlier (`gha-runner-policy`) and select it.
    10. Then click, "Create user".
    11. Next, click on the user you just created and go to the "Security credentials" tab.
    12. Click "Create access key" and then click "Other" and then "Next".
    13. Click next and then copy the Access Key and Secret Access Key (or download the CSV file), these will not be shown again.
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

**NOTE**: If you are already using AWS for EC2, you may consider creating a [VPC](https://docs.aws.amazon.com/vpc/latest/userguide/create-vpc.html), [subnet](https://docs.aws.amazon.com/vpc/latest/userguide/create-subnets.html), and a [security group](https://docs.aws.amazon.com/vpc/latest/userguide/working-with-security-groups.html) with outbound traffic on port 443 to isolate your runners from the rest of your AWS account.

You are now ready to start using this action with AWS!

## Useful Resources
- [AWS - Creating IAM Policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_create.html)
- [AWS - Creating an IAM User in your AWS account](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html)
