#!/usr/bin/env python3
"""
Real Browser Discovery Agent
===================
This agent discovers elements on web pages using real browser automation.
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealBrowserDiscoveryAgent:
    """
    Real Browser Discovery Agent
    
    This agent discovers elements on web pages using real browser automation.
    """
    
    def __init__(self):
        """Initialize the real browser discovery agent"""
        self.logger = logging.getLogger(__name__)
        
        # Create work directory
        self.work_dir = Path("work_dir/RealDiscoveryIntegration")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Screenshots directory
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return [
            "real_browser_discovery",
            "element_detection",
            "selector_generation",
            "page_analysis",
            "workflow_mapping"
        ]
    
    async def discover_elements(self, url: str) -> Dict[str, Any]:
        """
        Discover elements on a web page
        
        Args:
            url: URL of the web page to analyze
            
        Returns:
            Dict[str, Any]: Discovery results
        """
        self.logger.info(f"Discovering elements on {url}")
        
        try:
            # Launch browser and navigate to URL
            async with async_playwright() as playwright:
                # Launch browser
                browser = await playwright.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to URL
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                
                # Take screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = self.screenshots_dir / f"discovery_{timestamp}.png"
                await page.screenshot(path=screenshot_path)
                
                # Get page title
                title = await page.title()
                
                # Extract page information
                page_info = {
                    "url": url,
                    "title": title,
                    "timestamp": timestamp
                }
                
                # Discover elements
                elements = await self._discover_page_elements(page)
                
                # Analyze page structure
                page_structure = await self._analyze_page_structure(page)
                
                # Close browser
                await context.close()
                await browser.close()
                
                # Create discovery results
                discovery_results = {
                    "application_url": url,
                    "timestamp": timestamp,
                    "pages": [
                        {
                            "name": title,
                            "url": url,
                            "elements": elements
                        }
                    ],
                    "elements": self._convert_to_element_dict(elements),
                    "page_structure": page_structure,
                    "screenshot": str(screenshot_path)
                }
                
                # Save discovery results
                results_path = self.work_dir / f"discovery_results_{timestamp}.json"
                with open(results_path, 'w') as f:
                    json.dump(discovery_results, f, indent=2)
                
                self.logger.info(f"Discovery results saved to {results_path}")
                
                return discovery_results
                
        except Exception as e:
            self.logger.error(f"Discovery failed: {str(e)}")
            return {
                "error": str(e),
                "application_url": url,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
            }
    
    async def _discover_page_elements(self, page) -> List[Dict[str, Any]]:
        """
        Discover elements on a page
        
        Args:
            page: Playwright page
            
        Returns:
            List[Dict[str, Any]]: Discovered elements
        """
        self.logger.info("Discovering page elements")
        
        elements = []
        
        # Find all interactive elements
        selectors = [
            "button",
            "input",
            "select",
            "a",
            "[role='button']",
            "[role='link']",
            "[role='checkbox']",
            "[role='radio']",
            "[role='tab']",
            "[role='menuitem']"
        ]
        
        for selector in selectors:
            try:
                # Find elements matching selector
                element_handles = await page.query_selector_all(selector)
                
                for handle in element_handles:
                    try:
                        # Get element properties
                        tag_name = await handle.evaluate("el => el.tagName.toLowerCase()")
                        element_id = await handle.evaluate("el => el.id")
                        element_name = await handle.evaluate("el => el.name")
                        element_type = await handle.evaluate("el => el.type")
                        element_value = await handle.evaluate("el => el.value")
                        element_text = await handle.evaluate("el => el.textContent")
                        element_class = await handle.evaluate("el => el.className")
                        element_placeholder = await handle.evaluate("el => el.placeholder")
                        
                        # Generate selectors
                        selectors = await self._generate_selectors(handle, tag_name, element_id, element_name, element_class)
                        
                        # Determine element type
                        element_category = self._determine_element_category(tag_name, element_type, element_class)
                        
                        # Create element info
                        element_info = {
                            "tag": tag_name,
                            "id": element_id,
                            "name": element_name,
                            "type": element_type,
                            "value": element_value,
                            "text": element_text.strip() if element_text else "",
                            "class": element_class,
                            "placeholder": element_placeholder,
                            "selectors": selectors,
                            "category": element_category
                        }
                        
                        # Add element to list
                        elements.append(element_info)
                        
                    except Exception as e:
                        self.logger.warning(f"Error processing element: {str(e)}")
                
            except Exception as e:
                self.logger.warning(f"Error finding elements with selector {selector}: {str(e)}")
        
        self.logger.info(f"Discovered {len(elements)} elements")
        return elements
    
    async def _generate_selectors(self, handle, tag_name, element_id, element_name, element_class) -> Dict[str, str]:
        """
        Generate selectors for an element
        
        Args:
            handle: Element handle
            tag_name: Element tag name
            element_id: Element ID
            element_name: Element name
            element_class: Element class
            
        Returns:
            Dict[str, str]: Selectors
        """
        selectors = {}
        
        # ID selector
        if element_id:
            selectors["id"] = f"#{element_id}"
        
        # Name selector
        if element_name:
            selectors["name"] = f"{tag_name}[name='{element_name}']"
        
        # Class selector
        if element_class:
            class_names = element_class.split()
            if class_names:
                selectors["class"] = f".{'.'.join(class_names)}"
        
        # XPath selector
        try:
            xpath = await handle.evaluate("""el => {
                function getXPath(element) {
                    if (element.id) {
                        return `//*[@id="${element.id}"]`;
                    }
                    if (element === document.body) {
                        return '/html/body';
                    }
                    if (!element.parentElement) {
                        return '';
                    }
                    
                    let siblings = Array.from(element.parentElement.children);
                    let index = siblings.indexOf(element) + 1;
                    let tagName = element.tagName.toLowerCase();
                    let sameTagSiblings = siblings.filter(s => s.tagName.toLowerCase() === tagName);
                    
                    if (sameTagSiblings.length > 1) {
                        return `${getXPath(element.parentElement)}/${tagName}[${index}]`;
                    } else {
                        return `${getXPath(element.parentElement)}/${tagName}`;
                    }
                }
                return getXPath(el);
            }""")
            
            if xpath:
                selectors["xpath"] = xpath
        except Exception as e:
            self.logger.warning(f"Error generating XPath: {str(e)}")
        
        # CSS selector
        try:
            css = await handle.evaluate("""el => {
                function getSelector(element) {
                    if (element.id) {
                        return `#${element.id}`;
                    }
                    if (element === document.body) {
                        return 'body';
                    }
                    if (!element.parentElement) {
                        return '';
                    }
                    
                    let selector = element.tagName.toLowerCase();
                    if (element.className) {
                        let classes = element.className.split(' ').filter(c => c);
                        if (classes.length) {
                            selector += `.${classes.join('.')}`;
                        }
                    }
                    
                    return `${getSelector(element.parentElement)} > ${selector}`;
                }
                return getSelector(el);
            }""")
            
            if css:
                selectors["css"] = css
        except Exception as e:
            self.logger.warning(f"Error generating CSS selector: {str(e)}")
        
        return selectors
    
    def _determine_element_category(self, tag_name, element_type, element_class) -> str:
        """
        Determine element category
        
        Args:
            tag_name: Element tag name
            element_type: Element type
            element_class: Element class
            
        Returns:
            str: Element category
        """
        tag_name = tag_name.lower() if tag_name else ""
        element_type = element_type.lower() if element_type else ""
        element_class = element_class.lower() if element_class else ""
        
        if tag_name == "button" or element_type == "button" or "btn" in element_class:
            return "button"
        elif tag_name == "input":
            if element_type in ["text", "email", "password", "search", "tel", "url"]:
                return "input"
            elif element_type in ["checkbox", "radio"]:
                return element_type
            elif element_type in ["submit", "reset", "button"]:
                return "button"
            else:
                return "input"
        elif tag_name == "select":
            return "select"
        elif tag_name == "a":
            return "link"
        elif tag_name == "textarea":
            return "textarea"
        else:
            return "other"
    
    async def _analyze_page_structure(self, page) -> Dict[str, Any]:
        """
        Analyze page structure
        
        Args:
            page: Playwright page
            
        Returns:
            Dict[str, Any]: Page structure
        """
        self.logger.info("Analyzing page structure")
        
        try:
            # Get page structure
            structure = await page.evaluate("""() => {
                function getStructure(element, depth = 0) {
                    if (depth > 5) return null; // Limit depth
                    
                    let result = {
                        tag: element.tagName.toLowerCase(),
                        id: element.id || null,
                        class: element.className || null,
                        children: []
                    };
                    
                    if (element.children.length > 0) {
                        for (let i = 0; i < Math.min(element.children.length, 10); i++) {
                            let childStructure = getStructure(element.children[i], depth + 1);
                            if (childStructure) {
                                result.children.push(childStructure);
                            }
                        }
                    }
                    
                    return result;
                }
                
                return getStructure(document.body);
            }""")
            
            return structure
            
        except Exception as e:
            self.logger.error(f"Error analyzing page structure: {str(e)}")
            return {}
    
    def _convert_to_element_dict(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert elements list to dictionary
        
        Args:
            elements: List of elements
            
        Returns:
            Dict[str, Any]: Elements dictionary
        """
        element_dict = {}
        
        for element in elements:
            # Skip elements without selectors
            if not element.get("selectors"):
                continue
            
            # Create element name
            element_name = None
            
            # Try to use ID
            if element.get("id"):
                element_name = element["id"]
            # Try to use name
            elif element.get("name"):
                element_name = element["name"]
            # Try to use text
            elif element.get("text"):
                # Clean and truncate text
                text = element["text"].strip().lower()
                text = ''.join(c for c in text if c.isalnum() or c == ' ')
                text = text.replace(' ', '_')
                text = text[:20]  # Truncate to 20 chars
                if text:
                    element_name = text
            
            # If no name found, use category and index
            if not element_name:
                category = element.get("category", "element")
                index = len([k for k in element_dict.keys() if k.startswith(category)])
                element_name = f"{category}_{index}"
            
            # Add element to dictionary
            element_dict[element_name] = element.get("selectors", {}).get("id") or \
                                        element.get("selectors", {}).get("name") or \
                                        element.get("selectors", {}).get("css") or \
                                        element.get("selectors", {}).get("xpath")
        
        return element_dict

