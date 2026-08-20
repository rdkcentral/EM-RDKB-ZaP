# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 Zilogic Systems
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from zaero.bridge.database_module import DatabaseModule
import zaero.utils.zi_logger as zi_logger

from playwright.sync_api import expect, sync_playwright, TimeoutError as PlaywrightTimeoutError

import time

class FeatureUi(DatabaseModule):
    def __init__(self):
        zi_logger.print_context()
        DatabaseModule.__init__(self)
        self.db_obj = self.get_database_module_object()
        zi_logger.log(f"==== db_obj : {self.db_obj}")
        zi_logger.log("rdkb.feature_ui.RdkbUi __init__ : START")
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    def ui_start_playwright(self, device=None):
        zi_logger.print_context()
        try:
            if not self._playwright:
                self._playwright = sync_playwright().start()
        except PlaywrightTimeoutError as e:
            raise Exception(f"Timeout while starting playwright: {e}")
        except Exception as ERR:
            zi_logger.log(f"Could not start playwright")
            raise Exception(f"ERROR : {ERR}")

    def ui_stop_playwright(self, device=None):
        zi_logger.print_context()
        try:
            if self._playwright:
                self._playwright.stop()
        except PlaywrightTimeoutError as e:
            raise Exception(f"Timeout while stopping playwright: {e}")
        except Exception as ERR:
            zi_logger.log(f"Could not stop playwright")
            raise Exception(f"ERROR : {ERR}")

    def ui_open_browser(self, device=None):
        zi_logger.print_context()
        try:
            if not self._browser:
                self._browser = self._playwright.chromium.launch(headless=True)
        except PlaywrightTimeoutError as e:
            raise Exception(f"Timeout while launching chromium browser: {e}")
        except Exception as ERR:
            zi_logger.log(f"Could not open chromium browser")
            raise Exception(f"ERROR : {ERR}")

    def ui_close_browser(self, device=None):
        zi_logger.print_context()
        try:
            if self._browser:
                self._browser.close()
        except PlaywrightTimeoutError as e:
            self._browser = None
            raise Exception(f"Timeout close browser: {e}")
        except Exception as ERR:
            zi_logger.log("Could not close chromium browser")
            raise Exception(f"ERROR : {ERR}")

    def ui_open_context(self, device=None):
        zi_logger.print_context()
        try:
            self._context = self._browser.new_context(viewport=None, ignore_https_errors=True)
        except PlaywrightTimeoutError as e:
            raise Exception(f"Timeout while creating browser context: {e}")
        except Exception as ERR:
            zi_logger.log("Could not open new_context for the chromium browser")
            raise Exception(f"ERROR : {ERR}")

    def ui_close_context(self, device=None):
        zi_logger.print_context()
        try:
            if self._context:
                self._context.close()
        except PlaywrightTimeoutError as e:
            self._context = None
            raise Exception(f"Timeout while close context: {e}")
        except Exception as ERR:
            zi_logger.log("Could not close new_context for the chromium browser")
            raise Exception(f"ERROR : {ERR}")
        
    def ui_open_page(self, device=None):
        zi_logger.print_context()
        try:
            self._page = self._context.new_page()
            self._page.set_default_timeout(30000)
            self._page.set_default_navigation_timeout(30000)
        except PlaywrightTimeoutError as e:
            raise Exception(f"Timeout while opening new page: {e}")
        except Exception as ERR:
            zi_logger.log("Could not open new_page in the chromium browser")
            raise Exception(f"ERROR : {ERR}")

    def ui_close_page(self, device=None):
        zi_logger.print_context()
        try:
            if self._page:
                self._page.close()
        except PlaywrightTimeoutError as e:
            raise Exception(f"Timeout while close page: {e}")
        except Exception as ERR:
            zi_logger.log("Could not close page in the chromium browser")
            raise Exception(f"ERROR : {ERR}")

    def ui_navigate_to_home_page(self, device):
        zi_logger.print_context()
        try:
            ip = self.db_obj.read_from_database(device, 'login_ip')
            port = self.db_obj.read_from_database(device, 'ui_port')
            title = self.db_obj.read_from_database(device, 'ui_home_page_title')
            self._page.goto(f"http://{ip}:{port}/", wait_until="domcontentloaded")
            expect(self._page).to_have_title(title)
        except PlaywrightTimeoutError as e:
            raise Exception(f"Timeout while navigating to home page: {e}")
        except Exception as ERR:
            zi_logger.log(f"Could not open page {ip}:{port}")
            raise Exception(f"ERROR : {ERR}")

    def ui_navigate_to_required_page(self, page):
        zi_logger.print_context()
        try:
            self._page.locator(f"a:has-text('{page}')").first.click()
            expect(self._page.locator(f"h1:has-text('{page}')")).to_be_visible(timeout=15000)
        except PlaywrightTimeoutError as e:
            raise Exception(f"Timeout while navigate to page: {page}")
        except Exception as ERR:
            zi_logger.log(f"Could not navigate to page : {page}")
            raise Exception(f"ERROR : {ERR}")

    def ui_update_input_and_save(self, profile, field, value):
        zi_logger.print_context()
        try:
            self._page.locator(f"button[onclick*=\"editProfile('{profile}')\"]").click()
            time.sleep(2)
            self._page.fill(field, value)
            time.sleep(2)
            self._page.click("button[type='submit']")
            time.sleep(2)
            self._page.wait_for_selector("#save-profile-settings:not([disabled])")
            time.sleep(2)
            self._page.click("#save-profile-settings")
        except PlaywrightTimeoutError as e:
            raise Exception(f"Timeout occurred while updating profile settings")
        except Exception as ERR:
            zi_logger.log(f"Failed to update profile settings")
            raise Exception(f"ERROR : {ERR}")

    def ui_wifi_reset_dialog_handler(self, dialog):
        try:
            msg = dialog.message.lower()

            zi_logger.log(f"Dialog Message:\n{msg}")

            if "resetting the wi-fi configuration" in msg:
                dialog.accept()
                zi_logger.log("Accepted reset confirmation dialog")

            elif "wi-fi configuration reset successfully" in msg:
                dialog.accept()
                zi_logger.log("Accepted success dialog")

            else:
                zi_logger.log(f"Unknown dialog received: {msg}")
                dialog.accept()

        except Exception as e:
            zi_logger.log(f"Dialog handler failed: {e}")

    def ui_set_dialog_handler(self):
        try:
            self._page.on("dialog", self.ui_wifi_reset_dialog_handler)
        except Exception as e:
            zi_logger.log(f"Failed to set dialog handler: {e}")

    def ui_click_button(self, btn_name):
        zi_logger.print_context()
        try:        
            self._page.locator(btn_name).click()
            self._page.wait_for_timeout(10000)
        except PlaywrightTimeoutError as e:
            raise Exception(f"Timeout occurred while wifi reset")
        except Exception as ERR:
            zi_logger.log(f"Failed to reset WiFi")
            raise Exception(f"ERROR : {ERR}")
