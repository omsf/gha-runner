# gha-runner
A simple GitHub Action for creating self-hosted runners. Currently, this only supports AWS.

## Getting Started
To get started you will need a couple of config items from both AWS and GitHub.

First create a `config.toml` in the root of the project with the following:
```toml
[github]
repo = "<name of your repo>"

[aws]
image_id = "<name of your custom AMI>"
instance_type = "<image type>"
subnet_id = "<subnet ID>"
security_group_id = "<security group ID>"
iam_role = "<the optional IAM role to use>"
tags = []
region_name = "<the AWS region (ie us-east-1)>"
home_dir = "<the ec2 instance home directory, for Amazon Linux 2023/Amazon Linux 2 this is /home/ec2-user>"
labels = "<a comma seperated list of labels (ie testing,other,label)>"
```

Create a `.env` in the root of the project with the following environment variables:
```sh
AWS_ACCESS_KEY_ID="<Your AWS Access Key ID>"
AWS_SECRET_ACCESS_KEY="<YOU AWS Secret Access Key>"
GH_PAT="<A GitHub Personal Access Token>"
```

For a breakdown on how to get these items please use the following [https://github.com/machulav/ec2-github-runner?tab=readme-ov-file#how-to-start](https://github.com/machulav/ec2-github-runner?tab=readme-ov-file#how-to-start).


### Running the Project
```sh
docker build -t gha_runner .
docker run --rm --env-file .env gha_runner
```
This will do the following:
1. Request a GitHub Action Self-Hosted Runner Token from GitHub
2. Generate a user-data script to provision an EC2 instance with
3. Provision an EC2 instance
4. Add the runner to the repo
5. Remove the runner from the repo
6. Terminate the EC2 instance

