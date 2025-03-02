import pytest
import os
from datetime import datetime
from playwright.sync_api import sync_playwright


# Fetch config values from pytest.ini
def pytest_addoption(parser):
    parser.addini("--browser", default="chromium", help="Browser: chromium, firefox, webkit")
    parser.addini("--headed", default="True", help="Run in headed mode (True/False)")
    parser.addini("--slowmo", default="1000", help="Slow down execution (in ms)")
    parser.addini("--screenshot", default="on", help="Capture screenshots (on/off)")
    parser.addini("--video", default="on", help="Record video (on/off)")


# Read values from pytest config
@pytest.fixture(scope="session")
def get_browser_configurations(request):
    return {
        "browser": request.config.getini("--browser"),
        "headed": request.config.getini("--headed").lower() == "true",
        "slowmo": int(request.config.getini("--slowmo")),
        "screenshot": request.config.getini("--screenshot"),
        "video": request.config.getini("--video")
    }


# Create Playwright browser fixture
@pytest.fixture(scope="session")
def browser(get_browser_configurations):
    with sync_playwright() as spw:
        browser_type = getattr(spw, get_browser_configurations["browser"])
        browser = browser_type.launch(
            headless=not get_browser_configurations["headed"], 
            slow_mo=get_browser_configurations["slowmo"]
        )
        yield browser
        browser.close()


# Create Playwright page fixture
@pytest.fixture(scope="function")
def page(browser, get_browser_configurations, request):
    test_name = request.node.name
    test_time_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    test_screenshot_path = f"test_report/screenshots/{test_name}_{test_time_stamp}.png"

    context = browser.new_context(
        viewport=None,
        record_video_dir="test_report/videos" if get_browser_configurations["video"] == "on" else None
    )

    page = context.new_page()
    yield page

    # Capture screenshot on failure
    if request.node.rep_call.failed and get_browser_configurations["screenshot"] == "on":
        os.makedirs(os.path.dirname(test_screenshot_path), exist_ok=True)
        page.screenshot(path=test_screenshot_path)

    page.close()


# Capture test results for reporting
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
