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

    def set_channel_preference_for_2_4_band(self, uncheck_channel: int, check_channel: int, priority: int):
        zi_logger.print_context()
        try:
            # uncheck previous channel if checked
            uncheck_sel = f"div.list-row[data-channel=\"{uncheck_channel}\"] input.ch-check"
            if self._page.locator(uncheck_sel).count() > 0:
                if self._page.locator(uncheck_sel).is_checked():
                    self._page.locator(uncheck_sel).click()

            # check desired channel
            check_sel = f"div.list-row[data-channel=\"{check_channel}\"] input.ch-check"
            if self._page.locator(check_sel).count() > 0:
                if not self._page.locator(check_sel).is_checked():
                    self._page.locator(check_sel).click()
            # set preference dropdown for checked channel
            # the select is inside the same row with class pref-inline-dd
            pref_select = f"div.list-row[data-channel=\"{check_channel}\"] select.pref-inline-dd"
            # if the pref-choose button needs to be clicked to enable the select, click it
            pref_btn = f"div.list-row[data-channel=\"{check_channel}\"] button.pref-choose"
            if self._page.locator(pref_btn).count() > 0 and self._page.locator(pref_btn).is_enabled():
                try:
                    self._page.locator(pref_btn).click()
                except Exception:
                    pass
            if self._page.locator(pref_select).count() > 0:
                # ensure select is visible/enabled
                self._page.locator(pref_select).evaluate("el => el.removeAttribute('hidden')")
                self._page.locator(pref_select).select_option(str(priority))

            # click save Apply Radio Settings save-radio-settings
            if self._page.locator("#save-radio-settings").count() > 0:
                # wait for it to be enabled then click
                try:
                    self._page.wait_for_selector("#save-radio-settings:not([disabled])", timeout=5000)
                except Exception:
                    pass
                self._page.locator("#save-radio-settings").click()
        except PlaywrightTimeoutError as e:
            raise Exception(f"Timeout occurred while setting channel preference: {e}")
        except Exception as ERR:
            zi_logger.log(f"Failed to set channel preference: {ERR}")
            raise Exception(f"ERROR : {ERR}")

    def set_fronthaul_network_state(self, profile, enable: bool):
        """
        Toggle the enable/disable checkbox for a network profile and save.

        `profile` can be the profile name or identifier used in the UI.
        `enable` True to enable the profile, False to disable.
        """
        zi_logger.print_context()
        try:
            if not self._page:
                raise Exception("UI page not initialized")
            # attempt direct match first
            card_locator = self._page.locator(f".profile-card:has-text('{profile}')")
            if card_locator.count() == 0:
                # fallback: iterate all profile cards and match header h4 text (case-insensitive, substrings)
                all_cards = self._page.locator(".profile-card")
                found = None
                for idx in range(all_cards.count()):
                    card = all_cards.nth(idx)
                    try:
                        title_loc = card.locator(".profile-header h4")
                        if title_loc.count() > 0:
                            title = title_loc.first.inner_text().strip()
                        else:
                            title = card.inner_text().strip()
                    except Exception:
                        title = card.inner_text().strip()
                    if profile.lower() in (title or "").lower():
                        found = card
                        break
                if not found:
                    raise Exception(f"Profile not found: {profile}")
                checkbox = found.locator("input[type='checkbox']")
            else:
                checkbox = card_locator.locator("input[type='checkbox']")
            chk_count = checkbox.count()
            zi_logger.log(f"set_fronthaul_network_state: profile='{profile}' card_found={1 if 'checkbox' in locals() else 0} checkbox_count={chk_count}")
            if chk_count == 0:
                # try alternate toggle control inside card (styled slider)
                zi_logger.log("checkbox not found, attempting to locate toggle-slider or label")
                slider = None
                try:
                    card = found if 'found' in locals() and found is not None else card_locator
                    slider = card.locator(".toggle-slider")
                    if slider.count() == 0:
                        slider = card.locator("label.toggle-switch")
                except Exception:
                    slider = None
                if slider and slider.count() > 0:
                    zi_logger.log("Found toggle-slider/label, will click it instead of checkbox")
                    # attempt to click slider/label
                    try:
                        # save debug screenshot before click
                        pass
                        slider.first.click()
                        # wait briefly
                        self._page.wait_for_timeout(1000)
                    except Exception as e:
                        zi_logger.log(f"Failed to click slider for profile {profile}: {e}")
                        raise
                else:
                    raise Exception(f"Enable/disable checkbox not found for profile: {profile}")
            else:
                is_checked = checkbox.is_checked()
            # only click if current state differs from desired
            desired_state = bool(enable)
            if (is_checked is None and desired_state) or (is_checked is not None and ((desired_state and not is_checked) or (not desired_state and is_checked))):
                # choose the best clickable target: checkbox if visible/enabled, else slider/label
                card = found if 'found' in locals() and found is not None else card_locator
                chk = card.locator("input[type='checkbox']")
                click_target = None
                try:
                    if chk.count() > 0 and chk.first.is_visible() and chk.first.is_enabled():
                        click_target = chk.first
                    else:
                        alt = card.locator(".toggle-slider")
                        if alt.count() > 0 and alt.first.is_visible() and alt.first.is_enabled():
                            click_target = alt.first
                        else:
                            lbl = card.locator("label.toggle-switch")
                            if lbl.count() > 0 and lbl.first.is_visible() and lbl.first.is_enabled():
                                click_target = lbl.first
                except Exception:
                    click_target = None

                if click_target is None:
                    # as a last resort, try clicking the checkbox even if not visible
                    try:
                        chk.first.click()
                    except Exception as e:
                        zi_logger.log(f"No clickable target found for profile {profile}: {e}")
                        raise
                else:
                    try:
                        click_target.click()
                    except Exception as e:
                        zi_logger.log(f"Click on chosen target failed for profile {profile}: {e}")
                        raise
            # click save-profile-settings if available and wait for it to be enabled
            if self._page.locator("#save-profile-settings").count() > 0:
                try:
                    self._page.wait_for_selector("#save-profile-settings:not([disabled])", timeout=7000)
                    self._page.locator("#save-profile-settings").click()
                except Exception:
                    # if not enabled, still attempt to click
                    try:
                        self._page.locator("#save-profile-settings").click()
                    except Exception:
                        zi_logger.log("Could not click save-profile-settings")

            # Wait for the checkbox state to reflect desired value, poll until timeout
            desired = bool(enable)
            end_time = time.time() + 10
            last_state = None
            while time.time() < end_time:
                try:
                    # re-query checkbox (in case DOM was re-rendered)
                    card = found if 'found' in locals() and found is not None else card_locator
                    chk = card.locator("input[type='checkbox']")
                    if chk.count() == 0:
                        # try slider state by checking aria-checked on label or input
                        lbl = card.locator("label.toggle-switch")
                        if lbl.count() > 0:
                            aria = lbl.first.get_attribute('aria-checked')
                            current = (aria == 'true')
                        else:
                            current = None
                    else:
                        current = chk.first.is_checked()
                    last_state = current
                    if current is not None and current == desired:
                        break
                except Exception:
                    pass
                time.sleep(0.5)
            pass
            if last_state == desired:
                return True
            else:
                raise Exception(f"Timeout waiting for profile '{profile}' state to become {desired}")
        except PlaywrightTimeoutError as e:
            raise Exception(f"Timeout while toggling profile: {profile}")
        except Exception as ERR:
            zi_logger.log(f"Failed to toggle profile {profile}: {ERR}")
            raise Exception(f"ERROR : {ERR}")
