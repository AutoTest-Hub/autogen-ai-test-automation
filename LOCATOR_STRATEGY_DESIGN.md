# Priority-Based Locator Strategy Design

## Problem Analysis

### Current Issues
1. **Invalid Playwright Syntax**: Current implementation uses comma-separated selectors like `"[data-testid*='user'], [class*='user'], [class*='profile']"` which is invalid in Playwright
2. **No Fallback Mechanism**: Tests fail immediately if the primary selector doesn't work
3. **Application-Specific Hardcoding**: Selectors are often hardcoded for specific applications
4. **Poor Maintainability**: When selectors break, tests need manual updates

### Root Cause
The framework attempts to use CSS selector syntax with comma-separated alternatives, but Playwright requires individual locator calls with proper fallback logic.

## Proposed Solution: Priority-Based Locator Strategy

### Core Principles
1. **Single Selector Per Attempt**: Each locator call uses only one selector
2. **Priority-Based Fallback**: Multiple selectors ordered by reliability and specificity
3. **Application-Agnostic**: Generic selectors that work across different web applications
4. **Automatic Retry**: Framework automatically tries next priority selector if current one fails
5. **Semantic Mapping**: Map UI elements to semantic types (login_button, username_field, etc.)

### Locator Priority Hierarchy

#### 1. High Priority (Most Reliable)
- `data-testid` attributes
- `id` attributes
- `name` attributes for form elements

#### 2. Medium Priority (Moderately Reliable)
- Specific class names
- Type-based selectors for inputs
- Role-based selectors

#### 3. Low Priority (Fallback)
- Generic class patterns
- Text-based selectors
- XPath selectors
- Position-based selectors

### Semantic Element Types

#### Authentication Elements
- `username_field`: Input field for username/email
- `password_field`: Input field for password
- `login_button`: Button to submit login form
- `logout_button`: Button/link to logout

#### Navigation Elements
- `user_display`: Element showing current user name
- `dashboard_content`: Main dashboard/home page content
- `navigation_menu`: Main navigation menu

#### Validation Elements
- `error_message`: Error/validation messages
- `success_message`: Success confirmation messages
- `validation_message`: Field-level validation messages

### Implementation Architecture

#### 1. LocatorStrategy Class
```python
class LocatorStrategy:
    def __init__(self, page):
        self.page = page
        self.locator_map = self._build_locator_map()
    
    def find_element(self, semantic_type: str, timeout: int = 5000):
        """Find element using priority-based fallback"""
        
    def is_visible(self, semantic_type: str, timeout: int = 5000):
        """Check if element is visible using fallback"""
        
    def click(self, semantic_type: str, timeout: int = 5000):
        """Click element using fallback"""
        
    def fill(self, semantic_type: str, value: str, timeout: int = 5000):
        """Fill element using fallback"""
```

#### 2. Locator Map Structure
```python
LOCATOR_MAP = {
    "username_field": [
        # High priority
        "[data-testid*='username']",
        "#username",
        "input[name='username']",
        # Medium priority
        "input[type='text'][placeholder*='username' i]",
        "input[type='email']",
        ".username-input",
        # Low priority
        "input[type='text']:first-of-type",
        "//input[contains(@placeholder, 'username')]"
    ],
    "password_field": [
        # High priority
        "[data-testid*='password']",
        "#password",
        "input[name='password']",
        # Medium priority
        "input[type='password']",
        ".password-input",
        # Low priority
        "//input[@type='password']"
    ],
    "login_button": [
        # High priority
        "[data-testid*='login']",
        "#login-button",
        "button[name='login']",
        # Medium priority
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Login')",
        "button:has-text('Sign in')",
        # Low priority
        ".login-btn",
        ".btn-login",
        "//button[contains(text(), 'Login')]"
    ]
}
```

#### 3. Enhanced Page Objects
```python
class EnhancedLoginPage:
    def __init__(self, page):
        self.page = page
        self.locator_strategy = LocatorStrategy(page)
    
    def fill_username(self, username: str):
        self.locator_strategy.fill("username_field", username)
    
    def fill_password(self, password: str):
        self.locator_strategy.fill("password_field", password)
    
    def click_login(self):
        self.locator_strategy.click("login_button")
```

#### 4. Enhanced Test Generation
```python
# Instead of invalid comma-separated selectors:
# assert page.locator("[data-testid*='user'], [class*='user']").first.is_visible()

# Use priority-based approach:
# assert locator_strategy.is_visible("user_display")
```

### Benefits

1. **Playwright Compatibility**: All selectors use valid Playwright syntax
2. **Automatic Fallback**: Tests continue working even if primary selectors change
3. **Application Agnostic**: Generic selectors work across different applications
4. **Maintainable**: Centralized locator management
5. **Robust**: Multiple fallback options reduce test flakiness
6. **Extensible**: Easy to add new semantic types and selectors

### Migration Strategy

1. **Phase 1**: Implement LocatorStrategy class
2. **Phase 2**: Update test generation to use semantic types
3. **Phase 3**: Enhance page objects with LocatorStrategy
4. **Phase 4**: Update existing tests to use new approach
5. **Phase 5**: Add comprehensive locator map for common UI patterns

### Testing Strategy

1. Test with multiple web applications to validate application-agnostic approach
2. Verify fallback mechanism works when primary selectors fail
3. Performance testing to ensure fallback doesn't significantly slow down tests
4. Validate that all semantic types have appropriate fallback selectors

## Next Steps

1. Implement the LocatorStrategy class
2. Update test_creation_agent.py to use semantic types instead of comma-separated selectors
3. Enhance page objects to use LocatorStrategy
4. Test the implementation with the existing workflow
5. Validate with multiple applications

