import allure

from config.global_vars import GLOBAL_VARS
from utils.base_utils.base_page import BasePage


class LoginPage(BasePage):
    locator_password_login_tab = "text=密码登录"
    locator_username = 'input[type="text"]'
    locator_password = 'input[type="password"]'
    locator_agreement = '[role="checkbox"]'
    locator_login_button = "xpath=//button[normalize-space()='登录']"
    locator_captcha_prompt = "text=拖动滑块完成验证"
    locator_captcha_slider = ".slide-verify-slider-mask-item"

    @allure.step("固定滑块验证码随机位置")
    def prepare_deterministic_captcha(self):
        self.page.add_init_script("Math.random = () => 0.5")
        return self

    @allure.step("访问 SurgSmart 登录页面")
    def navigate(self, timeout: int = 30000):
        self.page.goto(
            GLOBAL_VARS["url"] + "/login?from=/work-station",
            timeout=timeout,
            wait_until="domcontentloaded",
        )
        return self

    @allure.step("切换到密码登录")
    def select_password_login(self):
        self.click(self.locator_password_login_tab)
        return self

    @allure.step("输入登录账号：{value}")
    def input_username(self, value):
        self.input(self.locator_username, value)
        return self

    @allure.step("输入登录密码")
    def input_password(self, value):
        self.page.fill(self.locator_password, value)
        return self

    @allure.step("同意用户协议和隐私政策")
    def accept_agreement(self):
        self.click(self.locator_agreement)
        return self

    @allure.step("提交登录表单")
    def submit_login(self):
        self.click(self.locator_login_button)
        return self

    @allure.step("完成滑块验证码")
    def complete_slider_captcha(self, distance):
        self.page.locator(self.locator_captcha_prompt).wait_for(
            state="visible",
            timeout=15000,
        )
        self.slide_captcha(
            slider_locator=self.locator_captcha_slider,
            distance=distance,
        )
        self.assert_element_hidden(self.locator_captcha_prompt, timeout=5000)
        return self

    @allure.step("SurgSmart 密码登录并完成滑块验证")
    def login_with_slider_captcha_flow(self, case):
        return (
            self.select_password_login()
            .input_username(case.get("login", ""))
            .input_password(case.get("password", ""))
            .accept_agreement()
            .submit_login()
            .complete_slider_captcha(case.get("captcha_distance", 167.4))
        )
