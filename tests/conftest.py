import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-live", action="store_true", default=False,
        help="Run tests marked @pytest.mark.live (real claude/network calls).",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "live: test makes real claude/network calls (opt-in via --run-live)"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-live"):
        return
    skip_live = pytest.mark.skip(reason="needs --run-live")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
