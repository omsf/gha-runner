from github import Github, Auth
import requests


class GitHubInstance:
    BASE_URL = "https://api.github.com"

    # repo is the full name of the repository, e.g. "owner/repo"
    def __init__(self, token: str, repo: str):
        self.token = token
        self.headers = self._headers({})
        auth = Auth.Token(token)
        self.github = Github(auth=auth)
        self.repo = repo

    def _headers(self, header_kwargs):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-Github-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
        }
        headers.update(header_kwargs)
        return headers

    def _do_request(self, func, endpoint, **kwargs):
        endpoint_url = f"{self.BASE_URL}/{endpoint}"
        headers = self.headers
        resp: requests.Response = func(endpoint_url, headers=headers, **kwargs)
        if not resp.ok:
            raise RuntimeError(
                f"Error in API call for {endpoint_url}: " f"{resp.content}"
            )
        else:
            return resp.json()

    def create_runner_token(self) -> str:
        try:
            res = self.post(f"repos/{self.repo}/actions/runners/registration-token")
            return res["token"]
        except Exception as e:
            raise Exception(f"Error creating runner token: {e}")

    def post(self, endpoint, **kwargs):
        return self._do_request(requests.post, endpoint, **kwargs)

    def get_runner(self, label: str):
        runners = self.github.get_repo(self.repo).get_self_hosted_runners()
        matchedRunners = [
            runner
            for runner in runners
            if label in [l["name"] for l in runner.labels()]
        ]
        return matchedRunners[0] if matchedRunners else None

    def remove_runner(self, label: str):
        runner = self.get_runner(label)
        if runner is not None:
            removed = self.github.get_repo(self.repo).remove_self_hosted_runner(runner)
            if not removed:
                raise RuntimeError(f"Error removing runner {label}")
        else:
            raise RuntimeError(f"Runner {label} not found")

    def get_latest_runner_release(self, platform: str, architecture: str) -> str:
        """Returns the latest runner for the given platform and architecture."""
        repo = "actions/runner"
        release = self.github.get_repo(repo).get_latest_release()
        assets = release.get_assets()
        for asset in assets:
            if platform in asset.name and architecture in asset.name:
                return asset.browser_download_url
        raise RuntimeError(f"Runner not found for {platform} and {architecture}")
