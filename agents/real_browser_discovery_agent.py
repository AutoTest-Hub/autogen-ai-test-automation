"""
Real Browser Discovery Agent
===========================
This agent uses actual browser automation to discover real elements
on web pages for accurate selector generation.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

from agents.base_agent import BaseTestAgent
from config.settings import AgentRole

# Setup logger
logger = logging.getLogger(__name__)

class RealBrowserDiscoveryAgent(BaseTestAgent):
    """Agent that uses real browser automation to discover page elements"""
    
    def __init__(self, local_ai_provider=None):
        super().__init__(
            role=AgentRole.DISCOVERY,
            name="RealBrowserDiscoveryAgent",
            system_message="You are a Real Browser Discovery Agent that uses browser automation to analyze web applications and discover actual DOM elements for test automation.",
            local_ai_provider=local_ai_provider
        )
        
        # Work directory for saving artifacts
        self.work_dir = Path(f"./work_dir/{self.name}")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Screenshots directory
        self.screenshots_dir = Path("./screenshots")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Register agent functions
        self.register_function(self._discover_page_elements, "Discover real elements on a specific page using browser automation")
        self.register_function(self._analyze_application, "Analyze a web application using real browser automation")
        self.register_function(self._generate_element_selectors, "Generate accurate element selectors using browser inspection")
        self.register_function(self._map_user_workflows, "Map user workflows using real browser interaction")
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task assigned to this agent"""
        task_type = task_data.get("task_type", "discover_page_elements")
        
        if task_type == "discover_page_elements":
            return await self._discover_page_elements(task_data)
        elif task_type == "analyze_application":
            return await self._analyze_application(task_data)
        elif task_type == "generate_element_selectors":
            return await self._generate_element_selectors(task_data)
        elif task_type == "map_user_workflows":
            return await self._map_user_workflows(task_data)
        else:
            return {
                "status": "error",
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _discover_page_elements(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Discover real elements on a specific page using browser automation"""
        self.logger.info("🔍 Starting real browser element discovery")
        
        try:
            page_url = task_data.get("page_url", "")
            element_types = task_data.get("element_types", ["inputs", "buttons", "links", "forms"])
            
            if not page_url:
                return {
                    "status": "error",
                    "error": "No page URL provided"
                }
            
            # Use Playwright for browser automation
            from playwright.async_api import async_playwright
            
            self.logger.info(f"🌐 Launching browser to analyze {page_url}")
            
            async with async_playwright() as playwright:
                # Launch browser
                browser = await playwright.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to the page
                await page.goto(page_url, wait_until="networkidle")
                
                # Take a screenshot for reference
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = str(self.screenshots_dir / f"discovery_{timestamp}.png")
                await page.screenshot(path=screenshot_path)
                
                # Discover elements based on requested types
                discovered_elements = {}
                
                # Inputs discovery
                if "inputs" in element_types:
                    inputs = await page.evaluate("""() => {
                        const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
                        return inputs.map(input => {
                            return {
                                tag: input.tagName.toLowerCase(),
                                type: input.type || 'text',
                                id: input.id,
                                name: input.name,
                                placeholder: input.placeholder,
                                className: input.className,
                                xpath: getXPath(input),
                                css: getOptimalSelector(input)
                            };
                        });
                        
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
                            
                            // Try with classes if available
                            if (element.className) {
                                const classes = element.className.split(' ')
                                    .filter(c => c && !c.includes(':') && !c.startsWith('ng-') && !c.startsWith('_'));
                                if (classes.length > 0) {
                                    return `.${classes[0]}`;
                                }
                            }
                            
                            // Fallback to attribute selectors
                            if (element.placeholder) return `[placeholder="${element.placeholder}"]`;
                            
                            // Last resort: position-based selector
                            let parent = element.parentNode;
                            let tag = element.tagName.toLowerCase();
                            let nth = Array.from(parent.children)
                                .filter(child => child.tagName.toLowerCase() === tag)
                                .indexOf(element) + 1;
                            return `${parent.tagName.toLowerCase()} > ${tag}:nth-child(${nth})`;
                        }
                    }""")
                    
                    discovered_elements["inputs"] = inputs
                
                # Buttons discovery
                if "buttons" in element_types:
                    buttons = await page.evaluate("""() => {
                        const buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"], a.btn, .button, [role="button"]'));
                        return buttons.map(button => {
                            return {
                                tag: button.tagName.toLowerCase(),
                                type: button.type || '',
                                id: button.id,
                                name: button.name,
                                text: button.innerText || button.value,
                                className: button.className,
                                xpath: getXPath(button),
                                css: getOptimalSelector(button)
                            };
                        });
                        
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
                            
                            // Try with text content for buttons
                            const text = element.innerText || element.value;
                            if (text && text.length < 25) {
                                return `${element.tagName.toLowerCase()}:has-text("${text.trim()}")`;
                            }
                            
                            if (element.name) return `[name="${element.name}"]`;
                            
                            // Try with classes if available
                            if (element.className) {
                                const classes = element.className.split(' ')
                                    .filter(c => c && !c.includes(':') && !c.startsWith('ng-') && !c.startsWith('_'));
                                if (classes.length > 0) {
                                    return `.${classes[0]}`;
                                }
                            }
                            
                            // Last resort: position-based selector
                            let parent = element.parentNode;
                            let tag = element.tagName.toLowerCase();
                            let nth = Array.from(parent.children)
                                .filter(child => child.tagName.toLowerCase() === tag)
                                .indexOf(element) + 1;
                            return `${parent.tagName.toLowerCase()} > ${tag}:nth-child(${nth})`;
                        }
                    }""")
                    
                    discovered_elements["buttons"] = buttons
                
                # Links discovery
                if "links" in element_types:
                    links = await page.evaluate("""() => {
                        const links = Array.from(document.querySelectorAll('a:not(.btn):not([role="button"])'));
                        return links.map(link => {
                            return {
                                tag: 'a',
                                href: link.href,
                                text: link.innerText,
                                id: link.id,
                                className: link.className,
                                xpath: getXPath(link),
                                css: getOptimalSelector(link)
                            };
                        });
                        
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
                            
                            // Try with text content for links
                            const text = element.innerText;
                            if (text && text.length < 25) {
                                return `a:has-text("${text.trim()}")`;
                            }
                            
                            if (element.name) return `[name="${element.name}"]`;
                            
                            // Try with classes if available
                            if (element.className) {
                                const classes = element.className.split(' ')
                                    .filter(c => c && !c.includes(':') && !c.startsWith('ng-') && !c.startsWith('_'));
                                if (classes.length > 0) {
                                    return `.${classes[0]}`;
                                }
                            }
                            
                            // Try with href
                            if (element.href) {
                                const url = new URL(element.href);
                                const path = url.pathname;
                                if (path && path !== '/') {
                                    return `a[href*="${path}"]`;
                                }
                            }
                            
                            // Last resort: position-based selector
                            let parent = element.parentNode;
                            let nth = Array.from(parent.children)
                                .filter(child => child.tagName.toLowerCase() === 'a')
                                .indexOf(element) + 1;
                            return `${parent.tagName.toLowerCase()} > a:nth-child(${nth})`;
                        }
                    }""")
                    
                    discovered_elements["links"] = links
                
                # Forms discovery
                if "forms" in element_types:
                    forms = await page.evaluate("""() => {
                        const forms = Array.from(document.querySelectorAll('form'));
                        return forms.map(form => {
                            const formInputs = Array.from(form.querySelectorAll('input, select, textarea'))
                                .map(input => ({
                                    name: input.name,
                                    type: input.type || input.tagName.toLowerCase(),
                                    id: input.id
                                }));
                                
                            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
                            
                            return {
                                id: form.id,
                                name: form.name,
                                action: form.action,
                                method: form.method,
                                className: form.className,
                                inputs: formInputs,
                                submitButton: submitButton ? {
                                    id: submitButton.id,
                                    text: submitButton.innerText || submitButton.value
                                } : null,
                                xpath: getXPath(form),
                                css: getOptimalSelector(form)
                            };
                        });
                        
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
                            if (element.name) return `form[name="${element.name}"]`;
                            
                            // Try with classes if available
                            if (element.className) {
                                const classes = element.className.split(' ')
                                    .filter(c => c && !c.includes(':') && !c.startsWith('ng-') && !c.startsWith('_'));
                                if (classes.length > 0) {
                                    return `.${classes[0]}`;
                                }
                            }
                            
                            // Try with action
                            if (element.action) {
                                const url = new URL(element.action);
                                const path = url.pathname;
                                if (path && path !== '/') {
                                    return `form[action*="${path}"]`;
                                }
                            }
                            
                            // Last resort: nth-form
                            const forms = Array.from(document.querySelectorAll('form'));
                            const index = forms.indexOf(element) + 1;
                            return `form:nth-of-type(${index})`;
                        }
                    }""")
                    
                    discovered_elements["forms"] = forms
                
                # Close browser
                await browser.close()
                
                # Save discovery results to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                results_file = self.work_dir / f"page_elements_{timestamp}.json"
                
                with open(results_file, 'w') as f:
                    json.dump({
                        "page_url": page_url,
                        "timestamp": timestamp,
                        "elements": discovered_elements,
                        "screenshot": screenshot_path
                    }, f, indent=2)
                
                # Count total elements
                total_elements = sum(len(elements) for elements in discovered_elements.values())
                
                self.logger.info(f"🎯 Discovered {total_elements} real elements on {page_url}")
                
                return {
                    "status": "completed",
                    "page_url": page_url,
                    "elements": discovered_elements,
                    "total_elements": total_elements,
                    "screenshot": screenshot_path,
                    "results_file": str(results_file)
                }
            
        except Exception as e:
            self.logger.error(f"❌ Real browser element discovery failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _analyze_application(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a web application using real browser automation"""
        self.logger.info("🔍 Starting real browser application analysis")
        
        try:
            application_url = task_data.get("application_url", "")
            analysis_depth = task_data.get("analysis_depth", "basic")  # basic, medium, deep
            
            if not application_url:
                return {
                    "status": "error",
                    "error": "No application URL provided"
                }
            
            # Use Playwright for browser automation
            from playwright.async_api import async_playwright
            
            self.logger.info(f"🌐 Launching browser to analyze {application_url}")
            
            async with async_playwright() as playwright:
                # Launch browser
                browser = await playwright.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to the application
                await page.goto(application_url, wait_until="networkidle")
                
                # Take a screenshot for reference
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = str(self.screenshots_dir / f"app_analysis_{timestamp}.png")
                await page.screenshot(path=screenshot_path)
                
                # Discover main pages
                main_pages = await self._discover_main_pages(page)
                
                # Analyze key elements on main page
                main_page_elements = await self._analyze_page_elements_with_browser(page)
                
                # Discover navigation structure
                navigation = await page.evaluate("""() => {
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
                                    selector: link.id ? `#${link.id}` : `.${link.className.split(' ')[0]}`
                                });
                            }
                        });
                    });
                    
                    return navLinks;
                }""")
                
                # Close browser
                await browser.close()
                
                # Prepare analysis result
                analysis_result = {
                    "application_url": application_url,
                    "analysis_depth": analysis_depth,
                    "discovered_pages": main_pages,
                    "main_page_elements": main_page_elements,
                    "navigation": navigation,
                    "screenshot": screenshot_path,
                    "analysis_timestamp": datetime.now().isoformat()
                }
                
                # Save analysis results to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                results_file = self.work_dir / f"app_analysis_{timestamp}.json"
                
                with open(results_file, 'w') as f:
                    json.dump(analysis_result, f, indent=2)
                
                self.logger.info(f"🔍 Application analysis completed for {application_url}")
                
                return {
                    "status": "completed",
                    "application_url": application_url,
                    "analysis_result": analysis_result,
                    "results_file": str(results_file)
                }
            
        except Exception as e:
            self.logger.error(f"❌ Real browser application analysis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _discover_main_pages(self, page) -> List[Dict[str, Any]]:
        """Discover main pages of the application using browser automation"""
        # Extract links from the page
        links = await page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a'));
            return links
                .filter(link => {
                    // Filter out non-http links, anchors, etc.
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
        }""")
        
        # Filter and deduplicate links
        seen_urls = set()
        main_pages = []
        
        for link in links:
            url = link["url"]
            # Skip if we've seen this URL already
            if url in seen_urls:
                continue
                
            seen_urls.add(url)
            main_pages.append({
                "url": url,
                "name": link["name"],
                "text": link["text"]
            })
            
            # Limit to 10 pages for performance
            if len(main_pages) >= 10:
                break
        
        return main_pages
    
    async def _analyze_page_elements_with_browser(self, page) -> Dict[str, Any]:
        """Analyze elements on the current page using browser automation"""
        # Extract key elements from the page
        elements = await page.evaluate("""() => {
            const result = {};
            
            // Find forms
            result.forms = Array.from(document.querySelectorAll('form')).map(form => {
                return {
                    id: form.id,
                    name: form.name,
                    action: form.action,
                    method: form.method,
                    selector: form.id ? `#${form.id}` : `form[action="${form.action}"]`
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
        }""")
        
        return elements
    
    async def _generate_element_selectors(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate accurate element selectors using browser inspection"""
        self.logger.info("🎯 Generating accurate element selectors")
        
        try:
            page_url = task_data.get("page_url", "")
            element_descriptions = task_data.get("element_descriptions", [])
            
            if not page_url or not element_descriptions:
                return {
                    "status": "error",
                    "error": "Page URL and element descriptions required"
                }
            
            # Use Playwright for browser automation
            from playwright.async_api import async_playwright
            
            self.logger.info(f"🌐 Launching browser to analyze {page_url}")
            
            async with async_playwright() as playwright:
                # Launch browser
                browser = await playwright.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to the page
                await page.goto(page_url, wait_until="networkidle")
                
                # Take a screenshot for reference
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = str(self.screenshots_dir / f"selector_gen_{timestamp}.png")
                await page.screenshot(path=screenshot_path)
                
                # Generate selectors for each element description
                generated_selectors = []
                
                for description in element_descriptions:
                    # Try to find elements matching the description
                    selectors = await self._find_matching_selectors(page, description)
                    
                    if selectors:
                        generated_selectors.append({
                            "description": description,
                            "selectors": selectors,
                            "recommended": selectors[0]  # Highest priority selector
                        })
                    else:
                        # Fallback to generic selectors if no match found
                        generic_selectors = [
                            {"type": "css", "value": f"[data-testid='{description.lower().replace(' ', '-')}']", "priority": "high"},
                            {"type": "css", "value": f".{description.lower().replace(' ', '-')}", "priority": "medium"},
                            {"type": "xpath", "value": f"//*[contains(text(), '{description}')]", "priority": "low"}
                        ]
                        
                        generated_selectors.append({
                            "description": description,
                            "selectors": generic_selectors,
                            "recommended": generic_selectors[0],
                            "note": "Element not found, using generic selectors"
                        })
                
                # Close browser
                await browser.close()
                
                # Save selector results to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                results_file = self.work_dir / f"selectors_{timestamp}.json"
                
                with open(results_file, 'w') as f:
                    json.dump({
                        "page_url": page_url,
                        "timestamp": timestamp,
                        "generated_selectors": generated_selectors,
                        "screenshot": screenshot_path
                    }, f, indent=2)
                
                self.logger.info(f"🎯 Generated {len(generated_selectors)} element selectors for {page_url}")
                
                return {
                    "status": "completed",
                    "page_url": page_url,
                    "generated_selectors": generated_selectors,
                    "total_elements": len(generated_selectors),
                    "screenshot": screenshot_path,
                    "results_file": str(results_file)
                }
            
        except Exception as e:
            self.logger.error(f"❌ Element selector generation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _find_matching_selectors(self, page, description: str) -> List[Dict[str, Any]]:
        """Find elements matching the description and generate selectors"""
        # Convert description to lowercase for case-insensitive matching
        desc_lower = description.lower()
        
        # Define search patterns based on common element types
        search_patterns = []
        
        # Login-related elements
        if "login" in desc_lower or "sign in" in desc_lower:
            if "button" in desc_lower:
                search_patterns.extend([
                    "button:has-text(/login|sign in/i)",
                    "input[type='submit'][value*='Login' i]",
                    "[data-testid*='login' i]",
                    "#login, .login-btn, .signin-btn"
                ])
            elif "form" in desc_lower:
                search_patterns.extend([
                    "form[action*='login' i]",
                    "form[id*='login' i]",
                    "form[name*='login' i]"
                ])
        
        # Username/email input
        if "username" in desc_lower or "email" in desc_lower:
            search_patterns.extend([
                "input[type='text'][name*='user' i], input[type='text'][name*='email' i]",
                "input[type='email']",
                "input[placeholder*='email' i], input[placeholder*='username' i]",
                "#username, #email, [name='username'], [name='email']"
            ])
        
        # Password input
        if "password" in desc_lower:
            search_patterns.extend([
                "input[type='password']",
                "#password, [name='password']",
                "input[placeholder*='password' i]"
            ])
        
        # Search-related elements
        if "search" in desc_lower:
            search_patterns.extend([
                "input[type='search']",
                "input[placeholder*='search' i]",
                "#search, .search-input, [name*='search' i]"
            ])
        
        # Generic button with text
        if "button" in desc_lower:
            # Extract the button text (remove "button" word)
            button_text = desc_lower.replace("button", "").strip()
            if button_text:
                search_patterns.append(f"button:has-text('{button_text}')")
                search_patterns.append(f"input[type='button'][value*='{button_text}' i]")
                search_patterns.append(f"a:has-text('{button_text}')")
        
        # Generic link with text
        if "link" in desc_lower:
            # Extract the link text (remove "link" word)
            link_text = desc_lower.replace("link", "").strip()
            if link_text:
                search_patterns.append(f"a:has-text('{link_text}')")
        
        # If no specific patterns, use generic text search
        if not search_patterns:
            # Remove common words like "the", "a", "an", etc.
            clean_desc = desc_lower.replace("the ", "").replace("a ", "").replace("an ", "")
            search_patterns.extend([
                f"*:has-text('{clean_desc}')",
                f"[placeholder*='{clean_desc}' i]",
                f"[aria-label*='{clean_desc}' i]",
                f"[title*='{clean_desc}' i]"
            ])
        
        # Try each search pattern and collect matching elements
        selectors = []
        
        for pattern in search_patterns:
            try:
                # Check if selector matches any elements
                count = await page.evaluate(f"document.querySelectorAll('{pattern}').length")
                
                if count > 0:
                    # Get more details about the matched elements
                    elements = await page.evaluate(f"""() => {{
                        const elements = Array.from(document.querySelectorAll('{pattern}'));
                        return elements.map(el => {{
                            return {{
                                tag: el.tagName.toLowerCase(),
                                id: el.id,
                                name: el.name,
                                type: el.type,
                                text: el.innerText || el.value || ''
                            }};
                        }});
                    }}""")
                    
                    # Add the selector to our list
                    selectors.append({
                        "type": "css",
                        "value": pattern,
                        "priority": "high" if count == 1 else "medium",
                        "matches": count,
                        "elements": elements
                    })
                    
                    # If we found an exact match (single element), also generate alternative selectors
                    if count == 1:
                        element = elements[0]
                        
                        # ID-based selector (highest priority)
                        if element.get("id"):
                            selectors.append({
                                "type": "css",
                                "value": f"#{element['id']}",
                                "priority": "highest",
                                "matches": 1
                            })
                        
                        # Name-based selector
                        if element.get("name"):
                            selectors.append({
                                "type": "css",
                                "value": f"[name='{element['name']}']",
                                "priority": "high",
                                "matches": 1
                            })
                        
                        # XPath with text
                        if element.get("text") and len(element["text"]) < 30:
                            selectors.append({
                                "type": "xpath",
                                "value": f"//{element['tag']}[contains(text(), '{element['text']}')]",
                                "priority": "medium",
                                "matches": 1
                            })
                
                # Limit to 5 selectors per element
                if len(selectors) >= 5:
                    break
                    
            except Exception as e:
                self.logger.warning(f"Error with selector pattern '{pattern}': {str(e)}")
        
        # Sort selectors by priority
        priority_order = {"highest": 0, "high": 1, "medium": 2, "low": 3}
        selectors.sort(key=lambda s: priority_order.get(s.get("priority", "low"), 99))
        
        return selectors
    
    async def _map_user_workflows(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map user workflows using real browser interaction"""
        self.logger.info("🔄 Mapping user workflows with real browser")
        
        try:
            application_url = task_data.get("application_url", "")
            workflow_types = task_data.get("workflow_types", ["authentication", "shopping", "browsing"])
            
            if not application_url:
                return {
                    "status": "error",
                    "error": "No application URL provided"
                }
            
            # Use Playwright for browser automation
            from playwright.async_api import async_playwright
            
            self.logger.info(f"🌐 Launching browser to analyze {application_url}")
            
            async with async_playwright() as playwright:
                # Launch browser
                browser = await playwright.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to the application
                await page.goto(application_url, wait_until="networkidle")
                
                # Take a screenshot for reference
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = str(self.screenshots_dir / f"workflow_map_{timestamp}.png")
                await page.screenshot(path=screenshot_path)
                
                # Discover main pages
                main_pages = await self._discover_main_pages(page)
                
                # Identify workflows based on page structure and links
                workflows = []
                
                # Authentication workflow detection
                if "authentication" in workflow_types:
                    # Look for login/register links
                    login_links = await page.evaluate("""() => {
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
                    }""")
                    
                    if login_links:
                        auth_workflow = {
                            "name": "User Authentication Workflow",
                            "type": "authentication",
                            "priority": "high",
                            "description": "User login and account access",
                            "entry_points": login_links,
                            "steps": [
                                {"action": "navigate", "target": login_links[0]["url"], "description": "Go to login page"}
                            ],
                            "test_scenarios": [
                                "Successful login with valid credentials",
                                "Failed login with invalid credentials",
                                "Password reset functionality",
                                "New user registration"
                            ]
                        }
                        
                        # Try to navigate to login page and analyze form
                        try:
                            await page.goto(login_links[0]["url"], wait_until="networkidle")
                            
                            # Check for login form elements
                            form_elements = await page.evaluate("""() => {
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
                                        selector: submitButton.id ? `#${submitButton.id}` : `button[type="submit"]`
                                    } : null
                                };
                            }""")
                            
                            if form_elements and form_elements.get("inputs"):
                                # Add form interaction steps
                                for input_el in form_elements["inputs"]:
                                    if input_el["type"] == "text" or input_el["type"] == "email":
                                        auth_workflow["steps"].append({
                                            "action": "input", 
                                            "target": input_el["selector"], 
                                            "description": "Enter username/email",
                                            "selector": input_el["selector"]
                                        })
                                    elif input_el["type"] == "password":
                                        auth_workflow["steps"].append({
                                            "action": "input", 
                                            "target": input_el["selector"], 
                                            "description": "Enter password",
                                            "selector": input_el["selector"]
                                        })
                                
                                if form_elements.get("submitButton"):
                                    auth_workflow["steps"].append({
                                        "action": "click", 
                                        "target": form_elements["submitButton"]["selector"], 
                                        "description": "Submit login form",
                                        "selector": form_elements["submitButton"]["selector"]
                                    })
                        except Exception as e:
                            self.logger.warning(f"Error analyzing login page: {str(e)}")
                        
                        workflows.append(auth_workflow)
                
                # Shopping/browsing workflow detection for e-commerce
                if "shopping" in workflow_types or "browsing" in workflow_types:
                    # Look for product links, categories, cart
                    product_elements = await page.evaluate("""() => {
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
                    }""")
                    
                    if product_elements["hasProductGrid"] or product_elements["productCount"] > 0:
                        browsing_workflow = {
                            "name": "Product Browsing Workflow",
                            "type": "browsing",
                            "priority": "high",
                            "description": "Browsing products and categories",
                            "steps": [
                                {"action": "navigate", "target": application_url, "description": "Start at home page"}
                            ],
                            "test_scenarios": [
                                "Browse product categories",
                                "Search for specific products",
                                "Filter products by attributes",
                                "Sort products by price/relevance"
                            ]
                        }
                        
                        # Add category navigation if available
                        if product_elements["categoryLinks"]:
                            browsing_workflow["steps"].append({
                                "action": "click", 
                                "target": product_elements["categoryLinks"][0]["selector"], 
                                "description": "Navigate to product category",
                                "selector": product_elements["categoryLinks"][0]["selector"]
                            })
                        
                        workflows.append(browsing_workflow)
                    
                    if product_elements["cartLinks"]:
                        shopping_workflow = {
                            "name": "Shopping Cart Workflow",
                            "type": "shopping",
                            "priority": "high",
                            "description": "Adding products to cart and checkout process",
                            "entry_points": product_elements["cartLinks"],
                            "steps": [
                                {"action": "navigate", "target": application_url, "description": "Start at home page"},
                                {"action": "click", "target": ".product-item", "description": "Select a product"},
                                {"action": "click", "target": ".add-to-cart", "description": "Add product to cart"},
                                {"action": "click", "target": product_elements["cartLinks"][0]["selector"], "description": "Go to shopping cart"}
                            ],
                            "test_scenarios": [
                                "Add product to cart",
                                "Update product quantity",
                                "Remove product from cart",
                                "Complete checkout process"
                            ]
                        }
                        
                        workflows.append(shopping_workflow)
                
                # Close browser
                await browser.close()
                
                # Save workflow results to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                results_file = self.work_dir / f"workflows_{timestamp}.json"
                
                with open(results_file, 'w') as f:
                    json.dump({
                        "application_url": application_url,
                        "timestamp": timestamp,
                        "workflows": workflows,
                        "screenshot": screenshot_path
                    }, f, indent=2)
                
                self.logger.info(f"🔄 Identified {len(workflows)} user workflows for {application_url}")
                
                return {
                    "status": "completed",
                    "application_url": application_url,
                    "workflows": workflows,
                    "total_workflows": len(workflows),
                    "screenshot": screenshot_path,
                    "results_file": str(results_file)
                }
            
        except Exception as e:
            self.logger.error(f"❌ Workflow mapping failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return [
            "real_browser_discovery",
            "element_detection",
            "selector_generation",
            "workflow_mapping",
            "application_analysis"
        ]

