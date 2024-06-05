import pytest
from gha_runner.clouddeployment import CloudDeploymentFactory, AWS


def test_get_provider():
    factory = CloudDeploymentFactory()
    with pytest.raises(ValueError, match="Invalid provider"):
        factory.get_provider("invalid_provider")
    with pytest.raises(TypeError, match="Invalid configuration"):
        factory.get_provider("aws", invalid_arg="invalid_arg")
    params = {
        "image_id": "ami-0772db4c976d21e9b",
        "instance_type": "t2.micro",
        "tags": [],
        "region_name": "us-east-1",
        "gh_runner_tokens": ["testing"],
        "home_dir": "/home/ec2-user",
        "runner_release": "",
        "repo": "omsf-eco-infra/awsinfratesting",
    }
    cloud = CloudDeploymentFactory().get_provider("aws", **params)
    assert isinstance(cloud, AWS)
