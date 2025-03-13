from playwright.sync_api import sync_playwright


def launch_browser(headless: bool = True):
    """
    Launch and return a Playwright browser instance (Chromium).

    Args:
        headless (bool): Whether to run the browser in headless mode.

    Returns:
        browser, context, page
    """
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()

    return playwright, browser, context, page


def close_browser(playwright, browser):
    """
    Gracefully closes the browser.
    """
    browser.close()
    playwright.stop()
