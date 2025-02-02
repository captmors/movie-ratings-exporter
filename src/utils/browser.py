from playwright.sync_api import sync_playwright, Page
from typing import Optional, Dict, Any, List
import os
from src.config import COOKIES_LIST
from src.utils.browser_config import DEFAULT_LAUNCH_OPTIONS, DEFAULT_ADDITIONAL_ARGS, DEFAULT_CONTEXT_SETTINGS


class Browser:
    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    def setup(self, 
              browser_type: str = "chromium",
              launch_options: Optional[Dict[str, Any]] = DEFAULT_LAUNCH_OPTIONS,
              additional_args: Optional[List[str]] = DEFAULT_ADDITIONAL_ARGS,
              context_settings: Optional[Dict[str, Any]] = DEFAULT_CONTEXT_SETTINGS,
              cookies: Optional[List[Dict[str, Any]]] = COOKIES_LIST) -> None:
        """
        Инициализация браузера с настраиваемыми параметрами
        
        Args:
            browser_type: ("chromium", "firefox", "webkit")
            
            launch_options:
                Примеры:
                - slow_mo=500:                                  
                - timeout=60000:                                
                - downloads_path="/path/to/dir":                
                - ignore_default_args=["--disable-extensions"]: 
                - channel="chrome":  
                                           
            additional_args:  
                Примеры:
                - "--disable-gpu": Отключение GPU
                - "--no-sandbox": Запуск без песочницы
                - "--disable-setuid-sandbox": Отключение SUID песочницы
                - "--disable-dev-shm-usage": Решение проблем с памятью в Docker      
                
            context_settings:
                Примеры:
                - viewport={"width": 1920, "height": 1080}: Устанавливает размеры окна
                - user_agent="Custom User Agent": Переопределяет User-Agent
                - ignore_https_errors=True: Игнорирует ошибки HTTPS
                - permissions=["geolocation", "notifications"]: Устанавливает разрешения
                - geolocation={"latitude": 51.5074, "longitude": -0.1278}: Задает геолокацию
                - locale="en-US": Устанавливает локаль браузера
                - timezone_id="Europe/London": Устанавливает часовой пояс                  
        """
        
        os.system(f"playwright install {browser_type}")
        
        self._playwright = sync_playwright().start()
        
        if additional_args:
            launch_options["args"] = additional_args
            
        if browser_type == "chromium":
            self._browser = self._playwright.chromium.launch(**launch_options)
        elif browser_type == "firefox":
            self._browser = self._playwright.firefox.launch(**launch_options)
        elif browser_type == "webkit":
            self._browser = self._playwright.webkit.launch(**launch_options)
        else:
            raise ValueError(f"Неподдерживаемый тип браузера: {browser_type}")


        self._context = self._browser.new_context(**context_settings)
        
        if cookies:
            self._context.add_cookies(cookies)
            
        self._context.route("**/*", self._handle_request)
        
        self._page = self._context.new_page()
        self._page.set_default_timeout(30_000)
        self._page.set_default_navigation_timeout(30_000)
        self._setup_page_scripts()
    
    
    def _handle_request(self, route):
        """Обработчик сетевых запросов"""
        
        # Можно модифицировать заголовки
        headers = route.request.headers
        headers["Cache-Control"] = "max-age=0"
        
        # Продолжаем запрос с модифицированными заголовками
        route.continue_(headers=headers)


    def _setup_page_scripts(self):
        """Установка скриптов для маскировки автоматизации"""
        
        # Переопределение свойств navigator
        self._page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {
                    0: {type: "application/x-google-chrome-pdf"},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                }
            ]
        });
        """)


    @property
    def page(self) -> Page:
        """Получить текущую страницу"""
        return self._page


    def close(self) -> None:
        """Закрыть все ресурсы"""
        if self._page:
            self._page.close()
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        


if __name__ == "__main__":
    with Browser() as browser:
        browser.setup(
            browser_type="chromium"
        )

        page = browser.page
        page.goto("https://bot.sannysoft.com")
        page.wait_for_timeout(5_000)
