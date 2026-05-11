import os
import logging
from contextlib import contextmanager
from typing import Iterator

logger = logging.getLogger(__name__)

class BrowserEngine:
    """Browser engine abstract factory to manage underlying anti-detect browser lifecycle."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._ctx_manager = None
        self._pw = None
        self.browser = None

    def start(self):
        engine_type = os.getenv("XHS_BROWSER_ENGINE", "cloak").lower()
        logger.info("Starting browser engine: %s", engine_type)
        
        if engine_type == "cloak":
            from cloakbrowser import launch
            humanize = os.getenv("XHS_HUMANIZE", "0").lower() in ("1", "true")
            self.browser = launch(headless=self.headless, humanize=humanize)
            
        elif engine_type == "camoufox":
            from camoufox.sync_api import Camoufox
            self._ctx_manager = Camoufox(headless=self.headless)
            self.browser = self._ctx_manager.__enter__()
            
        elif engine_type == "playwright":
            from playwright.sync_api import sync_playwright
            self._pw = sync_playwright().start()
            executable_path = os.getenv("XHS_BROWSER_EXECUTABLE")
            
            if not executable_path:
                logger.warning("XHS_BROWSER_EXECUTABLE is not set, using default chromium.")
                
            self.browser = self._pw.chromium.launch(
                headless=self.headless,
                executable_path=executable_path
            )
        else:
            raise ValueError(f"Unknown browser engine: {engine_type}")
            
        return self.browser

    def close(self):
        if hasattr(self, 'browser') and self.browser:
            self.browser.close()
        if self._pw:
            self._pw.stop()
            self._pw = None
        elif self._ctx_manager:
            self._ctx_manager.__exit__(None, None, None)
            self._ctx_manager = None
            
        self.browser = None

@contextmanager
def get_browser(headless: bool = True) -> Iterator:
    """Context manager for browser interactions (like QR code login)."""
    engine = BrowserEngine(headless=headless)
    try:
        yield engine.start()
    finally:
        engine.close()
