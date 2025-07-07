from playwright.sync_api import Playwright, sync_playwright
from playwright_stealth.stealth import Stealth
import time


class PlayBrowser:
    def __init__(self) -> None:
        self.pc = Stealth().use_sync(sync_playwright()).__enter__()
        self.browser = self.pc.chromium.launch(headless=False)
        self.page = self.browser.new_page(java_script_enabled=True)

    def visit_page(self, url: str):
        self.page.goto(url)
        # self.page.wait_for_selector("input")
        time.sleep(5)
        return self.page.content()

    def perform_action(self, action_data, credentials):
        action = action_data["action"]
        selector = action_data["selector"]
        field = action_data["field"]

        if action == "fill":
            data = credentials[field]
            locator = self.page.locator(selector)
            # locator.wait_for(state="")
            if locator.is_visible():
                locator.fill(data)
            else:
                print(f"skip an fill operation : {field}")
        if action == "click":
            locator = self.page.locator(selector)
            if locator.is_visible() and locator.is_enabled():
                locator.click()
            time.sleep(10)
        if action == "check":
            locator = self.page.locator(selector)
            if locator.is_visible() and (not locator.is_checked()):
                locator.check()
