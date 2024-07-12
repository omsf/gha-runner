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
            # "tags": {},
            "region_name": "us-east-1",
            # "gh_runner_token": "testing",
            "gh_runner_tokens": ["testing"],
            "home_dir": "/home/ec2-user",
            "runner_release": "testing",
            "repo": "omsf-eco-infra/awsinfratesting",
        }
        yield AWS(**params)


def test_build_aws_params():
    params = {
        "image_id": "ami-0772db4c976d21e9b",
        "instance_type": "t2.micro",
        "tags": [
            {"Key": "Name", "Value": "test"},
            {"Key": "Owner", "Value": "test"},
        ],
        "region_name": "us-east-1",
        "gh_runner_tokens": ["testing"],
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
    params = aws._build_aws_params(user_data_params)
    assert params == {
        "ImageId": "ami-0772db4c976d21e9b",
        "InstanceType": "t2.micro",
        "MinCount": 1,
        "MaxCount": 1,
        "SubnetId": "test",
        "SecurityGroupIds": ["test"],
        "IamInstanceProfile": {"Name": "test"},
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
        "TagSpecifications": [
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "test"},
                    {"Key": "Owner", "Value": "test"},
                ],
            }
        ],
    }


def test_create_instance_with_labels(aws):
    aws.labels = "test"
    ids = aws.create_instances()
    assert len(ids) == 1


def test_create_instances(aws):
    ids = aws.create_instances()
    assert len(ids) == 1


def test_create_instances_missing_release(aws):
    aws.runner_release = ""
    with pytest.raises(
        ValueError, match="No runner release provided, cannot create instances."
    ):
        aws.create_instances()


def test_create_instances_missing_home_dir(aws):
    aws.home_dir = ""
    with pytest.raises(
        ValueError, match="No home directory provided, cannot create instances."
    ):
        aws.create_instances()


def test_create_instances_missing_tokens(aws):
    aws.gh_runner_tokens = []
    with pytest.raises(
        ValueError,
        match="No GitHub runner tokens provided, cannot create instances.",
    ):
        aws.create_instances()


def test_create_instances_missing_image_id(aws):
    aws.image_id = ""
    with pytest.raises(
        ValueError, match="No image ID provided, cannot create instances."
    ):
        aws.create_instances()


def test_create_instances_missing_instance_type(aws):
    aws.instance_type = ""
    with pytest.raises(
        ValueError, match="No instance type provided, cannot create instances."
    ):
        aws.create_instances()


def test_instance_running(aws):
    ids = aws.create_instances()
    assert len(ids) == 1
    ids = list(ids)
    assert aws.instance_running(ids[0])


def test_instance_running_dne(aws):
    # This is a fake instance id
    ids = ["i-xxxxxxxxxxxxxxxxx"]
    with pytest.raises(Exception):
        aws.instance_running(ids[0])


def test_instance_running_terminated(aws):
    ids = aws.create_instances()
    assert len(ids) == 1
    ids = list(ids)
    aws.remove_instances(ids)
    assert not aws.instance_running(ids[0])


def test_wait_until_ready(aws):
    ids = aws.create_instances()
    params = {
        "MaxAttempts": 1,
        "Delay": 5,
    }
    ids = list(ids)
    aws.wait_until_ready(ids, **params)
    assert aws.instance_running(ids[0])


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
    ids = aws.create_instances()
    assert len(ids) == 1
    ids = list(ids)
    aws.remove_instances(ids)
    assert not aws.instance_running(ids[0])


def test_wait_until_removed(aws):
    ids = aws.create_instances()
    assert len(ids) == 1
    ids = list(ids)
    aws.remove_instances(ids)
    params = {
        "MaxAttempts": 1,
        "Delay": 5,
    }
    aws.wait_until_removed(ids, **params)
    assert not aws.instance_running(ids[0])


def test_wait_until_removed_dne(aws):
    # This is a fake instance id
    ids = ["i-xxxxxxxxxxxxxxxxx"]
    params = {
        "MaxAttempts": 1,
        "Delay": 5,
    }
    with pytest.raises(WaiterError):
        aws.wait_until_removed(ids, **params)


@pytest.mark.slow
def test_wait_until_removed_dne_long(aws):
    # This is a fake instance id
    ids = ["i-xxxxxxxxxxxxxxxxx"]
    with pytest.raises(WaiterError):
        aws.wait_until_removed(ids)


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
    user_data = aws._build_user_data(**params).strip()
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
        aws._build_user_data(**params)
