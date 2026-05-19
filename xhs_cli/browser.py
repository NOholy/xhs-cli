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
        self.browser = None

    def start(self):
        engine_type = os.getenv("XHS_BROWSER_ENGINE", "obscura").lower()
        logger.info("Starting browser engine: %s", engine_type)
        
        if engine_type == "cloak":
            from cloakbrowser import launch
            humanize = os.getenv("XHS_HUMANIZE", "1").lower() in ("1", "true")
            self.browser = launch(headless=self.headless, humanize=humanize)
            
        elif engine_type == "camoufox":
            from camoufox.sync_api import Camoufox
            self._ctx_manager = Camoufox(headless=self.headless)
            self.browser = self._ctx_manager.__enter__()
            
        elif engine_type == "obscura":
            from playwright.sync_api import sync_playwright
            logger.info("Connecting to obscura via CDP at ws://127.0.0.1:9222")
            self._ctx_manager = sync_playwright().start()
            self.browser = self._ctx_manager.chromium.connect_over_cdp("ws://127.0.0.1:9222/devtools/browser")
            
        else:
            raise ValueError(f"Unknown browser engine: {engine_type}")
            
        return self.browser

    def close(self):
        if hasattr(self, 'browser') and self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
        if self._ctx_manager:
            try:
                if hasattr(self._ctx_manager, '__exit__'):
                    self._ctx_manager.__exit__(None, None, None)
                elif hasattr(self._ctx_manager, 'stop'):
                    self._ctx_manager.stop()
            except Exception:
                pass
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
