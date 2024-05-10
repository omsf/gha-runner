import pytest
from unittest.mock import patch, MagicMock, Mock


@pytest.fixture
def github_release_mock():
    # Create MagicMocks for components not directly patched
    mock_release = MagicMock()
    mock_asset = MagicMock()
    mock_runners = MagicMock()
    runner = MagicMock()

    # Setup fixed attributes for mocks
    asset_name = "runner-linux-x64.tar.gz"
    asset_url = "https://github.com/testing/runner-linux-x64.tar.gz"
    mock_asset.name = asset_name
    mock_asset.browser_download_url = asset_url
    runner.labels.return_value = [{"name": "runner-linux-x64"}]
    mock_runners.__iter__.return_value = [runner]

    # Using patch as a context manager inside the fixture
    with patch("gha_runner.gh.Github") as mock_github:
        mock_repo = MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo
        mock_repo.get_latest_release.return_value = mock_release
        mock_repo.get_self_hosted_runners.return_value = mock_runners
        mock_release.get_assets.return_value = [mock_asset]
        mock_repo.remove_self_hosted_runner.return_value = True

        from gha_runner.gh import GitHubInstance

        instance = GitHubInstance("test", "testing/testing")

        yield instance, mock_asset, mock_repo


@pytest.mark.parametrize(
    "platform, architecture, expected, raises, match_msg",
    [
        # Test case where the latest release exists
        (
            "linux",
            "x64",
            "https://github.com/testing/runner-linux-x64.tar.gz",
            None,
            None,
        ),
        # Test case where the latest release does not exist
        ("darwin", "x64", None, RuntimeError, "Runner not found for darwin and x64"),
    ],
)
def test_get_latest_runner_release(
    github_release_mock, platform, architecture, expected, raises, match_msg
):
    instance, _, _ = github_release_mock
    if raises:
        with pytest.raises(raises, match=match_msg):
            instance.get_latest_runner_release(platform, architecture)
    else:
        result = instance.get_latest_runner_release(platform, architecture)
        assert result == expected, f"Expected URL {expected} but got {result}"


@pytest.mark.parametrize(
    "label, expected",
    [
        # TODO: Mock the expected object and test the get_runner method
        # Test case where the runner exists
        ("runner-linux-x64", True),
        # Test case where the runner does not exist
        ("runner-darwin-x64", None),
    ],
)
def test_get_runner(github_release_mock, label, expected):
    instance, _, _ = github_release_mock
    result = instance.get_runner(label)
    if expected is not None:
        assert result is not None
    else:
        assert result is None


def test_remove_runner_exists(github_release_mock):
    instance, _, mock_repo = github_release_mock
    instance.remove_runner("runner-linux-x64")
    mock_repo.remove_self_hosted_runner.assert_called_once()


def test_remove_runner_dne(github_release_mock):
    instance, _, mock_repo = github_release_mock
    mock_repo.remove_self_hosted_runner.return_value = False
    with pytest.raises(RuntimeError, match="Error removing runner runner-linux-x64"):
        instance.remove_runner("runner-linux-x64")


def test_remove_runner_not_found(github_release_mock):
    instance, _, _ = github_release_mock
    with pytest.raises(RuntimeError, match="Runner non-existent-runner not found"):
        instance.remove_runner("non-existent-runner")


def test_headers(github_release_mock):
    """Tests that headers get set correctly."""
    instance, _, _ = github_release_mock
    headers = {
        "Authorization": f"Bearer {instance.token}",
        "X-Github-Api-Version": "2022-11-28",
        "Accept": "application/vnd.github+json",
    }
    assert instance.headers == headers


def test_do_request(github_release_mock):
    import requests

    """Tests that the request is made correctly."""
    instance, _, _ = github_release_mock
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "token": "LLBF3JGZDX3P5PMEXLND6TS6FCWO6",
        "expires_at": "2020-01-22T12:13:35.123-08:00",
    }
    with patch("requests.get", return_value=mock_response) as mock_func:
        response = instance._do_request(mock_func, "https://api.github.com")
        assert response == mock_response.json.return_value


def test_do_request_fail(github_release_mock):
    import requests

    """Tests that the request is made correctly."""
    instance, _, _ = github_release_mock
    endpoint = "/mock/test"
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.ok = False
    mock_response.content = "Not Found"
    error = f"Error in API call for https://api.github.com{endpoint}: {mock_response.content}"
    with patch("requests.get", return_value=mock_response) as mock_func:
        with pytest.raises(RuntimeError, match=error):
            instance._do_request(mock_func, endpoint)


@pytest.fixture
def post_fixture(github_release_mock):
    import requests

    instance, _, _ = github_release_mock
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "token": "LLBF3JGZDX3P5PMEXLND6TS6FCWO6",
        "expires_at": "2020-01-22T12:13:35.123-08:00",
    }
    with patch("requests.post", return_value=mock_response):
        yield instance, mock_response


def test_post(post_fixture):
    instance, mock_response = post_fixture
    response = instance.post("https://api.github.com", data={"key": "value"})
    assert response == mock_response.json.return_value
    mock_response.json.assert_called_once()


def test_create_runner_token(post_fixture):
    instance, mock_response = post_fixture
    response = instance.create_runner_token()
    assert response == mock_response.json.return_value["token"]
    mock_response.json.assert_called_once()


def test_create_runner_token_fail(post_fixture):
    from gha_runner.gh import TokenRetrievalError

    instance, mock_response = post_fixture
    mock_response.status_code = 404
    mock_response.ok = False
    mock_response.content = "Not Found"
    error = f"Error creating runner token: Error in API call for https://api.github.com/repos/testing/testing/actions/runners/registration-token: {mock_response.content}"
    with pytest.raises(TokenRetrievalError, match=error):
        instance.create_runner_token()


def test_generate_random_label(github_release_mock):
    instance, _, _ = github_release_mock
    with patch("random.choice", return_value="a"):
        label = instance.generate_random_label()
        assert label == f"runner-{'a'*8}"
