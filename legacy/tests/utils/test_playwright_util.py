from legacy.src.utils.playwright_util import launch_browser, close_browser


def test_browser_launch():
    # Launch browser and verify page opens
    playwright, browser, context, page = launch_browser()
    assert page is not None
    assert browser.is_connected()
    close_browser(playwright, browser)