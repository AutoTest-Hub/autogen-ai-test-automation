"""
Enhanced Discovery Agent
========================

This agent provides intelligent application analysis and discovery capabilities.
It goes beyond basic element discovery to understand application structure,
user flows, business logic, and testing opportunities.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from .base_agent import BaseTestAgent
from config.settings import AgentRole
from utils.step_generator import create_step_generator
from utils.intelligent_flow_handler import create_intelligent_flow_handler


class EnhancedDiscoveryAgent(BaseTestAgent):
    """
    Enhanced Discovery Agent with intelligent application analysis capabilities
    """
    
    def __init__(self, **kwargs):
        system_message = """
You are the Enhanced Discovery Agent, an expert in intelligent application analysis and discovery. Your responsibilities include:

1. **Deep Application Analysis**: Understand application structure, navigation patterns, and user workflows
2. **Intelligent Element Discovery**: Identify not just elements, but their purpose and relationships
3. **Business Logic Understanding**: Analyze forms, validations, and business rules
4. **User Journey Mapping**: Map complete user journeys and interaction patterns
5. **Testing Opportunity Identification**: Identify areas that need comprehensive testing
6. **Performance and Security Analysis**: Detect potential performance and security testing areas
7. **Accessibility Assessment**: Evaluate accessibility features and compliance
8. **Cross-browser Compatibility**: Analyze compatibility requirements and issues

**Key Capabilities**:
- Advanced DOM analysis with semantic understanding
- Dynamic content detection and handling
- Form analysis with validation rule discovery
- Navigation pattern recognition
- API endpoint discovery
- Performance bottleneck identification
- Security vulnerability detection
- Accessibility compliance checking
- Mobile responsiveness analysis
- Third-party integration detection

**Analysis Depth Levels**:
- Surface Level: Basic element discovery
- Structural Level: Page relationships and navigation
- Behavioral Level: User interactions and workflows
- Business Level: Business rules and validation logic
- Technical Level: Performance, security, and architecture

You provide comprehensive analysis that enables intelligent test generation and optimization.
"""
        
        super().__init__(role=AgentRole.DISCOVERY, system_message=system_message, **kwargs)
        self.step_generator = create_step_generator()
        self.flow_handler = create_intelligent_flow_handler()
        self.browser = None
        self.context = None
        self.page = None
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process enhanced discovery task with intelligent analysis
        """
        try:
            task_type = task_data.get("type", "enhanced_discovery")
            
            if task_type == "enhanced_discovery":
                return await self._perform_enhanced_discovery(task_data)
            elif task_type == "deep_analysis":
                return await self._perform_deep_analysis(task_data)
            elif task_type == "business_logic_analysis":
                return await self._analyze_business_logic(task_data)
            elif task_type == "performance_analysis":
                return await self._analyze_performance_characteristics(task_data)
            else:
                return {"error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Enhanced discovery failed: {str(e)}")
            return {"error": str(e)}

    async def analyze_application(
        self,
        url: str,
        analysis_depth: str = "comprehensive",
        headless: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a web application for test generation.

        This is a convenience method that wraps the task-based API for simpler use.
        Called by the API server for test creation requests.

        Args:
            url: URL of the application to analyze
            analysis_depth: Depth of analysis ("basic", "standard", "comprehensive")
            headless: Whether to run browser in headless mode

        Returns:
            Dict[str, Any]: Discovery results including application profile,
                           discovered elements, user journeys, and testing recommendations.
        """
        try:
            self.logger.info(f"Analyzing application: {url}")

            task_data = {
                "type": "enhanced_discovery",
                "url": url,
                "analysis_depth": analysis_depth,
                "headless": headless
            }

            result = await self._perform_enhanced_discovery(task_data)

            # Return results in a format suitable for API consumption
            if "error" in result:
                return result

            discovery_results = result.get("discovery_results", {})

            return {
                "status": "success",
                "url": url,
                "application_profile": discovery_results.get("application_profile", {}),
                "page_analysis": discovery_results.get("page_analysis", {}),
                "user_journeys": discovery_results.get("user_journeys", {}),
                "business_logic": discovery_results.get("business_logic", {}),
                "technical_analysis": discovery_results.get("technical_analysis", {}),
                "testing_recommendations": discovery_results.get("testing_recommendations", {}),
                "risk_assessment": discovery_results.get("risk_assessment", {}),
                "intelligent_flows": discovery_results.get("intelligent_flows", {}),
                "summary": result.get("summary", {}),
                "output_file": result.get("output_file")
            }

        except Exception as e:
            self.logger.error(f"Application analysis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "url": url
            }

    async def _perform_enhanced_discovery(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive enhanced discovery
        """
        url = task_data.get("url")
        analysis_depth = task_data.get("analysis_depth", "comprehensive")
        
        if not url:
            return {"error": "URL is required for enhanced discovery"}
        
        discovery_results = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "analysis_depth": analysis_depth,
            "application_profile": {},
            "page_analysis": {},
            "user_journeys": {},
            "business_logic": {},
            "technical_analysis": {},
            "testing_recommendations": {},
            "risk_assessment": {}
        }
        
        try:
            # Initialize browser
            await self._initialize_browser(task_data.get("headless", True))
            
            # Navigate to the application
            await self.page.goto(url, wait_until="networkidle")
            
            # Perform multi-level analysis
            discovery_results["application_profile"] = await self._analyze_application_profile()
            discovery_results["page_analysis"] = await self._analyze_current_page()
            discovery_results["user_journeys"] = await self._discover_user_journeys()
            discovery_results["business_logic"] = await self._analyze_business_logic_patterns()
            discovery_results["technical_analysis"] = await self._perform_technical_analysis()
            discovery_results["testing_recommendations"] = await self._generate_testing_recommendations(discovery_results)
            discovery_results["risk_assessment"] = await self._assess_testing_risks(discovery_results)
            
            # Generate intelligent test flows
            flow_analysis = self.flow_handler.analyze_application_flows(discovery_results)
            discovery_results["intelligent_flows"] = flow_analysis
            
            # Save results
            output_file = self.save_work_artifact(
                f"enhanced_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                json.dumps(discovery_results, indent=2)
            )
            
            return {
                "status": "success",
                "discovery_results": discovery_results,
                "output_file": output_file,
                "summary": self._create_discovery_summary(discovery_results)
            }
            
        finally:
            await self._cleanup_browser()
    
    async def _initialize_browser(self, headless: bool = True):
        """Initialize browser for discovery"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = await self.context.new_page()
        
        # Enable request/response interception for API discovery
        await self.page.route("**/*", self._intercept_requests)
        
        self.api_calls = []
        self.performance_metrics = []
    
    async def _cleanup_browser(self):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    async def _intercept_requests(self, route):
        """Intercept requests for API discovery and performance analysis"""
        request = route.request
        
        # Log API calls
        if request.url.endswith(('.json', '.xml')) or '/api/' in request.url:
            self.api_calls.append({
                "url": request.url,
                "method": request.method,
                "headers": dict(request.headers),
                "timestamp": datetime.now().isoformat()
            })
        
        # Continue with the request
        await route.continue_()
    
    async def _analyze_application_profile(self) -> Dict[str, Any]:
        """
        Analyze overall application profile and characteristics
        """
        profile = {
            "application_type": "unknown",
            "technology_stack": {},
            "architecture_patterns": [],
            "ui_framework": "unknown",
            "responsive_design": False,
            "accessibility_features": {},
            "internationalization": False,
            "third_party_integrations": []
        }
        
        # Detect application type
        profile["application_type"] = await self._detect_application_type()
        
        # Analyze technology stack
        profile["technology_stack"] = await self._analyze_technology_stack()
        
        # Check responsive design
        profile["responsive_design"] = await self._check_responsive_design()
        
        # Analyze accessibility features
        profile["accessibility_features"] = await self._analyze_accessibility_features()
        
        # Detect UI framework
        profile["ui_framework"] = await self._detect_ui_framework()
        
        # Check internationalization
        profile["internationalization"] = await self._check_internationalization()
        
        # Detect third-party integrations
        profile["third_party_integrations"] = await self._detect_third_party_integrations()
        
        return profile
    
    async def _analyze_current_page(self) -> Dict[str, Any]:
        """
        Perform detailed analysis of the current page
        """
        page_analysis = {
            "url": self.page.url,
            "title": await self.page.title(),
            "meta_data": {},
            "structure": {},
            "interactive_elements": {},
            "forms": {},
            "navigation": {},
            "content_analysis": {},
            "performance_indicators": {}
        }
        
        # Extract meta data
        page_analysis["meta_data"] = await self._extract_meta_data()
        
        # Analyze page structure
        page_analysis["structure"] = await self._analyze_page_structure()
        
        # Discover interactive elements
        page_analysis["interactive_elements"] = await self._discover_interactive_elements()
        
        # Analyze forms
        page_analysis["forms"] = await self._analyze_forms()
        
        # Analyze navigation
        page_analysis["navigation"] = await self._analyze_navigation()
        
        # Analyze content
        page_analysis["content_analysis"] = await self._analyze_content()
        
        # Check performance indicators
        page_analysis["performance_indicators"] = await self._check_performance_indicators()
        
        return page_analysis
    
    async def _discover_user_journeys(self) -> Dict[str, Any]:
        """
        Discover and map user journeys through the application
        """
        journeys = {
            "primary_flows": [],
            "secondary_flows": [],
            "error_flows": [],
            "navigation_patterns": {},
            "user_personas": {}
        }
        
        # Discover primary user flows
        journeys["primary_flows"] = await self._discover_primary_flows()
        
        # Discover secondary flows
        journeys["secondary_flows"] = await self._discover_secondary_flows()
        
        # Analyze navigation patterns
        journeys["navigation_patterns"] = await self._analyze_navigation_patterns()
        
        # Identify user personas
        journeys["user_personas"] = await self._identify_user_personas()
        
        return journeys
    
    async def _analyze_business_logic_patterns(self) -> Dict[str, Any]:
        """
        Analyze business logic and validation patterns
        """
        business_logic = {
            "validation_rules": {},
            "business_workflows": [],
            "data_relationships": {},
            "authorization_patterns": {},
            "error_handling": {}
        }
        
        # Analyze validation rules
        business_logic["validation_rules"] = await self._analyze_validation_rules()
        
        # Identify business workflows
        business_logic["business_workflows"] = await self._identify_business_workflows()
        
        # Analyze data relationships
        business_logic["data_relationships"] = await self._analyze_data_relationships()
        
        # Check authorization patterns
        business_logic["authorization_patterns"] = await self._analyze_authorization_patterns()
        
        # Analyze error handling
        business_logic["error_handling"] = await self._analyze_error_handling()
        
        return business_logic
    
    async def _perform_technical_analysis(self) -> Dict[str, Any]:
        """
        Perform technical analysis of the application
        """
        technical = {
            "performance_characteristics": {},
            "security_indicators": {},
            "api_endpoints": self.api_calls,
            "resource_usage": {},
            "browser_compatibility": {},
            "mobile_compatibility": {}
        }
        
        # Analyze performance characteristics
        technical["performance_characteristics"] = await self._analyze_performance_characteristics()
        
        # Check security indicators
        technical["security_indicators"] = await self._analyze_security_indicators()
        
        # Analyze resource usage
        technical["resource_usage"] = await self._analyze_resource_usage()
        
        # Check browser compatibility indicators
        technical["browser_compatibility"] = await self._check_browser_compatibility()
        
        # Check mobile compatibility
        technical["mobile_compatibility"] = await self._check_mobile_compatibility()
        
        return technical
    
    async def _detect_application_type(self) -> str:
        """Detect the type of application"""
        # Check for common application patterns
        body_classes = await self.page.evaluate("() => document.body.className")
        page_content = await self.page.content()
        
        if "e-commerce" in body_classes.lower() or "shop" in self.page.url.lower():
            return "e-commerce"
        elif "admin" in body_classes.lower() or "dashboard" in page_content.lower():
            return "admin_dashboard"
        elif "blog" in body_classes.lower() or "article" in page_content.lower():
            return "content_management"
        elif "login" in page_content.lower() and "form" in page_content.lower():
            return "web_application"
        else:
            return "website"
    
    async def _analyze_technology_stack(self) -> Dict[str, Any]:
        """Analyze the technology stack used"""
        stack = {
            "frontend_frameworks": [],
            "css_frameworks": [],
            "javascript_libraries": [],
            "analytics_tools": [],
            "other_technologies": []
        }
        
        # Check for common frameworks and libraries
        scripts = await self.page.evaluate("""
            () => Array.from(document.scripts).map(script => script.src).filter(src => src)
        """)
        
        for script in scripts:
            if "react" in script.lower():
                stack["frontend_frameworks"].append("React")
            elif "angular" in script.lower():
                stack["frontend_frameworks"].append("Angular")
            elif "vue" in script.lower():
                stack["frontend_frameworks"].append("Vue.js")
            elif "bootstrap" in script.lower():
                stack["css_frameworks"].append("Bootstrap")
            elif "jquery" in script.lower():
                stack["javascript_libraries"].append("jQuery")
            elif "analytics" in script.lower() or "gtag" in script.lower():
                stack["analytics_tools"].append("Google Analytics")
        
        return stack
    
    async def _check_responsive_design(self) -> bool:
        """Check if the application has responsive design"""
        viewport_meta = await self.page.evaluate("""
            () => {
                const meta = document.querySelector('meta[name="viewport"]');
                return meta ? meta.content : null;
            }
        """)
        
        has_media_queries = await self.page.evaluate("""
            () => {
                const stylesheets = Array.from(document.styleSheets);
                for (let sheet of stylesheets) {
                    try {
                        const rules = Array.from(sheet.cssRules || sheet.rules);
                        for (let rule of rules) {
                            if (rule.type === CSSRule.MEDIA_RULE) {
                                return true;
                            }
                        }
                    } catch (e) {
                        // Cross-origin stylesheet
                    }
                }
                return false;
            }
        """)
        
        return viewport_meta is not None and has_media_queries
    
    async def _analyze_accessibility_features(self) -> Dict[str, Any]:
        """Analyze accessibility features"""
        accessibility = {
            "aria_labels": 0,
            "alt_texts": 0,
            "semantic_html": False,
            "keyboard_navigation": False,
            "color_contrast_issues": [],
            "accessibility_score": 0
        }
        
        # Count ARIA labels
        accessibility["aria_labels"] = await self.page.evaluate("""
            () => document.querySelectorAll('[aria-label], [aria-labelledby]').length
        """)
        
        # Count alt texts
        accessibility["alt_texts"] = await self.page.evaluate("""
            () => document.querySelectorAll('img[alt]').length
        """)
        
        # Check semantic HTML
        accessibility["semantic_html"] = await self.page.evaluate("""
            () => {
                const semanticTags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer'];
                return semanticTags.some(tag => document.querySelector(tag) !== null);
            }
        """)
        
        # Calculate basic accessibility score
        total_images = await self.page.evaluate("() => document.querySelectorAll('img').length")
        if total_images > 0:
            alt_text_ratio = accessibility["alt_texts"] / total_images
            accessibility["accessibility_score"] = min(100, alt_text_ratio * 50 + 
                                                     (50 if accessibility["semantic_html"] else 0))
        
        return accessibility
    
    async def _extract_meta_data(self) -> Dict[str, Any]:
        """Extract meta data from the page"""
        return await self.page.evaluate("""
            () => {
                const metas = {};
                document.querySelectorAll('meta').forEach(meta => {
                    const name = meta.name || meta.property || meta.httpEquiv;
                    if (name) {
                        metas[name] = meta.content;
                    }
                });
                return metas;
            }
        """)
    
    async def _analyze_page_structure(self) -> Dict[str, Any]:
        """Analyze the structure of the page"""
        return await self.page.evaluate("""
            () => {
                const structure = {
                    headings: {},
                    sections: 0,
                    forms: 0,
                    tables: 0,
                    lists: 0,
                    images: 0,
                    links: 0
                };
                
                // Count headings by level
                for (let i = 1; i <= 6; i++) {
                    structure.headings[`h${i}`] = document.querySelectorAll(`h${i}`).length;
                }
                
                structure.sections = document.querySelectorAll('section, div[class*="section"]').length;
                structure.forms = document.querySelectorAll('form').length;
                structure.tables = document.querySelectorAll('table').length;
                structure.lists = document.querySelectorAll('ul, ol').length;
                structure.images = document.querySelectorAll('img').length;
                structure.links = document.querySelectorAll('a').length;
                
                return structure;
            }
        """)
    
    async def _discover_interactive_elements(self) -> Dict[str, Any]:
        """Discover interactive elements on the page"""
        return await self.page.evaluate("""
            () => {
                const elements = {
                    buttons: [],
                    inputs: [],
                    selects: [],
                    links: [],
                    clickable_elements: []
                };
                
                // Buttons
                document.querySelectorAll('button, input[type="button"], input[type="submit"]').forEach((btn, index) => {
                    elements.buttons.push({
                        index: index,
                        text: btn.textContent || btn.value,
                        type: btn.type || 'button',
                        id: btn.id,
                        class: btn.className,
                        selector: btn.tagName.toLowerCase() + (btn.id ? `#${btn.id}` : '') + (btn.className ? `.${btn.className.split(' ')[0]}` : '')
                    });
                });
                
                // Input fields
                document.querySelectorAll('input, textarea').forEach((input, index) => {
                    elements.inputs.push({
                        index: index,
                        type: input.type,
                        name: input.name,
                        id: input.id,
                        placeholder: input.placeholder,
                        required: input.required,
                        selector: input.tagName.toLowerCase() + (input.id ? `#${input.id}` : '') + (input.name ? `[name="${input.name}"]` : '')
                    });
                });
                
                // Select elements
                document.querySelectorAll('select').forEach((select, index) => {
                    elements.selects.push({
                        index: index,
                        name: select.name,
                        id: select.id,
                        multiple: select.multiple,
                        options: Array.from(select.options).map(opt => ({text: opt.text, value: opt.value})),
                        selector: `select${select.id ? `#${select.id}` : ''}${select.name ? `[name="${select.name}"]` : ''}`
                    });
                });
                
                // Links
                document.querySelectorAll('a[href]').forEach((link, index) => {
                    elements.links.push({
                        index: index,
                        text: link.textContent.trim(),
                        href: link.href,
                        target: link.target,
                        selector: `a[href="${link.getAttribute('href')}"]`
                    });
                });
                
                return elements;
            }
        """)
    
    async def _analyze_forms(self) -> Dict[str, Any]:
        """Analyze forms on the page"""
        return await self.page.evaluate("""
            () => {
                const forms = [];
                
                document.querySelectorAll('form').forEach((form, index) => {
                    const formData = {
                        index: index,
                        action: form.action,
                        method: form.method,
                        id: form.id,
                        class: form.className,
                        fields: [],
                        validation_rules: {}
                    };
                    
                    // Analyze form fields
                    form.querySelectorAll('input, textarea, select').forEach(field => {
                        const fieldData = {
                            name: field.name,
                            type: field.type,
                            required: field.required,
                            pattern: field.pattern,
                            minLength: field.minLength,
                            maxLength: field.maxLength,
                            min: field.min,
                            max: field.max,
                            placeholder: field.placeholder
                        };
                        
                        formData.fields.push(fieldData);
                        
                        // Extract validation rules
                        if (field.required) {
                            formData.validation_rules[field.name] = formData.validation_rules[field.name] || [];
                            formData.validation_rules[field.name].push('required');
                        }
                        if (field.pattern) {
                            formData.validation_rules[field.name] = formData.validation_rules[field.name] || [];
                            formData.validation_rules[field.name].push(`pattern: ${field.pattern}`);
                        }
                    });
                    
                    forms.push(formData);
                });
                
                return forms;
            }
        """)
    
    async def _analyze_navigation(self) -> Dict[str, Any]:
        """Analyze navigation structure"""
        return await self.page.evaluate("""
            () => {
                const navigation = {
                    main_nav: [],
                    breadcrumbs: [],
                    footer_nav: [],
                    sidebar_nav: []
                };
                
                // Main navigation
                const mainNav = document.querySelector('nav, .navbar, .navigation, .main-nav');
                if (mainNav) {
                    mainNav.querySelectorAll('a').forEach(link => {
                        navigation.main_nav.push({
                            text: link.textContent.trim(),
                            href: link.href,
                            active: link.classList.contains('active') || link.classList.contains('current')
                        });
                    });
                }
                
                // Breadcrumbs
                const breadcrumbs = document.querySelector('.breadcrumb, .breadcrumbs, nav[aria-label="breadcrumb"]');
                if (breadcrumbs) {
                    breadcrumbs.querySelectorAll('a, span').forEach(item => {
                        navigation.breadcrumbs.push({
                            text: item.textContent.trim(),
                            href: item.href || null
                        });
                    });
                }
                
                return navigation;
            }
        """)
    
    async def _analyze_content(self) -> Dict[str, Any]:
        """Analyze page content"""
        return await self.page.evaluate("""
            () => {
                const content = {
                    word_count: 0,
                    has_dynamic_content: false,
                    content_types: [],
                    media_elements: {
                        images: 0,
                        videos: 0,
                        audio: 0
                    }
                };
                
                // Word count
                const textContent = document.body.textContent || '';
                content.word_count = textContent.split(/\\s+/).filter(word => word.length > 0).length;
                
                // Check for dynamic content indicators
                content.has_dynamic_content = document.querySelectorAll('[data-bind], [ng-], [v-], .loading, .spinner').length > 0;
                
                // Media elements
                content.media_elements.images = document.querySelectorAll('img').length;
                content.media_elements.videos = document.querySelectorAll('video').length;
                content.media_elements.audio = document.querySelectorAll('audio').length;
                
                return content;
            }
        """)
    
    async def _check_performance_indicators(self) -> Dict[str, Any]:
        """Check performance indicators"""
        performance = await self.page.evaluate("""
            () => {
                const perf = performance.getEntriesByType('navigation')[0];
                return {
                    load_time: perf ? perf.loadEventEnd - perf.loadEventStart : 0,
                    dom_content_loaded: perf ? perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart : 0,
                    resource_count: performance.getEntriesByType('resource').length
                };
            }
        """)
        
        return performance
    
    async def _discover_primary_flows(self) -> List[Dict[str, Any]]:
        """Discover primary user flows"""
        flows = []
        
        # Look for common primary flow indicators
        login_elements = await self.page.query_selector_all('input[type="password"], input[name*="password"]')
        if login_elements:
            flows.append({
                "name": "user_authentication",
                "type": "primary",
                "description": "User login and authentication flow",
                "entry_points": ["login form", "sign in button"],
                "complexity": "medium"
            })
        
        # Look for e-commerce flows
        cart_elements = await self.page.query_selector_all('[class*="cart"], [id*="cart"], [class*="basket"]')
        if cart_elements:
            flows.append({
                "name": "shopping_cart",
                "type": "primary",
                "description": "Shopping cart and checkout flow",
                "entry_points": ["add to cart", "cart icon"],
                "complexity": "high"
            })
        
        return flows
    
    async def _discover_secondary_flows(self) -> List[Dict[str, Any]]:
        """Discover secondary user flows"""
        flows = []
        
        # Profile management
        profile_elements = await self.page.query_selector_all('[class*="profile"], [id*="profile"], [class*="account"]')
        if profile_elements:
            flows.append({
                "name": "profile_management",
                "type": "secondary",
                "description": "User profile and account management",
                "entry_points": ["profile link", "account settings"],
                "complexity": "medium"
            })
        
        return flows
    
    async def _analyze_navigation_patterns(self) -> Dict[str, Any]:
        """Analyze navigation patterns"""
        return {
            "navigation_type": "horizontal_menu",  # This would be detected
            "depth_levels": 2,  # This would be calculated
            "responsive_navigation": True,  # This would be detected
            "search_functionality": await self.page.query_selector('input[type="search"], .search-box') is not None
        }
    
    async def _identify_user_personas(self) -> Dict[str, Any]:
        """Identify potential user personas"""
        personas = {}
        
        # This would analyze the application to identify different user types
        # For now, return a basic structure
        personas["guest_user"] = {
            "description": "Unauthenticated user browsing the site",
            "capabilities": ["browse", "search", "view_content"],
            "restrictions": ["cannot_purchase", "cannot_save_preferences"]
        }
        
        return personas
    
    async def _analyze_validation_rules(self) -> Dict[str, Any]:
        """Analyze validation rules in forms"""
        validation_rules = {}
        
        forms = await self.page.query_selector_all('form')
        for i, form in enumerate(forms):
            form_rules = {}
            
            inputs = await form.query_selector_all('input, textarea, select')
            for input_elem in inputs:
                name = await input_elem.get_attribute('name')
                if name:
                    rules = []
                    
                    if await input_elem.get_attribute('required'):
                        rules.append('required')
                    
                    pattern = await input_elem.get_attribute('pattern')
                    if pattern:
                        rules.append(f'pattern: {pattern}')
                    
                    min_length = await input_elem.get_attribute('minlength')
                    if min_length:
                        rules.append(f'minlength: {min_length}')
                    
                    max_length = await input_elem.get_attribute('maxlength')
                    if max_length:
                        rules.append(f'maxlength: {max_length}')
                    
                    if rules:
                        form_rules[name] = rules
            
            if form_rules:
                validation_rules[f'form_{i}'] = form_rules
        
        return validation_rules
    
    async def _identify_business_workflows(self) -> List[Dict[str, Any]]:
        """Identify business workflows"""
        workflows = []
        
        # This would analyze the application to identify business processes
        # For now, return basic workflows based on common patterns
        
        if await self.page.query_selector('form'):
            workflows.append({
                "name": "data_entry_workflow",
                "description": "User data entry and submission process",
                "steps": ["form_display", "data_entry", "validation", "submission", "confirmation"],
                "business_value": "high"
            })
        
        return workflows
    
    async def _analyze_data_relationships(self) -> Dict[str, Any]:
        """Analyze data relationships"""
        return {
            "form_dependencies": {},  # This would be populated with actual analysis
            "data_flow": {},
            "validation_dependencies": {}
        }
    
    async def _analyze_authorization_patterns(self) -> Dict[str, Any]:
        """Analyze authorization patterns"""
        return {
            "authentication_required": await self.page.query_selector('input[type="password"]') is not None,
            "role_based_access": False,  # This would be detected
            "session_management": True   # This would be analyzed
        }
    
    async def _analyze_error_handling(self) -> Dict[str, Any]:
        """Analyze error handling patterns"""
        return {
            "error_message_containers": await self.page.query_selector_all('.error, .alert-danger, .validation-error'),
            "client_side_validation": True,  # This would be detected
            "server_side_validation": True   # This would be inferred
        }
    
    async def _analyze_performance_characteristics(self) -> Dict[str, Any]:
        """Analyze performance characteristics"""
        return {
            "page_load_time": 0,  # This would be measured
            "resource_count": len(self.api_calls),
            "large_resources": [],  # This would be identified
            "optimization_opportunities": []
        }
    
    async def _analyze_security_indicators(self) -> Dict[str, Any]:
        """Analyze security indicators"""
        return {
            "https_usage": self.page.url.startswith('https://'),
            "csrf_protection": await self.page.query_selector('input[name="_token"], input[name="csrf_token"]') is not None,
            "xss_protection": True,  # This would be analyzed
            "security_headers": {}   # This would be checked
        }
    
    async def _analyze_resource_usage(self) -> Dict[str, Any]:
        """Analyze resource usage"""
        return {
            "javascript_files": len([call for call in self.api_calls if call['url'].endswith('.js')]),
            "css_files": len([call for call in self.api_calls if call['url'].endswith('.css')]),
            "image_files": len([call for call in self.api_calls if any(call['url'].endswith(ext) for ext in ['.jpg', '.png', '.gif', '.svg'])]),
            "total_requests": len(self.api_calls)
        }
    
    async def _check_browser_compatibility(self) -> Dict[str, Any]:
        """Check browser compatibility indicators"""
        return {
            "modern_features_used": False,  # This would be detected
            "polyfills_present": False,     # This would be checked
            "compatibility_issues": []      # This would be identified
        }
    
    async def _check_mobile_compatibility(self) -> Dict[str, Any]:
        """Check mobile compatibility"""
        return {
            "responsive_design": await self._check_responsive_design(),
            "touch_friendly": False,  # This would be analyzed
            "mobile_specific_features": []
        }
    
    async def _detect_ui_framework(self) -> str:
        """Detect UI framework being used"""
        # This would analyze the DOM and scripts to detect frameworks
        return "unknown"
    
    async def _check_internationalization(self) -> bool:
        """Check for internationalization features"""
        lang_attr = await self.page.get_attribute('html', 'lang')
        return lang_attr is not None
    
    async def _detect_third_party_integrations(self) -> List[str]:
        """Detect third-party integrations"""
        integrations = []
        
        # Check for common third-party services
        for call in self.api_calls:
            url = call['url'].lower()
            if 'google-analytics' in url or 'gtag' in url:
                integrations.append('Google Analytics')
            elif 'facebook' in url:
                integrations.append('Facebook SDK')
            elif 'stripe' in url:
                integrations.append('Stripe Payment')
            elif 'paypal' in url:
                integrations.append('PayPal')
        
        return list(set(integrations))
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this agent provides"""
        return [
            "enhanced_application_discovery",
            "intelligent_element_analysis", 
            "business_context_understanding",
            "technical_architecture_analysis",
            "user_journey_identification",
            "risk_assessment",
            "testing_strategy_recommendations",
            "comprehensive_application_profiling"
        ]
    
    def _generate_testing_recommendations(self, discovery_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate testing recommendations based on discovery results"""
        recommendations = {
            "priority_areas": [],
            "test_types": [],
            "automation_opportunities": [],
            "risk_mitigation": []
        }
        
        # Analyze forms for testing recommendations
        forms = discovery_results.get("page_analysis", {}).get("forms", [])
        if forms:
            recommendations["priority_areas"].append("Form validation testing")
            recommendations["test_types"].append("functional_testing")
        
        # Check for authentication
        if discovery_results.get("business_logic", {}).get("authorization_patterns", {}).get("authentication_required"):
            recommendations["priority_areas"].append("Authentication and authorization testing")
            recommendations["test_types"].append("security_testing")
        
        # Performance recommendations
        if discovery_results.get("technical_analysis", {}).get("resource_usage", {}).get("total_requests", 0) > 50:
            recommendations["priority_areas"].append("Performance optimization testing")
            recommendations["test_types"].append("performance_testing")
        
        return recommendations
    
    async def _assess_testing_risks(self, discovery_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess testing risks based on discovery results"""
        risks = {
            "high_risk_areas": [],
            "complexity_factors": [],
            "maintenance_challenges": [],
            "mitigation_strategies": []
        }
        
        # Dynamic content risk
        if discovery_results.get("page_analysis", {}).get("content_analysis", {}).get("has_dynamic_content"):
            risks["high_risk_areas"].append("Dynamic content timing issues")
            risks["mitigation_strategies"].append("Implement smart waiting strategies")
        
        # Complex forms risk
        forms = discovery_results.get("page_analysis", {}).get("forms", [])
        complex_forms = [f for f in forms if len(f.get("fields", [])) > 10]
        if complex_forms:
            risks["high_risk_areas"].append("Complex form validation")
            risks["mitigation_strategies"].append("Implement comprehensive form testing")
        
        return risks
    
    def _create_discovery_summary(self, discovery_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of discovery results"""
        summary = {
            "application_type": discovery_results.get("application_profile", {}).get("application_type", "unknown"),
            "total_pages_analyzed": 1,  # Currently analyzing one page
            "interactive_elements_found": 0,
            "forms_discovered": 0,
            "api_endpoints_found": len(self.api_calls),
            "testing_priority": "medium",
            "estimated_test_complexity": "medium"
        }
        
        # Count interactive elements
        interactive = discovery_results.get("page_analysis", {}).get("interactive_elements", {})
        summary["interactive_elements_found"] = (
            len(interactive.get("buttons", [])) +
            len(interactive.get("inputs", [])) +
            len(interactive.get("selects", [])) +
            len(interactive.get("links", []))
        )
        
        # Count forms
        summary["forms_discovered"] = len(discovery_results.get("page_analysis", {}).get("forms", []))
        
        # Determine testing priority
        if summary["forms_discovered"] > 0 or summary["api_endpoints_found"] > 10:
            summary["testing_priority"] = "high"
        elif summary["interactive_elements_found"] > 20:
            summary["testing_priority"] = "medium"
        else:
            summary["testing_priority"] = "low"
        
        return summary


def create_enhanced_discovery_agent(**kwargs) -> EnhancedDiscoveryAgent:
    """Factory function to create an enhanced discovery agent"""
    return EnhancedDiscoveryAgent(**kwargs)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_enhanced_discovery():
        agent = create_enhanced_discovery_agent()
        
        task_data = {
            "type": "enhanced_discovery",
            "url": "https://example.com",
            "analysis_depth": "comprehensive",
            "headless": True
        }
        
        result = await agent.process_task(task_data)
        print(f"Discovery completed: {result.get('status')}")
        if result.get('summary'):
            print(f"Summary: {result['summary']}")
    
    asyncio.run(test_enhanced_discovery())
