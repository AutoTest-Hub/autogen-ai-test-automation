import unittest
import asyncio
from playwright.async_api import async_playwright

class TestBrowserIntegration(unittest.TestCase):

    def test_browser_integration(self):
        async def run_test():
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto("https://www.google.com")
                self.assertEqual(await page.title(), "Google")
                await browser.close()

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()

