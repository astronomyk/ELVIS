import pytest
import os

def pytest_addoption(parser):
    parser.addoption(
        "-P", "--no-plots", action="store_true", default=False,
        help="Suppress matplotlib plots by setting CI=true"
    )

@pytest.fixture(autouse=True, scope="session")
def suppress_plots(request):
    if request.config.getoption("--no-plots"):
        os.environ["CI"] = "true"
