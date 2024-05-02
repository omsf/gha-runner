from gha_runner.clouddeployment import CloudDeploymentFactory
from gha_runner.gh import GitHubInstance
import sys
import os

# https://github.com/hukkin/tomli?tab=readme-ov-file#building-a-tomlitomllib-compatibility-layer
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def main():
    """
    Main entrypoint for the application. As of right now, this is just a test.
    Requires the following environment variables:
        - GH_PAT: GitHub Personal Access Token
        - AWS_ACCESS_KEY_ID: AWS Access Key ID
        - AWS_SECRET_ACCESS_KEY: AWS Secret Access Key
    You will also need a config.toml file in the root directory of the project.
    """
    # Check for required environment variables
    required = ["GH_PAT", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    for req in required:
        if req not in os.environ:
            raise Exception(f"Missing required environment variable {req}")
    config = None
    gha_params = {
        "token": os.environ["GH_PAT"],
    }
    cloud_params = {}

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
        gha_params.update(config["github"])
        cloud_params = config["aws"]
        cloud_params["repo"] = gha_params["repo"]

    repo = "omsf-eco-infra/awsinfratesting"
    print("Starting up...")
    gha_params = {
        "token": os.environ["GH_PAT"],
        "repo": repo,
    }
    # Create a GitHub instance
    gh = GitHubInstance(**gha_params)
    print("Creating GitHub Actions Runner")
    # We need to create a runner token first
    runner_token = gh.create_runner_token()
    cloud_params["gh_runner_token"] = runner_token
    # We will also get the latest runner release
    release = gh.get_latest_runner_release(platform="linux", architecture="x64")
    cloud_params["runner_release"] = release
    cloud = CloudDeploymentFactory().get_provider("aws", **cloud_params)
    ids = cloud.create_instance(count=1)
    print(ids)
    print("Waiting for instance to be ready...")
    cloud.wait_until_ready(ids)
    print("Instance is ready!")
    gh.wait_for_runner("testing")
    # -----------
    gh.remove_runner("testing")
    print("Runner removed!")
    cloud.remove_instances(ids)
    print("Waiting for instance to be removed...")
    cloud.wait_until_removed(ids)
    print("Instance removed!")


if __name__ == "__main__":
    main()
