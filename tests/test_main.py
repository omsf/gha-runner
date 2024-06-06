import pytest
import os
from gha_runner.__main__ import (
    parse_aws_params,
    env_parse_helper,
)


def test_env_parse_helper():
    base: dict[str, str] = {}
    assert env_parse_helper(base, "TEST_ENV_VAR_GHA_RUNNER", "test") == base
    os.environ["TEST_ENV_VAR_GHA_RUNNER"] = "test"
    assert env_parse_helper(base, "TEST_ENV_VAR_GHA_RUNNER", "test") == {"test": "test"}


def test_parse_aws_params():
    base = parse_aws_params()
    assert len(base) == 0
    assert base == {}
    os.environ["INPUT_AWS_IMAGE_ID"] = "ami-1234567890"
    assert parse_aws_params() == {"image_id": "ami-1234567890"}
    os.environ["INPUT_AWS_INSTANCE_TYPE"] = "t2.micro"
    assert parse_aws_params() == {
        "image_id": "ami-1234567890",
        "instance_type": "t2.micro",
    }
    os.environ["INPUT_AWS_SUBNET_ID"] = "subnet-1234567890"
    assert parse_aws_params() == {
        "image_id": "ami-1234567890",
        "instance_type": "t2.micro",
        "subnet_id": "subnet-1234567890",
    }
    os.environ["INPUT_AWS_SECURITY_GROUP_ID"] = "sg-1234567890"
    assert parse_aws_params() == {
        "image_id": "ami-1234567890",
        "instance_type": "t2.micro",
        "subnet_id": "subnet-1234567890",
        "security_group_id": "sg-1234567890",
    }
    os.environ["INPUT_AWS_IAM_ROLE"] = "role-1234567890"
    assert parse_aws_params() == {
        "image_id": "ami-1234567890",
        "instance_type": "t2.micro",
        "subnet_id": "subnet-1234567890",
        "security_group_id": "sg-1234567890",
        "iam_role": "role-1234567890",
    }
    os.environ["INPUT_AWS_TAGS"] = '[{"Key": "Name", "Value": "test"}]'
    assert parse_aws_params() == {
        "image_id": "ami-1234567890",
        "instance_type": "t2.micro",
        "subnet_id": "subnet-1234567890",
        "security_group_id": "sg-1234567890",
        "iam_role": "role-1234567890",
        "tags": [{"Key": "Name", "Value": "test"}],
    }
    os.environ["INPUT_AWS_REGION_NAME"] = "us-east-1"
    assert parse_aws_params() == {
        "image_id": "ami-1234567890",
        "instance_type": "t2.micro",
        "subnet_id": "subnet-1234567890",
        "security_group_id": "sg-1234567890",
        "iam_role": "role-1234567890",
        "tags": [{"Key": "Name", "Value": "test"}],
        "region_name": "us-east-1",
    }
    os.environ["INPUT_AWS_HOME_DIR"] = "/home/ec2-user"
    assert parse_aws_params() == {
        "image_id": "ami-1234567890",
        "instance_type": "t2.micro",
        "subnet_id": "subnet-1234567890",
        "security_group_id": "sg-1234567890",
        "iam_role": "role-1234567890",
        "tags": [{"Key": "Name", "Value": "test"}],
        "region_name": "us-east-1",
        "home_dir": "/home/ec2-user",
    }
    os.environ["INPUT_AWS_LABELS"] = "test"
    assert parse_aws_params() == {
        "image_id": "ami-1234567890",
        "instance_type": "t2.micro",
        "subnet_id": "subnet-1234567890",
        "security_group_id": "sg-1234567890",
        "iam_role": "role-1234567890",
        "tags": [{"Key": "Name", "Value": "test"}],
        "region_name": "us-east-1",
        "home_dir": "/home/ec2-user",
        "labels": "test",
    }


def test_parse_aws_params_empty():
    os.environ["INPUT_AWS_IMAGE_ID"] = ""
    os.environ["INPUT_AWS_INSTANCE_TYPE"] = ""
    os.environ["INPUT_AWS_SUBNET_ID"] = ""
    os.environ["INPUT_AWS_SECURITY_GROUP_ID"] = ""
    os.environ["INPUT_AWS_IAM_ROLE"] = ""
    os.environ["INPUT_AWS_TAGS"] = ""
    os.environ["INPUT_AWS_REGION_NAME"] = ""
    os.environ["INPUT_AWS_HOME_DIR"] = ""
    os.environ["INPUT_AWS_LABELS"] = ""
    assert parse_aws_params() == {
        "image_id": "",
        "instance_type": "",
        "home_dir": "",
        "region_name": "",
    }
