#!/usr/bin/env python3
"""
Discovery Agent for AutoGen Test Automation Framework
====================================================
This agent analyzes web applications to understand their structure,
elements, and workflows to enable intelligent test generation.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse

from .base_agent import BaseTestAgent


class DiscoveryAgent(BaseTestAgent):
    """Agent that discovers and analyzes web application structure"""
    
    def __init__(self, local_ai_provider=None):
        from config.settings import AgentRole
        super().__init__(
            role=AgentRole.DISCOVERY,
            name="DiscoveryAgent",
            system_message="You are a Discovery Agent that analyzes web applications to understand their structure, elements, and workflows for intelligent test generation.",
            local_ai_provider=local_ai_provider
        )
        
        # Discovery capabilities
        self.discovered_pages = {}
        self.discovered_elements = {}
        self.discovered_workflows = {}
        self.application_map = {}
        
        # Work directory for saving artifacts
        self.work_dir = Path(f"./work_dir/{self.name}")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Register agent functions
        self.register_function(self._analyze_application, "Analyze a web application to understand its structure")
        self.register_function(self._discover_page_elements, "Discover elements on a specific page")
        self.register_function(self._map_user_workflows, "Map user workflows for the application")
        self.register_function(self._generate_element_selectors, "Generate robust element selectors for testing")
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task assigned to this agent"""
        task_type = task_data.get("task_type", "analyze_application")
        
        if task_type == "analyze_application":
            return await self._analyze_application(task_data)
        elif task_type == "discover_page_elements":
            return await self._discover_page_elements(task_data)
        elif task_type == "map_user_workflows":
            return await self._map_user_workflows(task_data)
        elif task_type == "generate_element_selectors":
            return await self._generate_element_selectors(task_data)
        else:
            return {
                "status": "error",
                "error": f"Unknown task type: {task_type}"
            }
    
    async def _analyze_application(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a web application to understand its structure"""
        self.logger.info("🔍 Starting application analysis")
        
        try:
            application_url = task_data.get("application_url", "")
            analysis_depth = task_data.get("analysis_depth", "basic")  # basic, medium, deep
            
            if not application_url:
                return {
                    "status": "error",
                    "error": "No application URL provided"
                }
            
            # Start analysis
            analysis_result = {
                "application_url": application_url,
                "analysis_depth": analysis_depth,
                "discovered_pages": [],
                "application_structure": {},
                "key_elements": {},
                "user_workflows": [],
                "recommendations": [],
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # Phase 1: Discover main pages
            self.logger.info("📄 Phase 1: Discovering main pages")
            main_pages = await self._discover_main_pages(application_url)
            analysis_result["discovered_pages"] = main_pages
            
            # Phase 2: Analyze key elements on each page
            self.logger.info("🎯 Phase 2: Analyzing key elements")
            for page in main_pages[:3]:  # Limit to first 3 pages for now
                page_elements = await self._analyze_page_elements(page["url"])
                analysis_result["key_elements"][page["name"]] = page_elements
            
            # Phase 3: Identify common workflows
            self.logger.info("🔄 Phase 3: Identifying user workflows")
            workflows = await self._identify_workflows(main_pages, analysis_result["key_elements"])
            analysis_result["user_workflows"] = workflows
            
            # Phase 4: Generate recommendations
            self.logger.info("💡 Phase 4: Generating testing recommendations")
            recommendations = await self._generate_testing_recommendations(analysis_result)
            analysis_result["recommendations"] = recommendations
            
            # Save analysis results
            analysis_file = f"application_analysis_{int(time.time())}.json"
            analysis_path = self.work_dir / analysis_file
            
            with open(analysis_path, 'w') as f:
                json.dump(analysis_result, f, indent=2)
            
            self.logger.info(f"📁 Analysis saved to: {analysis_path}")
            
            return {
                "status": "completed",
                "analysis_result": analysis_result,
                "analysis_file": str(analysis_path),
                "pages_discovered": len(main_pages),
                "elements_analyzed": sum(len(elements) for elements in analysis_result["key_elements"].values()),
                "workflows_identified": len(workflows)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Application analysis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _discover_main_pages(self, base_url: str) -> List[Dict[str, Any]]:
        """Discover main pages of the application"""
        # For now, we'll simulate page discovery
        # In a real implementation, this would use browser automation
        
        discovered_pages = [
            {
                "name": "Home Page",
                "url": base_url,
                "type": "landing",
                "priority": "high",
                "description": "Main landing page of the application"
            },
            {
                "name": "Login Page",
                "url": urljoin(base_url, "/login"),
                "type": "authentication",
                "priority": "high",
                "description": "User authentication page"
            },
            {
                "name": "Product Catalog",
                "url": urljoin(base_url, "/catalog"),
                "type": "catalog",
                "priority": "high",
                "description": "Product browsing and search"
            },
            {
                "name": "Shopping Cart",
                "url": urljoin(base_url, "/cart"),
                "type": "transaction",
                "priority": "high",
                "description": "Shopping cart and checkout"
            },
            {
                "name": "User Profile",
                "url": urljoin(base_url, "/profile"),
                "type": "account",
                "priority": "medium",
                "description": "User account management"
            }
        ]
        
        self.logger.info(f"📄 Discovered {len(discovered_pages)} main pages")
        return discovered_pages
    
    async def _analyze_page_elements(self, page_url: str) -> Dict[str, Any]:
        """Analyze key elements on a specific page"""
        # Simulate element discovery based on page type
        page_name = urlparse(page_url).path.strip('/') or 'home'
        
        if 'login' in page_name.lower():
            elements = {
                "forms": [
                    {
                        "name": "login_form",
                        "selector": "#loginForm",
                        "fields": [
                            {"name": "username", "selector": "#username", "type": "text", "required": True},
                            {"name": "password", "selector": "#password", "type": "password", "required": True}
                        ]
                    }
                ],
                "buttons": [
                    {"name": "login_button", "selector": "#loginBtn", "action": "submit"},
                    {"name": "forgot_password", "selector": "#forgotPassword", "action": "navigate"}
                ],
                "links": [
                    {"name": "register_link", "selector": "#registerLink", "target": "/register"}
                ]
            }
        elif 'catalog' in page_name.lower() or 'product' in page_name.lower():
            elements = {
                "search": [
                    {"name": "search_box", "selector": "#searchBox", "type": "text"},
                    {"name": "search_button", "selector": "#searchBtn", "action": "search"}
                ],
                "filters": [
                    {"name": "category_filter", "selector": "#categoryFilter", "type": "dropdown"},
                    {"name": "price_filter", "selector": "#priceFilter", "type": "range"}
                ],
                "products": [
                    {"name": "product_grid", "selector": ".product-grid", "type": "container"},
                    {"name": "product_item", "selector": ".product-item", "type": "repeating"},
                    {"name": "add_to_cart", "selector": ".add-to-cart-btn", "action": "add_to_cart"}
                ]
            }
        elif 'cart' in page_name.lower():
            elements = {
                "cart_items": [
                    {"name": "cart_container", "selector": "#cartContainer", "type": "container"},
                    {"name": "cart_item", "selector": ".cart-item", "type": "repeating"},
                    {"name": "quantity_input", "selector": ".quantity-input", "type": "number"}
                ],
                "actions": [
                    {"name": "update_cart", "selector": "#updateCart", "action": "update"},
                    {"name": "checkout_button", "selector": "#checkoutBtn", "action": "checkout"},
                    {"name": "continue_shopping", "selector": "#continueShopping", "action": "navigate"}
                ],
                "totals": [
                    {"name": "subtotal", "selector": "#subtotal", "type": "display"},
                    {"name": "total", "selector": "#total", "type": "display"}
                ]
            }
        else:
            # Default home page elements
            elements = {
                "navigation": [
                    {"name": "main_menu", "selector": "#mainMenu", "type": "navigation"},
                    {"name": "user_menu", "selector": "#userMenu", "type": "dropdown"}
                ],
                "content": [
                    {"name": "hero_section", "selector": "#heroSection", "type": "display"},
                    {"name": "featured_products", "selector": "#featuredProducts", "type": "container"}
                ],
                "footer": [
                    {"name": "footer_links", "selector": "#footerLinks", "type": "navigation"}
                ]
            }
        
        self.logger.info(f"🎯 Analyzed {sum(len(category) for category in elements.values())} elements on {page_url}")
        return elements
    
    async def _identify_workflows(self, pages: List[Dict[str, Any]], elements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify common user workflows based on discovered pages and elements"""
        workflows = []
        
        # E-commerce shopping workflow
        if any('catalog' in page['name'].lower() for page in pages) and any('cart' in page['name'].lower() for page in pages):
            workflows.append({
                "name": "Complete Shopping Workflow",
                "type": "end_to_end",
                "priority": "high",
                "description": "Full shopping experience from browsing to checkout",
                "steps": [
                    {"action": "navigate", "target": "home_page", "description": "Start at home page"},
                    {"action": "navigate", "target": "catalog", "description": "Browse product catalog"},
                    {"action": "search", "target": "search_box", "description": "Search for products"},
                    {"action": "click", "target": "product_item", "description": "Select a product"},
                    {"action": "click", "target": "add_to_cart", "description": "Add product to cart"},
                    {"action": "navigate", "target": "cart", "description": "Go to shopping cart"},
                    {"action": "click", "target": "checkout_button", "description": "Proceed to checkout"}
                ],
                "test_scenarios": [
                    "Search and add single product to cart",
                    "Add multiple products to cart",
                    "Update quantities in cart",
                    "Remove items from cart"
                ]
            })
        
        # Authentication workflow
        if any('login' in page['name'].lower() for page in pages):
            workflows.append({
                "name": "User Authentication Workflow",
                "type": "authentication",
                "priority": "high",
                "description": "User login and account access",
                "steps": [
                    {"action": "navigate", "target": "login_page", "description": "Go to login page"},
                    {"action": "input", "target": "username", "description": "Enter username"},
                    {"action": "input", "target": "password", "description": "Enter password"},
                    {"action": "click", "target": "login_button", "description": "Submit login form"},
                    {"action": "verify", "target": "user_menu", "description": "Verify successful login"}
                ],
                "test_scenarios": [
                    "Valid login credentials",
                    "Invalid login credentials",
                    "Empty form submission",
                    "Password reset flow"
                ]
            })
        
        # Product browsing workflow
        if any('catalog' in page['name'].lower() for page in pages):
            workflows.append({
                "name": "Product Browsing Workflow",
                "type": "browsing",
                "priority": "medium",
                "description": "Product discovery and filtering",
                "steps": [
                    {"action": "navigate", "target": "catalog", "description": "Go to product catalog"},
                    {"action": "input", "target": "search_box", "description": "Enter search term"},
                    {"action": "click", "target": "search_button", "description": "Execute search"},
                    {"action": "select", "target": "category_filter", "description": "Apply category filter"},
                    {"action": "verify", "target": "product_grid", "description": "Verify filtered results"}
                ],
                "test_scenarios": [
                    "Search by product name",
                    "Filter by category",
                    "Filter by price range",
                    "Sort products by price/rating"
                ]
            })
        
        self.logger.info(f"🔄 Identified {len(workflows)} user workflows")
        return workflows
    
    async def _generate_testing_recommendations(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate testing recommendations based on analysis"""
        recommendations = []
        
        # Recommend test frameworks based on application complexity
        total_elements = sum(len(elements) for elements in analysis_result["key_elements"].values())
        
        if total_elements > 20:
            recommendations.append({
                "type": "framework",
                "priority": "high",
                "title": "Use Playwright for Complex UI Testing",
                "description": "Application has many interactive elements. Playwright provides better reliability for complex scenarios.",
                "rationale": f"Detected {total_elements} interactive elements across pages"
            })
        else:
            recommendations.append({
                "type": "framework",
                "priority": "medium",
                "title": "Selenium WebDriver Suitable",
                "description": "Application complexity is moderate. Selenium WebDriver should handle testing requirements.",
                "rationale": f"Detected {total_elements} interactive elements across pages"
            })
        
        # Recommend test patterns based on workflows
        if len(analysis_result["user_workflows"]) > 2:
            recommendations.append({
                "type": "pattern",
                "priority": "high",
                "title": "Implement Page Object Model",
                "description": "Multiple workflows detected. Use Page Object Model for maintainable test code.",
                "rationale": f"Found {len(analysis_result['user_workflows'])} distinct workflows"
            })
        
        # Recommend data-driven testing for e-commerce
        if any('shopping' in workflow['name'].lower() for workflow in analysis_result["user_workflows"]):
            recommendations.append({
                "type": "data",
                "priority": "medium",
                "title": "Use Data-Driven Testing",
                "description": "E-commerce workflows benefit from testing with multiple product data sets.",
                "rationale": "Shopping workflows detected"
            })
        
        # Recommend API testing integration
        recommendations.append({
            "type": "integration",
            "priority": "medium",
            "title": "Include API Testing",
            "description": "Combine UI tests with API validation for comprehensive coverage.",
            "rationale": "Modern web applications rely heavily on API interactions"
        })
        
        self.logger.info(f"💡 Generated {len(recommendations)} testing recommendations")
        return recommendations
    
    async def _discover_page_elements(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Discover elements on a specific page"""
        self.logger.info("🎯 Discovering page elements")
        
        try:
            page_url = task_data.get("page_url", "")
            element_types = task_data.get("element_types", ["forms", "buttons", "links"])
            
            if not page_url:
                return {
                    "status": "error",
                    "error": "No page URL provided"
                }
            
            # Analyze the specific page
            elements = await self._analyze_page_elements(page_url)
            
            # Filter by requested element types
            filtered_elements = {
                element_type: elements.get(element_type, [])
                for element_type in element_types
                if element_type in elements
            }
            
            return {
                "status": "completed",
                "page_url": page_url,
                "elements": filtered_elements,
                "total_elements": sum(len(category) for category in filtered_elements.values())
            }
            
        except Exception as e:
            self.logger.error(f"❌ Page element discovery failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _map_user_workflows(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map user workflows for the application"""
        self.logger.info("🔄 Mapping user workflows")
        
        try:
            application_url = task_data.get("application_url", "")
            workflow_types = task_data.get("workflow_types", ["authentication", "shopping", "browsing"])
            
            # Discover pages first
            pages = await self._discover_main_pages(application_url)
            
            # Analyze elements
            elements = {}
            for page in pages[:3]:  # Limit for performance
                page_elements = await self._analyze_page_elements(page["url"])
                elements[page["name"]] = page_elements
            
            # Identify workflows
            workflows = await self._identify_workflows(pages, elements)
            
            # Filter by requested workflow types
            filtered_workflows = [
                workflow for workflow in workflows
                if workflow["type"] in workflow_types
            ]
            
            return {
                "status": "completed",
                "application_url": application_url,
                "workflows": filtered_workflows,
                "total_workflows": len(filtered_workflows)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Workflow mapping failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _generate_element_selectors(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate robust element selectors for testing"""
        self.logger.info("🎯 Generating element selectors")
        
        try:
            page_url = task_data.get("page_url", "")
            element_descriptions = task_data.get("element_descriptions", [])
            
            if not page_url or not element_descriptions:
                return {
                    "status": "error",
                    "error": "Page URL and element descriptions required"
                }
            
            # Generate selectors based on descriptions
            generated_selectors = []
            
            for description in element_descriptions:
                # Simple selector generation based on common patterns
                if "login" in description.lower() and "button" in description.lower():
                    selectors = [
                        {"type": "id", "value": "#loginBtn", "priority": "high"},
                        {"type": "css", "value": "button[type='submit']", "priority": "medium"},
                        {"type": "xpath", "value": "//button[contains(text(), 'Login')]", "priority": "low"}
                    ]
                elif "username" in description.lower() or "email" in description.lower():
                    selectors = [
                        {"type": "id", "value": "#username", "priority": "high"},
                        {"type": "name", "value": "input[name='username']", "priority": "medium"},
                        {"type": "xpath", "value": "//input[@type='text' or @type='email']", "priority": "low"}
                    ]
                elif "password" in description.lower():
                    selectors = [
                        {"type": "id", "value": "#password", "priority": "high"},
                        {"type": "css", "value": "input[type='password']", "priority": "medium"},
                        {"type": "xpath", "value": "//input[@type='password']", "priority": "low"}
                    ]
                elif "search" in description.lower():
                    selectors = [
                        {"type": "id", "value": "#searchBox", "priority": "high"},
                        {"type": "css", "value": "input[placeholder*='search']", "priority": "medium"},
                        {"type": "xpath", "value": "//input[contains(@placeholder, 'search')]", "priority": "low"}
                    ]
                else:
                    # Generic selectors
                    selectors = [
                        {"type": "css", "value": f"[data-testid='{description.lower().replace(' ', '-')}']", "priority": "high"},
                        {"type": "css", "value": f".{description.lower().replace(' ', '-')}", "priority": "medium"},
                        {"type": "xpath", "value": f"//*[contains(text(), '{description}')]", "priority": "low"}
                    ]
                
                generated_selectors.append({
                    "description": description,
                    "selectors": selectors,
                    "recommended": selectors[0]  # Highest priority selector
                })
            
            return {
                "status": "completed",
                "page_url": page_url,
                "generated_selectors": generated_selectors,
                "total_elements": len(generated_selectors)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Selector generation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return [
            "analyze_application",
            "discover_page_elements", 
            "map_user_workflows",
            "generate_element_selectors"
        ]

