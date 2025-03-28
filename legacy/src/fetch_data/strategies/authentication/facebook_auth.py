from legacy.src.fetch_data.strategies.authentication.base_auth import BaseAuth
from legacy.src.utils.config_util import ConfigUtil
from legacy.src.utils.logging_util import setup_logger, log_exception
from playwright.sync_api import Page, Error as PlaywrightError


class FacebookAuthentication(BaseAuth):
    def __init__(self, config=None):
        super().__init__(config)
        self.logger = setup_logger(f"{self.__class__.__name__}")
        self.config = config or {}

    def authenticate(self, page: Page):
        username = ConfigUtil().get_from_env("facebook.username")
        password = ConfigUtil().get_from_env("facebook.password")

        if not username or not password:
            raise ValueError("Facebook credentials not found in environment variables.")

        try:
            page.goto("https://www.facebook.com/login")
            page.locator("#email").fill(username)
            page.locator("#pass").fill(password)
            page.locator("[name='login']").click()

            # Basic success check (can be improved later)
            page.wait_for_url("https://www.facebook.com/", timeout=30000)  # Check if redirected to homepage after login

        except (PlaywrightError, Exception) as e:
            log_exception(self.logger, e, "Facebook login failed")
            raise
