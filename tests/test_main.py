import pytest
import os
from gha_runner.__main__ import (
    parse_aws_params,
    _env_parse_helper,
)


def test_env_parse_helper():
    base: dict[str, str] = {}
    assert _env_parse_helper(base, "TEST_ENV_VAR_GHA_RUNNER", "test") == {}
    os.environ["TEST_ENV_VAR_GHA_RUNNER"] = "test"
    assert _env_parse_helper(base, "TEST_ENV_VAR_GHA_RUNNER", "test") == {
        "test": "test"
    }


@pytest.mark.parametrize(
    "env_vars, expected_output",
    [
        ({}, [{}]),
        (
            {"INPUT_AWS_IMAGE_ID": "ami-1234567890"},
            [{"image_id": "ami-1234567890"}],
        ),
        (
            {"INPUT_AWS_INSTANCE_TYPE": "t2.micro"},
            [{"instance_type": "t2.micro"}],
        ),
        (
            {"INPUT_AWS_SUBNET_ID": "subnet-1234567890"},
            [{"subnet_id": "subnet-1234567890"}],
        ),
        (
            {"INPUT_AWS_SECURITY_GROUP_ID": "sg-1234567890"},
            [{"security_group_id": "sg-1234567890"}],
        ),
        (
            {"INPUT_AWS_IAM_ROLE": "role-1234567890"},
            [{"iam_role": "role-1234567890"}],
        ),
        (
            {"INPUT_AWS_TAGS": '[{"Key": "Name", "Value": "test"}]'},
            [{"tags": [{"Key": "Name", "Value": "test"}]}],
        ),
        (
            {"INPUT_AWS_REGION_NAME": "us-east-1"},
            [{"region_name": "us-east-1"}],
        ),
        (
            {"INPUT_AWS_HOME_DIR": "/home/ec2-user"},
            [{"home_dir": "/home/ec2-user"}],
        ),
        ({"INPUT_EXTRA_GH_LABELS": "test"}, [{"labels": "test"}]),
        (
            {"INPUT_AWS_IMAGE_ID": "ami-1234567890"},
            [{"image_id": "ami-1234567890"}],
        ),
        (
            {
                "INPUT_AWS_IMAGE_ID": "ami-1234567890",
                "INPUT_AWS_INSTANCE_TYPE": "t2.micro",
            },
            [
                {"image_id": "ami-1234567890"},
                {"image_id": "ami-1234567890", "instance_type": "t2.micro"},
            ],
        ),
    ],
)
def test_parse_aws_params(env_vars, expected_output):
    idx = 0
    for key, value in env_vars.items():
        if key == "INPUT_AWS_TAGS":
            os.environ[key] = value
        else:
            os.environ[key] = str(value)
        assert parse_aws_params() == expected_output[idx]
        idx += 1
    for key in env_vars.keys():
        del os.environ[key]


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
