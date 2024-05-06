from botocore.exceptions import WaiterError
import pytest
from moto import mock_aws
import os
from gha_runner.clouddeployment import AWS


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope="function")
def aws(aws_credentials):
    with mock_aws():
        params = {
            "image_id": "ami-0772db4c976d21e9b",
            "instance_type": "t2.micro",
            "tags": [],
            "region_name": "us-east-1",
            "gh_runner_token": "testing",
            "home_dir": "/home/ec2-user",
            "runner_release": "",
            "repo": "omsf-eco-infra/awsinfratesting",
        }
        yield AWS(**params)


def test_build_aws_params():
    params = {
        "image_id": "ami-0772db4c976d21e9b",
        "instance_type": "t2.micro",
        "tags": [],
        "region_name": "us-east-1",
        "gh_runner_token": "testing",
        "home_dir": "/home/ec2-user",
        "runner_release": "",
        "repo": "omsf-eco-infra/awsinfratesting",
        "subnet_id": "test",
        "security_group_id": "test",
        "iam_role": "test",
    }
    user_data_params = {
        "token": "test",
        "repo": "omsf-eco-infra/awsinfratesting",
        "homedir": "/home/ec2-user",
        "script": "echo 'Hello, World!'",
        "runner_release": "test.tar.gz",
        "labels": "label",
    }
    aws = AWS(**params)
    params = aws.build_aws_params(1, user_data_params)
    assert params == {
        "ImageId": "ami-0772db4c976d21e9b",
        "InstanceType": "t2.micro",
        "MinCount": 1,
        "MaxCount": 1,
        "SubnetId": "test",
        "SecurityGroupIds": ["test"],
        "IamInstanceProfile": {"Name": "test"},
        "TagSpecifications": [],
        "UserData": """#!/bin/bash
cd "/home/ec2-user"
echo "echo 'Hello, World!'" > pre-runner-script.sh
source pre-runner-script.sh
export RUNNER_ALLOW_RUNASROOT=1
# We will get the latest release from the GitHub API
curl -L test.tar.gz -o runner.tar.gz
tar xzf runner.tar.gz
./config.sh --url https://github.com/omsf-eco-infra/awsinfratesting --token test --labels label --ephemeral
./run.sh
""",
    }


def test_create_instance(aws):
    ids = aws.create_instance(count=1)
    assert len(ids) == 1


def test_wait_until_ready(aws):
    ids = aws.create_instance(count=1)
    params = {
        "MaxAttempts": 1,
        "Delay": 5,
    }
    aws.wait_until_ready(ids, **params)


def test_wait_until_ready_dne(aws):
    # This is a fake instance id
    ids = ["i-xxxxxxxxxxxxxxxxx"]
    params = {
        "MaxAttempts": 1,
        "Delay": 5,
    }
    with pytest.raises(WaiterError):
        aws.wait_until_ready(ids, **params)


@pytest.mark.slow
def test_wait_until_ready_dne_long(aws):
    # This is a fake instance id
    ids = ["i-xxxxxxxxxxxxxxxxx"]
    with pytest.raises(WaiterError):
        aws.wait_until_ready(ids)


def test_remove_instances(aws):
    ids = aws.create_instance(count=1)
    assert len(ids) == 1
    aws.remove_instances(ids)


def test_wait_until_removed(aws):
    ids = aws.create_instance(count=1)
    assert len(ids) == 1
    aws.remove_instances(ids)
    params = {
        "MaxAttempts": 1,
        "Delay": 5,
    }
    aws.wait_until_removed(ids, **params)


def test_wait_until_removed_dne(aws):
    # This is a fake instance id
    ids = ["i-xxxxxxxxxxxxxxxxx"]
    params = {
        "MaxAttempts": 1,
        "Delay": 5,
    }
    with pytest.raises(WaiterError):
        aws.wait_until_removed(ids, **params)


def test_build_user_data(aws):
    params = {
        "homedir": "/home/ec2-user",
        "script": "echo 'Hello, World!'",
        "repo": "omsf-eco-infra/awsinfratesting",
        "token": "test",
        "labels": "label",
        "runner_release": "test.tar.gz",
    }
    # We strip this to ensure that we don't have any extra whitespace to fail our test
    user_data = aws._AWS__build_user_data(**params).strip()
    # We also strip here
    file = """#!/bin/bash
cd "/home/ec2-user"
echo "echo 'Hello, World!'" > pre-runner-script.sh
source pre-runner-script.sh
export RUNNER_ALLOW_RUNASROOT=1
# We will get the latest release from the GitHub API
curl -L test.tar.gz -o runner.tar.gz
tar xzf runner.tar.gz
./config.sh --url https://github.com/omsf-eco-infra/awsinfratesting --token test --labels label --ephemeral
./run.sh
    """.strip()
    assert user_data == file


def test_build_user_data_missing_params(aws):
    params = {
        "homedir": "/home/ec2-user",
        "script": "echo 'Hello, World!'",
        "repo": "omsf-eco-infra/awsinfratesting",
        "token": "test",
    }
    with pytest.raises(Exception):
        aws._AWS__build_user_data(**params)
