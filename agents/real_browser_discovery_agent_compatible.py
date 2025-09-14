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
        self.work_dir = Path("./work_dir/{}".format(self.name))
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
                "error": "Unknown task type: {}".format(task_type)
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
            
            self.logger.info("🌐 Launching browser to analyze {}".format(page_url))
            
            async with async_playwright() as playwright:
                # Launch browser
                browser = await playwright.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to the page
                await page.goto(page_url, wait_until="networkidle")
                
                # Take a screenshot for reference
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = str(self.screenshots_dir / "discovery_{}.png".format(timestamp))
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
                                action: form.action,
                                method: form.method,
                                inputs: formInputs,
                                submitButton: submitButton ? {
                                    id: submitButton.id,
                                    text: submitButton.innerText || submitButton.value,
                                    type: submitButton.type
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
                            if (element.name) return `[name="${element.name}"]`;
                            
                            // Try with action for forms
                            if (element.tagName.toLowerCase() === 'form' && element.action) {
                                return `form[action="${element.action}"]`;
                            }
                            
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
                    
                    discovered_elements["forms"] = forms
                
                # Close browser
                await browser.close()
                
                # Calculate total elements
                total_elements = sum(len(elements) for elements in discovered_elements.values())
                
                # Save discovery results to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                results_file = self.work_dir / "discovery_results_{}.json".format(timestamp)
                
                with open(results_file, 'w') as f:
                    json.dump({
                        "page_url": page_url,
                        "timestamp": timestamp,
                        "elements": discovered_elements,
                        "total_elements": total_elements,
                        "screenshot": screenshot_path
                    }, f, indent=2)
                
                self.logger.info("🔍 Discovered {} elements on {}".format(total_elements, page_url))
                
                return {
                    "status": "completed",
                    "page_url": page_url,
                    "elements": discovered_elements,
                    "total_elements": total_elements,
                    "screenshot": screenshot_path,
                    "results_file": str(results_file)
                }
            
        except Exception as e:
            self.logger.error("❌ Real browser element discovery failed: {}".format(str(e)))
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
            
            self.logger.info("🌐 Launching browser to analyze {}".format(application_url))
            
            async with async_playwright() as playwright:
                # Launch browser
                browser = await playwright.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to the application
                await page.goto(application_url, wait_until="networkidle")
                
                # Take a screenshot for reference
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = str(self.screenshots_dir / "app_analysis_{}.png".format(timestamp))
                await page.screenshot(path=screenshot_path)
                
                # Analyze application structure
                analysis_result = {}
                
                # Get page title and metadata
                title = await page.title()
                
                analysis_result["title"] = title
                analysis_result["url"] = application_url
                analysis_result["timestamp"] = timestamp
                
                # Discover main pages
                self.logger.info("🔍 Discovering main pages")
                discovered_pages = await self._discover_main_pages(page)
                analysis_result["discovered_pages"] = discovered_pages
                
                # Analyze current page elements
                self.logger.info("🔍 Analyzing page elements")
                page_elements = await self._analyze_page_elements_with_browser(page)
                analysis_result["main_page_elements"] = page_elements
                
                # For medium or deep analysis, visit some of the discovered pages
                if analysis_depth in ["medium", "deep"]:
                    self.logger.info("🔍 Performing {} analysis on discovered pages".format(analysis_depth))
                    
                    # Limit the number of pages to visit based on depth
                    max_pages = 3 if analysis_depth == "medium" else 5
                    pages_to_visit = discovered_pages[:max_pages]
                    
                    # Visit each page and analyze elements
                    page_analyses = {}
                    for page_info in pages_to_visit:
                        page_url = page_info["url"]
                        page_name = page_info["name"]
                        
                        try:
                            # Navigate to the page
                            await page.goto(page_url, wait_until="networkidle")
                            
                            # Take a screenshot
                            page_screenshot = str(self.screenshots_dir / "page_{}_{}.png".format(
                                page_name.lower().replace(" ", "_"), timestamp
                            ))
                            await page.screenshot(path=page_screenshot)
                            
                            # Analyze page elements
                            elements = await self._analyze_page_elements_with_browser(page)
                            
                            page_analyses[page_name] = {
                                "url": page_url,
                                "elements": elements,
                                "screenshot": page_screenshot
                            }
                            
                        except Exception as e:
                            self.logger.warning("⚠️ Error analyzing page {}: {}".format(page_url, str(e)))
                    
                    analysis_result["page_analyses"] = page_analyses
                
                # Close browser
                await browser.close()
                
                # Save analysis results to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                results_file = self.work_dir / "app_analysis_{}.json".format(timestamp)
                
                with open(results_file, 'w') as f:
                    json.dump(analysis_result, f, indent=2)
                
                self.logger.info("🔍 Application analysis completed for {}".format(application_url))
                
                return {
                    "status": "completed",
                    "application_url": application_url,
                    "analysis_result": analysis_result,
                    "results_file": str(results_file)
                }
            
        except Exception as e:
            self.logger.error("❌ Real browser application analysis failed: {}".format(str(e)))
            return {
                "status": "error",
                "error": str(e)
            }
    
    # Additional methods would be implemented similarly, replacing f-strings with .format()

