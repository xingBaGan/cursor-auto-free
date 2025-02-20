import time
import random
from typing import Dict, Any
from logger import logging
from browser_utils import BrowserManager
from get_email_code import EmailVerificationHandler
from email_generator import EmailGenerator
from cursor_auth_manager import CursorAuthManager
from enum import Enum
from typing import Optional
import os
from config import Config
import json

# 定义 EMOJI 字典
EMOJI = {"ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}


class VerificationStatus(Enum):
    """验证状态枚举"""

    PASSWORD_PAGE = "@name=password"
    CAPTCHA_PAGE = "@data-index=0"
    ACCOUNT_SETTINGS = "Account Settings"


class TurnstileError(Exception):
    """Turnstile 验证相关异常"""

    pass


def save_screenshot(tab, stage: str, timestamp: bool = True) -> None:
    """
    保存页面截图

    Args:
        tab: 浏览器标签页对象
        stage: 截图阶段标识
        timestamp: 是否添加时间戳
    """
    try:
        # 创建 screenshots 目录
        screenshot_dir = "screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        # 生成文件名
        if timestamp:
            filename = f"turnstile_{stage}_{int(time.time())}.png"
        else:
            filename = f"turnstile_{stage}.png"

        filepath = os.path.join(screenshot_dir, filename)

        # 保存截图
        tab.get_screenshot(filepath)
        logging.debug(f"截图已保存: {filepath}")
    except Exception as e:
        logging.warning(f"截图保存失败: {str(e)}")


def check_verification_success(tab) -> Optional[VerificationStatus]:
    """
    检查验证是否成功

    Returns:
        VerificationStatus: 验证成功时返回对应状态，失败返回 None
    """
    for status in VerificationStatus:
        if tab.ele(status.value):
            logging.info(f"验证成功 - 已到达{status.name}页面")
            return status
    return None


def handle_turnstile(tab, max_retries: int = 2, retry_interval: tuple = (1, 2)) -> bool:
    """
    处理 Turnstile 验证

    Args:
        tab: 浏览器标签页对象
        max_retries: 最大重试次数
        retry_interval: 重试间隔时间范围(最小值, 最大值)

    Returns:
        bool: 验证是否成功

    Raises:
        TurnstileError: 验证过程中出现异常
    """
    logging.info("正在检测 Turnstile 验证...")
    save_screenshot(tab, "start")

    retry_count = 0

    try:
        while retry_count < max_retries:
            retry_count += 1
            logging.debug(f"第 {retry_count} 次尝试验证")

            try:
                # 定位验证框元素
                challenge_check = (
                    tab.ele("@id=cf-turnstile", timeout=2)
                    .child()
                    .shadow_root.ele("tag:iframe")
                    .ele("tag:body")
                    .sr("tag:input")
                )

                if challenge_check:
                    logging.info("检测到 Turnstile 验证框，开始处理...")
                    # 随机延时后点击验证
                    time.sleep(random.uniform(1, 3))
                    challenge_check.click()
                    time.sleep(2)

                    # 保存验证后的截图
                    save_screenshot(tab, "clicked")

                    # 检查验证结果
                    if check_verification_success(tab):
                        logging.info("Turnstile 验证通过")
                        save_screenshot(tab, "success")
                        return True

            except Exception as e:
                logging.debug(f"当前尝试未成功: {str(e)}")

            # 检查是否已经验证成功
            if check_verification_success(tab):
                return True

            # 随机延时后继续下一次尝试
            time.sleep(random.uniform(*retry_interval))

        # 超出最大重试次数
        logging.error(f"验证失败 - 已达到最大重试次数 {max_retries}")
        logging.error(
            "请前往开源项目查看更多信息：https://github.com/chengazhen/cursor-auto-free"
        )
        save_screenshot(tab, "failed")
        return False

    except Exception as e:
        error_msg = f"Turnstile 验证过程发生异常: {str(e)}"
        logging.error(error_msg)
        save_screenshot(tab, "error")
        raise TurnstileError(error_msg)


def update_cursor_auth(email=None, access_token=None, refresh_token=None):
    """
    更新Cursor的认证信息的便捷函数
    """
    auth_manager = CursorAuthManager()
    return auth_manager.update_auth(email, access_token, refresh_token)

class EmailGenerator:
    def __init__(
        self,
        password="".join(
            random.choices(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
                k=12,
            )
        ),
    ):
        configInstance = Config()
        configInstance.print_config()
        self.domain = configInstance.get_domain()
        self.default_password = password
        self.default_first_name = self.generate_random_name()
        self.default_last_name = self.generate_random_name()

    def generate_random_name(self, length=6):
        """生成随机用户名"""
        first_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        rest_letters = "".join(
            random.choices("abcdefghijklmnopqrstuvwxyz", k=length - 1)
        )
        return first_letter + rest_letters

    def generate_email(self, length=8):
        """生成随机邮箱地址"""
        random_str = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length))
        timestamp = str(int(time.time()))[-6:]  # 使用时间戳后6位
        return f"{random_str}{timestamp}@{self.domain}"

    def get_account_info(self):
        """获取完整的账号信息"""
        return {
            "email": self.generate_email(),
            "password": self.default_password,
            "first_name": self.default_first_name,
            "last_name": self.default_last_name,
        }


def get_user_agent():
    """获取user_agent"""
    try:
        # 使用JavaScript获取user agent
        browser_manager = BrowserManager()
        browser = browser_manager.init_browser()
        user_agent = browser.latest_tab.run_js("return navigator.userAgent")
        browser_manager.quit()
        return user_agent
    except Exception as e:
        logging.error(f"获取user agent失败: {str(e)}")
        return None

def print_end_message():
    logging.info("\n\n\n\n\n")
    logging.info("=" * 30)
    logging.info("所有操作已完成")
    logging.info("\n=== 获取更多信息 ===")
    logging.info("🔥 QQ交流群: 1034718338")
    logging.info("📺 B站UP主: 想回家的前端")
    logging.info("=" * 30)
    logging.info(
        "请前往开源项目查看更多信息：https://github.com/chengazhen/cursor-auto-free"
    )

login_url = "https://authenticator.cursor.sh"
sign_up_url = "https://authenticator.cursor.sh/sign-up"
settings_url = "https://www.cursor.com/settings"
mail_url = "https://tempmail.plus"

def sign_up_account(browser, tab, account_info, email_handler):
    logging.info("=== 开始注册账号流程 ===")
    logging.info(f"正在访问注册页面: {sign_up_url}")
    tab.get(sign_up_url)

    try:
        if tab.ele("@name=first_name"):
            logging.info("正在填写个人信息...")
            tab.actions.click("@name=first_name").input(account_info['first_name'])
            logging.info(f"已输入名字: {account_info['first_name']}")
            time.sleep(random.uniform(1, 3))

            tab.actions.click("@name=last_name").input(account_info['last_name'])
            logging.info(f"已输入姓氏: {account_info['last_name']}")
            time.sleep(random.uniform(1, 3))

            tab.actions.click("@name=email").input(account_info['email'])
            logging.info(f"已输入邮箱: {account_info['email']}")
            time.sleep(random.uniform(1, 3))

            logging.info("提交个人信息...")
            tab.actions.click("@type=submit")

    except Exception as e:
        logging.error(f"注册页面访问失败: {str(e)}")
        return False

    handle_turnstile(tab)

    try:
        if tab.ele("@name=password"):
            logging.info("正在设置密码...")
            tab.ele("@name=password").input(account_info['password'])
            time.sleep(random.uniform(1, 3))

            logging.info("提交密码...")
            tab.ele("@type=submit").click()
            logging.info("密码设置完成，等待系统响应...")

    except Exception as e:
        logging.error(f"密码设置失败: {str(e)}")
        return False

    if tab.ele("This email is not available."):
        logging.error("注册失败：邮箱已被使用")
        return False

    handle_turnstile(tab)

    total_usage = None  # 初始化 total_usage 变量
    while True:
        try:
            if tab.ele("Account Settings"):
                logging.info("注册成功 - 已进入账户设置页面")
                break
            if tab.ele("@data-index=0"):
                logging.info("正在获取邮箱验证码...")
                code = email_handler.get_verification_code()
                if not code:
                    logging.error("获取验证码失败")
                    return False

                logging.info(f"成功获取验证码: {code}")
                logging.info("正在输入验证码...")
                for i, digit in enumerate(code):
                    tab.ele(f"@data-index={i}").input(digit)
                    time.sleep(random.uniform(0.1, 0.3))
                logging.info("验证码输入完成")
                break
        except Exception as e:
            logging.error(f"验证码处理过程出错: {str(e)}")
            return False

    handle_turnstile(tab)
    wait_time = random.randint(3, 6)
    for i in range(wait_time):
        logging.info(f"等待系统处理中... 剩余 {wait_time-i} 秒")
        time.sleep(1)

    logging.info("正在获取账户信息...")
    tab.get(settings_url)
    try:
        usage_selector = (
            "css:div.col-span-2 > div > div > div > div > "
            "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
            "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
        )
        usage_ele = tab.ele(usage_selector)
        if usage_ele:
            usage_info = usage_ele.text
            total_usage = usage_info.split("/")[-1].strip()
            logging.info(f"账户可用额度上限: {total_usage}")
            logging.info(
                "请前往开源项目查看更多信息：https://github.com/chengazhen/cursor-auto-free"
            )
    except Exception as e:
        logging.error(f"获取账户额度信息失败: {str(e)}")
        total_usage = "Unknown"

    logging.info("\n=== 注册完成 ===")
    account_info_str = f"Cursor 账号信息:\n邮箱: {account_info['email']}\n密码: {account_info['password']}"
    info_obj = {
        "email": account_info['email'],
        "password": account_info['password'],
        "usage_limit": total_usage
    }
    logging.info(account_info_str)
    
    # 保存账号信息到文件
    try:
        if not os.path.exists("account_info.json"):
            with open("account_info.json", "w", encoding="utf-8") as f:
                json.dump([info_obj], f, ensure_ascii=False, indent=2)
        else:
            with open("account_info.json", "r", encoding="utf-8") as f:
                accounts = json.load(f)
                accounts.append(info_obj)
                with open("account_info.json", "w", encoding="utf-8") as f:
                    json.dump(accounts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"保存账号信息失败: {str(e)}")

    time.sleep(5)
    return True

class CursorSignupService:
    def __init__(self):
        self.browser_manager = None
        self.email_handler = None
        self.account_info = None
        self.password = None
        self.first_name = None
        self.last_name = None
        self.cards_file = "cards.json"
        self.max_accounts_per_card = 5

    def get_cursor_session_token(self, tab, max_attempts=3, retry_interval=2):
        """
        获取Cursor会话token，带有重试机制
        :param tab: 浏览器标签页
        :param max_attempts: 最大尝试次数
        :param retry_interval: 重试间隔(秒)
        :return: session token 或 None
        """
        logging.info("开始获取cookie")
        attempts = 0

        while attempts < max_attempts:
            try:
                cookies = tab.cookies()
                for cookie in cookies:
                    if cookie.get("name") == "WorkosCursorSessionToken":
                        return cookie["value"].split("%3A%3A")[1]

                attempts += 1
                if attempts < max_attempts:
                    logging.warning(
                        f"第 {attempts} 次尝试未获取到CursorSessionToken，{retry_interval}秒后重试..."
                    )
                    time.sleep(retry_interval)
                else:
                    logging.error(
                        f"已达到最大尝试次数({max_attempts})，获取CursorSessionToken失败"
                    )

            except Exception as e:
                logging.error(f"获取cookie失败: {str(e)}")
                attempts += 1
                if attempts < max_attempts:
                    logging.info(f"将在 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)

        return None

    def get_user_agent(self) -> str:
        try:
            self.browser_manager = BrowserManager()
            browser = self.browser_manager.init_browser()
            user_agent = browser.latest_tab.run_js("return navigator.userAgent")
            user_agent = user_agent.replace("HeadlessChrome", "Chrome")
            return user_agent
        except Exception as e:
            logging.error(f"获取user agent失败: {str(e)}")
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def handle_turnstile(self, tab, max_retries: int = 2, retry_interval: tuple = (1, 2)) -> bool:
        """
        处理 Turnstile 验证

        Args:
            tab: 浏览器标签页对象
            max_retries: 最大重试次数
            retry_interval: 重试间隔时间范围(最小值, 最大值)

        Returns:
            bool: 验证是否成功

        Raises:
            TurnstileError: 验证过程中出现异常
        """
        logging.info("正在检测 Turnstile 验证...")
        save_screenshot(tab, "start")

        retry_count = 0

        try:
            while retry_count < max_retries:
                retry_count += 1
                logging.debug(f"第 {retry_count} 次尝试验证")

                try:
                    # 定位验证框元素
                    challenge_check = (
                        tab.ele("@id=cf-turnstile", timeout=2)
                        .child()
                        .shadow_root.ele("tag:iframe")
                        .ele("tag:body")
                        .sr("tag:input")
                    )

                    if challenge_check:
                        logging.info("检测到 Turnstile 验证框，开始处理...")
                        # 随机延时后点击验证
                        time.sleep(random.uniform(1, 3))
                        challenge_check.click()
                        time.sleep(2)

                        # 保存验证后的截图
                        save_screenshot(tab, "clicked")

                        # 检查验证结果
                        if check_verification_success(tab):
                            logging.info("Turnstile 验证通过")
                            save_screenshot(tab, "success")
                            return True

                except Exception as e:
                    logging.debug(f"当前尝试未成功: {str(e)}")

                # 检查是否已经验证成功
                if check_verification_success(tab):
                    return True

                # 随机延时后继续下一次尝试
                time.sleep(random.uniform(*retry_interval))

            # 超出最大重试次数
            logging.error(f"验证失败 - 已达到最大重试次数 {max_retries}")
            logging.error(
                "请前往开源项目查看更多信息：https://github.com/chengazhen/cursor-auto-free"
            )
            save_screenshot(tab, "failed")
            return False

        except Exception as e:
            error_msg = f"Turnstile 验证过程发生异常: {str(e)}"
            logging.error(error_msg)
            save_screenshot(tab, "error")
            raise TurnstileError(error_msg)

    def sign_up_account(self) -> Dict[str, Any]:
        try:
            # 初始化必要组件
            user_agent = self.get_user_agent()
            self.browser_manager = BrowserManager()
            browser = self.browser_manager.init_browser(user_agent)
            self.email_handler = EmailVerificationHandler()
            
            # 生成账号信息
            email_generator = EmailGenerator()
            self.account_info = email_generator.get_account_info()
            logging.info(f"生成的邮箱账号: {self.account_info['email']}")
            tab = browser.latest_tab
            tab.run_js("try { turnstile.reset() } catch(e) { }")
            
            # 开始注册流程
            tab.get(sign_up_url)
            
            # 执行注册流程
            success = sign_up_account(browser, tab, self.account_info, self.email_handler)
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to sign up account'
                }
                
            # 获取token
            token = self.get_cursor_session_token(tab)
            if not token:
                return {
                    'success': False,
                    'error': 'Failed to get session token'
                }
                
            # 更新认证信息
            auth_manager = CursorAuthManager()
            auth_manager.update_auth(
                email=self.account_info['email'],
                access_token=token,
                refresh_token=token
            )
            
            # 获取使用额度信息
            usage_limit = self.get_usage_limit(tab)
            
            return {
                'success': True,
                'email': self.account_info['email'],
                'password': self.account_info['password'],
                'token': token,
                'usage_limit': usage_limit
            }
            
        except Exception as e:
            logging.error(f"注册失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            if self.browser_manager:
                self.browser_manager.quit()

    def get_usage_limit(self, tab) -> str:
        try:
            tab.get(settings_url)
            usage_selector = (
                "css:div.col-span-2 > div > div > div > div > "
                "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
                "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
            )
            usage_ele = tab.ele(usage_selector)
            if usage_ele:
                usage_info = usage_ele.text
                return usage_info.split("/")[-1].strip()
        except Exception as e:
            logging.error(f"获取账户额度信息失败: {str(e)}")
            return "Unknown"

    def validate_card(self, card_number: str) -> bool:
        """
        验证卡密是否有效且未超过使用次数限制
        
        Args:
            card_number: 卡密号码
            
        Returns:
            bool: 卡密是否有效
        """
        try:
            if not os.path.exists(self.cards_file):
                logging.error("cards.json 文件不存在")
                return False
                
            with open(self.cards_file, 'r', encoding='utf-8') as f:
                cards = json.load(f)
                
            # 查找卡密
            card = next((c for c in cards if c.get('number') == card_number), None)
            if not card:
                logging.error("无效的卡密")
                return False
                
            # 检查使用次数
            if card.get('used_count', 0) >= self.max_accounts_per_card:
                logging.error(f"卡密已达到最大使用次数 ({self.max_accounts_per_card})")
                return False
                
            return True
                
        except Exception as e:
            logging.error(f"验证卡密时出错: {str(e)}")
            return False
            
    def update_card_usage(self, card_number: str) -> bool:
        """
        更新卡密使用次数
        
        Args:
            card_number: 卡密号码
            
        Returns:
            bool: 更新是否成功
        """
        try:
            with open(self.cards_file, 'r', encoding='utf-8') as f:
                cards = json.load(f)
                
            # 更新使用次数
            for card in cards:
                if card['number'] == card_number:
                    card['used_count'] = card.get('used_count', 0) + 1
                    break
                    
            # 保存更新后的数据
            with open(self.cards_file, 'w', encoding='utf-8') as f:
                json.dump(cards, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            logging.error(f"更新卡密使用次数时出错: {str(e)}")
            return False

    def register_with_card(self, card_number: str) -> Dict[str, Any]:
        """
        使用卡密注册新账号
        
        Args:
            card_number: 卡密号码
            
        Returns:
            Dict[str, Any]: 注册结果，包含成功状态和账号信息
        """
        # 验证卡密
        if not self.validate_card(card_number):
            return {
                'success': False,
                'error': '无效的卡密或已达到使用次数限制'
            }
            
        # 执行注册流程
        result = self.sign_up_account()
        
        # 如果注册成功，更新卡密使用次数
        if result['success']:
            if not self.update_card_usage(card_number):
                logging.warning("更新卡密使用次数失败，但账号已注册成功")
                
        return result 