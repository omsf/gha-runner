# AWS Setup Instructions
The goal of this document is to provide a guide on how to setup the GitHub Action runner on AWS. This document will guide you through the account setup required to use this action with AWS.

## Prerequisites
- An AWS account

## Setup
1. Prepare an IAM uyser with AWS access keys
  a. Go to the AWS Management Console and sign in to your account.
  b. Go to the IAM console.
  c. In the navigation pane, choose Policies.
  d. Create a new policy by clicking "Create Policy".
  e. Next, click JSON and paste the following JSON with the required permissions and then click "Next".
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
  f. Name the policy (for example: `gha-runner-policy`) and select "Create Policy".
  g. Now select "Users" in the navigation pane and click "Add user".
  h. Enter a username (for example: `gha-runner-user`) and ensure that "Provide user access to the AWS Management Console" is unchecked.
  i. Select "Attach policies directly" and search for the policy you created earlier (`gha-runner-policy`) and select it.
  j. Then click, "Create user".
  k. Next, click on the user you just created and go to the "Security credentials" tab.
  l. Click "Create access key" and then click "Other" and then "Next".
  m. Click next and then copy the Access Key and Secret Access Key (or download the CSV file), these will not be shown again.
2. Create your GitHub Access Token
  a. This can be done with either a Personal Access Token or a Fine-Grained Personal Access Token.
  b. Go to your GitHub account settings.
  c. Click on "Developer settings".
  d. Create a new token with `repo` scope.
  e. Save and/or copy the token.
3. Add your credentials to your repository secrets
  a. Go to your repository on GitHub.
  b. Click on "Settings", then "Secrets and Variables", and then "Actions.
  c. Click "New repository secret".
  d. Add the following secrets:
    - `AWS_ACCESS_KEY_ID` - The Access Key you copied earlier.
    - `AWS_SECRET_ACCESS_KEY` - The Secret Access Key you copied earlier.
    - `GITHUB_TOKEN` - The GitHub token you copied earlier.
4. Prepare an EC2 image
  a. Go to the AWS Management Console and sign in to your account.
  b. Go to the EC2 console.
  c. Click "Launch Instance".
  d. Select an Amazon Linux 2 AMI.
  e. Choose an instance type.
  f. Configure the instance details.
  g. Connect to the instance and install `docker`, `git`, and enable the `docker` service. This will be distro dependent.
  i. Feel free to install any other useful tools that you may need to get started.
  j. Create an image of the instance using the following [AWS Docs](https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/tkv-create-ami-from-instance.html) (this may take awhile)
  k. Make sure to remove the instance once you are done creating the image.
5. Optional: Create a VPC with subnet and security group.
  a. Go to the AWS Management Console and sign in to your account.
  b. Go to the VPC console.
  c. Create a VPC.
  d. Create a subnet.
  e. Create a security group. The security group should only require outbound traffic on port 443 to pull jobs from GitHub, no inbound traffic is required.
  f. Attach the security group to the subnet.

You are now ready to start using this action with AWS!

## Useful Resources
- [AWS - Creating IAM Policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_create.html)
- [AWS - Creating an IAM User in your AWS account](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html)
