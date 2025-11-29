"""
JavaScript Discovery Scripts for Browser-Based Element Discovery

This module contains reusable JavaScript code snippets used by the
RealBrowserDiscoveryAgent for DOM element discovery and selector generation.
Centralizing these scripts reduces code duplication and makes maintenance easier.
"""

# Common utility functions used in all discovery operations
JS_UTILITY_FUNCTIONS = """
function getXPath(element) {
    if (element.id) return `//*[@id="${element.id}"]`;

    const paths = [];
    while (element !== document.documentElement) {
        let index = 0;
        let sibling = element;
        while (sibling) {
            if (sibling.nodeName === element.nodeName) index++;
            sibling = sibling.previousElementSibling;
        }
        const tagName = element.nodeName.toLowerCase();
        const pathIndex = (index > 1) ? `[${index}]` : '';
        paths.unshift(`${tagName}${pathIndex}`);
        element = element.parentNode;
    }
    return `//${paths.join('/')}`;
}

function getOptimalSelector(element) {
    if (element.id) return `#${element.id}`;
    if (element.name) return `[name="${element.name}"]`;

    // Try with text content for buttons/links
    const text = element.innerText || element.value;
    if (text && text.length < 25 && text.trim()) {
        const tag = element.tagName.toLowerCase();
        if (tag === 'button' || tag === 'a') {
            return `${tag}:has-text("${text.trim()}")`;
        }
    }

    // Try with classes if available
    if (element.className && typeof element.className === 'string') {
        const classes = element.className.split(' ')
            .filter(c => c && !c.includes(':') && !c.startsWith('ng-') && !c.startsWith('_'));
        if (classes.length > 0) {
            return `.${classes[0]}`;
        }
    }

    // Try with placeholder
    if (element.placeholder) return `[placeholder="${element.placeholder}"]`;

    // Last resort: position-based selector
    let parent = element.parentNode;
    if (parent) {
        let tag = element.tagName.toLowerCase();
        let nth = Array.from(parent.children)
            .filter(child => child.tagName.toLowerCase() === tag)
            .indexOf(element) + 1;
        return `${parent.tagName.toLowerCase()} > ${tag}:nth-child(${nth})`;
    }

    return element.tagName.toLowerCase();
}
"""

# Script to discover input elements
JS_DISCOVER_INPUTS = f"""() => {{
    {JS_UTILITY_FUNCTIONS}

    const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
    return inputs.map(input => {{
        return {{
            tag: input.tagName.toLowerCase(),
            type: input.type || 'text',
            id: input.id,
            name: input.name,
            placeholder: input.placeholder,
            className: input.className,
            xpath: getXPath(input),
            css: getOptimalSelector(input)
        }};
    }});
}}"""

# Script to discover button elements
JS_DISCOVER_BUTTONS = f"""() => {{
    {JS_UTILITY_FUNCTIONS}

    const buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"], a.btn, .button, [role="button"]'));
    return buttons.map(button => {{
        return {{
            tag: button.tagName.toLowerCase(),
            type: button.type || '',
            id: button.id,
            name: button.name,
            text: button.innerText || button.value,
            className: button.className,
            xpath: getXPath(button),
            css: getOptimalSelector(button)
        }};
    }});
}}"""

# Script to discover link elements
JS_DISCOVER_LINKS = f"""() => {{
    {JS_UTILITY_FUNCTIONS}

    const links = Array.from(document.querySelectorAll('a:not(.btn):not([role="button"])'));
    return links.map(link => {{
        return {{
            tag: 'a',
            href: link.href,
            text: link.innerText,
            id: link.id,
            className: link.className,
            xpath: getXPath(link),
            css: getOptimalSelector(link)
        }};
    }});
}}"""

# Script to discover form elements
JS_DISCOVER_FORMS = f"""() => {{
    {JS_UTILITY_FUNCTIONS}

    const forms = Array.from(document.querySelectorAll('form'));
    return forms.map(form => {{
        const formInputs = Array.from(form.querySelectorAll('input, select, textarea'))
            .map(input => ({{
                name: input.name,
                type: input.type || input.tagName.toLowerCase(),
                id: input.id
            }}));

        const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');

        return {{
            id: form.id,
            name: form.name,
            action: form.action,
            method: form.method,
            className: form.className,
            inputs: formInputs,
            submitButton: submitButton ? {{
                id: submitButton.id,
                text: submitButton.innerText || submitButton.value
            }} : null,
            xpath: getXPath(form),
            css: getOptimalSelector(form)
        }};
    }});
}}"""

# Script to discover navigation elements
JS_DISCOVER_NAVIGATION = """() => {
    const navElements = Array.from(document.querySelectorAll('nav, [role="navigation"], .nav, .navbar, .menu, header a, footer a'));
    const navLinks = [];

    navElements.forEach(nav => {
        const links = Array.from(nav.querySelectorAll('a'));
        links.forEach(link => {
            if (link.href && !link.href.startsWith('javascript:') && !link.href.includes('#')) {
                navLinks.push({
                    text: link.innerText.trim(),
                    href: link.href,
                    id: link.id,
                    className: link.className,
                    selector: link.id ? `#${link.id}` : link.className ? `.${link.className.split(' ')[0]}` : ''
                });
            }
        });
    });

    return navLinks;
}"""

# Script to discover main pages/links
JS_DISCOVER_MAIN_PAGES = """() => {
    const links = Array.from(document.querySelectorAll('a'));
    return links
        .filter(link => {
            return link.href &&
                   link.href.startsWith('http') &&
                   !link.href.includes('#') &&
                   !link.href.startsWith('javascript:') &&
                   !link.href.includes('mailto:') &&
                   !link.href.includes('tel:');
        })
        .map(link => {
            return {
                url: link.href,
                text: link.innerText.trim(),
                name: link.innerText.trim() || new URL(link.href).pathname.split('/').pop() || 'page'
            };
        });
}"""

# Script to analyze page elements
JS_ANALYZE_PAGE_ELEMENTS = """() => {
    const result = {};

    // Find forms
    result.forms = Array.from(document.querySelectorAll('form')).map(form => {
        return {
            id: form.id,
            name: form.name,
            action: form.action,
            method: form.method,
            selector: form.id ? `#${form.id}` : form.action ? `form[action="${form.action}"]` : 'form'
        };
    });

    // Find inputs
    result.inputs = Array.from(document.querySelectorAll('input, textarea, select')).map(input => {
        return {
            type: input.type || input.tagName.toLowerCase(),
            id: input.id,
            name: input.name,
            placeholder: input.placeholder,
            selector: input.id ? `#${input.id}` : input.name ? `[name="${input.name}"]` : null
        };
    });

    // Find buttons
    result.buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]')).map(button => {
        return {
            type: button.type,
            id: button.id,
            text: button.innerText || button.value,
            selector: button.id ? `#${button.id}` : button.innerText ? `button:has-text("${button.innerText}")` : null
        };
    });

    return result;
}"""

# Script to discover login-related elements
JS_DISCOVER_LOGIN_ELEMENTS = """() => {
    const links = Array.from(document.querySelectorAll('a'));
    return links
        .filter(link => {
            const text = link.innerText.toLowerCase();
            return text.includes('login') ||
                   text.includes('sign in') ||
                   text.includes('register') ||
                   text.includes('sign up');
        })
        .map(link => {
            return {
                url: link.href,
                text: link.innerText.trim(),
                selector: link.id ? `#${link.id}` : `a:has-text("${link.innerText.trim()}")`
            };
        });
}"""

# Script to analyze login form
JS_ANALYZE_LOGIN_FORM = """() => {
    const form = document.querySelector('form');
    if (!form) return null;

    const inputs = Array.from(form.querySelectorAll('input'));
    const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');

    return {
        inputs: inputs.map(input => ({
            type: input.type,
            name: input.name,
            id: input.id,
            placeholder: input.placeholder,
            selector: input.id ? `#${input.id}` : `[name="${input.name}"]`
        })),
        submitButton: submitButton ? {
            text: submitButton.innerText || submitButton.value,
            selector: submitButton.id ? `#${submitButton.id}` : 'button[type="submit"]'
        } : null
    };
}"""

# Script to discover shopping/e-commerce elements
JS_DISCOVER_SHOPPING_ELEMENTS = """() => {
    // Check for product grid/list
    const productContainers = document.querySelectorAll('.products, .product-grid, .product-list, [class*="product-container"]');
    const productItems = document.querySelectorAll('.product, .product-item, [class*="product-card"]');

    // Check for cart elements
    const cartLinks = Array.from(document.querySelectorAll('a')).filter(a => {
        const text = a.innerText.toLowerCase();
        return text.includes('cart') || text.includes('basket') || text.includes('bag');
    });

    // Check for category navigation
    const categoryLinks = Array.from(document.querySelectorAll('nav a, .categories a, .category a'));

    return {
        hasProductGrid: productContainers.length > 0,
        productCount: productItems.length,
        cartLinks: cartLinks.map(link => ({
            url: link.href,
            text: link.innerText.trim(),
            selector: link.id ? `#${link.id}` : `a:has-text("${link.innerText.trim()}")`
        })),
        categoryLinks: categoryLinks.map(link => ({
            url: link.href,
            text: link.innerText.trim(),
            selector: link.id ? `#${link.id}` : `a:has-text("${link.innerText.trim()}")`
        }))
    };
}"""


def get_element_count_script(selector: str) -> str:
    """Generate a script to count elements matching a selector"""
    return f"document.querySelectorAll('{selector}').length"


def get_element_details_script(selector: str) -> str:
    """Generate a script to get details of elements matching a selector"""
    return f"""() => {{
        const elements = Array.from(document.querySelectorAll('{selector}'));
        return elements.map(el => {{
            return {{
                tag: el.tagName.toLowerCase(),
                id: el.id,
                name: el.name,
                type: el.type,
                text: el.innerText || el.value || ''
            }};
        }});
    }}"""
