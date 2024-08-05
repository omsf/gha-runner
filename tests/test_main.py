import pytest
import os
from gha_runner.__main__ import (
    parse_aws_params,
    _env_parse_helper,
    start_runner_instances,
    stop_runner_instances,
)
from unittest.mock import Mock, patch, mock_open

pytestmark = pytest.mark.main


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


# Define a mock CloudProvider class (e.g., MockAWS)
class MockCloudProvider:
    def __init__(self, **kwargs):
        pass

    def create_instances(self):
        return mock_get_instance_mapping()

    def wait_until_ready(self, instance_ids):
        pass

    def remove_instances(self, instance_ids):
        pass

    def wait_until_removed(self, instance_ids):
        pass


class FailedCloudProvider:
    def __init__(self, **kwargs):
        pass

    def create_instances(self):
        pass

    def wait_until_ready(self, instance_ids):
        pass

    def remove_instances(self, instance_ids):
        pass

    def wait_until_removed(self, instance_ids):
        raise Exception("Test")


def mock_get_instance_mapping():
    return {"instance_id_1": "label_1"}


@pytest.fixture
def mock_cloud_deployment_factory():
    with patch.dict(
        "gha_runner.clouddeployment.CloudDeploymentFactory.providers",
        {
            "mock_provider": MockCloudProvider,
            "failed_provider": FailedCloudProvider,
        },
    ):
        yield


@pytest.fixture
def mock_gh_output():
    with patch.dict("os.environ", {"GITHUB_OUTPUT": "mock_output"}):
        with patch("builtins.open", mock_open()):
            yield


@pytest.fixture
def mock_gh():
    gh_mock = Mock()
    gh_mock.get_latest_runner_release.return_value = "mock_release"
    gh_mock.create_runner_tokens.return_value = ["mock_token"]
    gh_mock.remove_runner.return_value = None

    return gh_mock


def test_start_runner_instances_smoke(
    mock_cloud_deployment_factory, mock_gh_output, mock_gh
):
    try:
        start_runner_instances(
            provider="mock_provider",
            gh=mock_gh,
            count=1,
            cloud_params={},
            timeout=0,
        )
    except Exception as e:
        pytest.fail(f"Exception raised: {e}")


def test_stop_runner_instances_smoke(
    mock_cloud_deployment_factory, mock_gh_output, mock_gh
):
    with patch(
        "gha_runner.__main__.get_instance_mapping",
        new=mock_get_instance_mapping,
    ):
        try:
            stop_runner_instances(
                provider="mock_provider", cloud_params={}, gh=mock_gh
            )
        except Exception as e:
            pytest.fail(f"stop_runner_instances raised an exception: {e}")


def test_stop_runner_instances_failure(
    mock_cloud_deployment_factory, mock_gh_output, mock_gh, capsys
):
    with patch(
        "gha_runner.__main__.get_instance_mapping",
        side_effect=Exception("Test"),
    ):
        with pytest.raises(SystemExit) as fail:
            stop_runner_instances(
                provider="mock_provider", cloud_params={}, gh=mock_gh
            )
            assert fail.type == SystemExit
            assert fail.value.code == 1

            captured = capsys.readouterr()
            assert (
                captured.out == "::error title=Malformed instance mapping::Test"
            )


def test_stop_runner_instances_aws(
    mock_cloud_deployment_factory, mock_gh_output, mock_gh, capsys
):
    with patch(
        "gha_runner.__main__.get_instance_mapping",
        new=mock_get_instance_mapping,
    ):
        with pytest.raises(SystemExit) as fail:
            stop_runner_instances(
                provider="failed_provider", cloud_params={}, gh=mock_gh
            )
            assert fail.type == SystemExit
            assert fail.value.code == 1
