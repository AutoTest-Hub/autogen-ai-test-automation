# Playwright Installation Troubleshooting

## Issue: `playwright install` runs silently with no output

This can happen for several reasons. Let's diagnose and fix it step by step.

## Step 1: Check Playwright Installation Status

```bash
# Check if Playwright is properly installed
python3 -m playwright --version

# Check if browsers are already installed
python3 -m playwright install --dry-run

# List installed browsers
ls -la ~/Library/Caches/ms-playwright/
```

## Step 2: Verbose Installation

Try installing with verbose output:

```bash
# Install with verbose output
python3 -m playwright install --verbose

# Or install just Chromium with verbose output
python3 -m playwright install chromium --verbose

# Force reinstall if needed
python3 -m playwright install --force
```

## Step 3: Check Installation Location

```bash
# Check where Playwright expects browsers (macOS)
echo "Playwright cache location:"
echo "~/Library/Caches/ms-playwright/"
ls -la ~/Library/Caches/ms-playwright/

# Check if Chromium exists at the expected path
ls -la "/Library/Caches/ms-playwright/chromium-1091/chrome-mac/Chromium.app/Contents/MacOS/Chromium"
```

## Step 4: Alternative Installation Methods

### Method 1: Install via pip with browsers
```bash
# Reinstall Playwright with browsers
pip install playwright
python3 -m playwright install
```

### Method 2: Install specific browser
```bash
# Install only Chromium (smaller download)
python3 -m playwright install chromium

# Check if it worked
python3 -c "from playwright.sync_api import sync_playwright; print('Playwright working!')"
```

### Method 3: Manual verification
```bash
# Test Playwright installation
python3 -c "
from playwright.async_api import async_playwright
import asyncio

async def test():
    playwright = await async_playwright().start()
    print('Playwright started successfully')
    browser = await playwright.chromium.launch(headless=True)
    print('Browser launched successfully')
    await browser.close()
    await playwright.stop()
    print('Test completed successfully')

asyncio.run(test())
"
```

## Step 5: Quick Test Without Full Installation

If installation is problematic, let's test with a simpler approach:

```bash
# Create a simple test to verify Playwright works
cat > simple_playwright_test.py << 'EOF'
import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    try:
        playwright = await async_playwright().start()
        print("✅ Playwright started successfully")
        
        # Try to launch browser
        browser = await playwright.chromium.launch(headless=True)
        print("✅ Chromium browser launched successfully")
        
        # Create a page
        page = await browser.new_page()
        print("✅ New page created successfully")
        
        # Navigate to a simple page
        await page.goto("https://example.com")
        print("✅ Navigation successful")
        
        # Get title
        title = await page.title()
        print(f"✅ Page title: {title}")
        
        # Cleanup
        await browser.close()
        await playwright.stop()
        print("✅ All tests passed - Playwright is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("❌ Playwright installation may be incomplete")

if __name__ == "__main__":
    asyncio.run(test_playwright())
EOF

# Run the simple test
python3 simple_playwright_test.py
```

## Step 6: Common macOS Issues and Fixes

### Issue: Permission Problems
```bash
# Fix permissions
sudo chown -R $(whoami) ~/Library/Caches/ms-playwright/
```

### Issue: Network/Proxy Problems
```bash
# Install with different approach
pip install --upgrade playwright
python3 -m playwright install --with-deps
```

### Issue: Multiple Python Versions
```bash
# Make sure you're using the right Python
which python3
which pip3

# Install for specific Python version
python3.11 -m pip install playwright
python3.11 -m playwright install
```

## Step 7: Alternative - Use Different Browser

If Chromium installation fails, try Firefox:

```bash
# Install Firefox instead
python3 -m playwright install firefox

# Update your test to use Firefox
# In test_user_login_test.py, change:
# browser = await playwright.chromium.launch(headless=True)
# to:
# browser = await playwright.firefox.launch(headless=True)
```

## Step 8: Verification Commands

After trying the fixes above, verify with these commands:

```bash
# 1. Check Playwright version
python3 -m playwright --version

# 2. List available browsers
python3 -m playwright install --help

# 3. Check browser installation
python3 -c "
import os
cache_dir = os.path.expanduser('~/Library/Caches/ms-playwright/')
if os.path.exists(cache_dir):
    print('✅ Playwright cache directory exists')
    for item in os.listdir(cache_dir):
        print(f'  - {item}')
else:
    print('❌ Playwright cache directory not found')
"

# 4. Test browser launch
python3 -c "
import asyncio
from playwright.async_api import async_playwright

async def test():
    p = await async_playwright().start()
    try:
        browser = await p.chromium.launch()
        print('✅ Browser launch successful')
        await browser.close()
    except Exception as e:
        print(f'❌ Browser launch failed: {e}')
    finally:
        await p.stop()

asyncio.run(test())
"
```

## Expected Successful Output

When Playwright is properly installed, you should see:
```
✅ Playwright started successfully
✅ Chromium browser launched successfully  
✅ New page created successfully
✅ Navigation successful
✅ Page title: Example Domain
✅ All tests passed - Playwright is working!
```

## If All Else Fails - Docker Alternative

```bash
# Run the test in a Docker container with Playwright pre-installed
docker run --rm -v $(pwd):/work -w /work mcr.microsoft.com/playwright/python:v1.40.0 \
    bash -c "pip install pytest pytest-asyncio && python3 -m pytest test_user_login_test.py -v"
```

## Next Steps

1. **Try Step 2 first** (verbose installation)
2. **Run Step 5** (simple test) to verify
3. **If still failing**, try Step 6 (macOS fixes)
4. **Report back** with the output from any of these commands

The goal is to get this output when running your test:
```
✅ Browser launches
✅ Navigates to website
✅ Test executes (may fail on login, but that's expected)
```

