"""
Knowledge Ingester for AutoGen AI QA Platform

Automatically extracts knowledge from various sources:
- OpenAPI/Swagger specifications
- README.md files
- Existing test suites
- Tech stack detection
"""

import json
import re
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from enum import Enum
import logging

from .application_context import (
    APIEndpoint,
    TechStackInfo,
    TestPattern,
    DomainTerm,
)

logger = logging.getLogger(__name__)


class IngestionSource(str, Enum):
    """Types of knowledge sources."""
    OPENAPI = "openapi"
    README = "readme"
    EXISTING_TESTS = "existing_tests"
    PACKAGE_JSON = "package_json"
    REQUIREMENTS_TXT = "requirements_txt"
    DOCKERFILE = "dockerfile"


@dataclass
class IngestionResult:
    """Result of a knowledge ingestion operation."""
    source: IngestionSource
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class OpenAPIIngester:
    """
    Ingests OpenAPI/Swagger specifications to extract:
    - API endpoints with methods, paths, parameters
    - Request/response schemas
    - Authentication requirements
    - Domain terms from descriptions
    """

    def ingest(self, spec_path: str) -> IngestionResult:
        """
        Ingest an OpenAPI specification file.

        Args:
            spec_path: Path to OpenAPI JSON or YAML file

        Returns:
            IngestionResult with extracted endpoints and terms
        """
        result = IngestionResult(source=IngestionSource.OPENAPI, success=False)

        try:
            spec = self._load_spec(spec_path)
            if not spec:
                result.errors.append(f"Failed to load spec from {spec_path}")
                return result

            # Extract endpoints
            endpoints = self._extract_endpoints(spec)
            result.data["endpoints"] = endpoints

            # Extract domain terms from descriptions
            terms = self._extract_domain_terms(spec)
            result.data["domain_terms"] = terms

            # Extract auth requirements
            auth = self._extract_auth_requirements(spec)
            result.data["auth_requirements"] = auth

            # Extract API info
            info = spec.get("info", {})
            result.data["api_info"] = {
                "title": info.get("title", "Unknown API"),
                "version": info.get("version", "1.0.0"),
                "description": info.get("description", ""),
            }

            result.success = True
            logger.info(f"Ingested {len(endpoints)} endpoints from OpenAPI spec")

        except Exception as e:
            result.errors.append(f"Error ingesting OpenAPI: {str(e)}")
            logger.exception("OpenAPI ingestion failed")

        return result

    def _load_spec(self, spec_path: str) -> Optional[Dict]:
        """Load OpenAPI spec from JSON or YAML file."""
        path = Path(spec_path)

        if not path.exists():
            return None

        content = path.read_text()

        if path.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(content)
        else:
            return json.loads(content)

    def _extract_endpoints(self, spec: Dict) -> List[APIEndpoint]:
        """Extract API endpoints from OpenAPI spec."""
        endpoints = []
        paths = spec.get("paths", {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    continue

                # Extract parameters
                parameters = []
                for param in details.get("parameters", []):
                    parameters.append({
                        "name": param.get("name"),
                        "in": param.get("in"),
                        "required": param.get("required", False),
                        "type": param.get("schema", {}).get("type", "string"),
                    })

                # Extract request body schema
                request_body = details.get("requestBody", {})
                request_schema = None
                if request_body:
                    content = request_body.get("content", {})
                    json_content = content.get("application/json", {})
                    request_schema = json_content.get("schema", {})

                # Extract response schemas
                response_schemas = {}
                for status, response in details.get("responses", {}).items():
                    content = response.get("content", {})
                    json_content = content.get("application/json", {})
                    if json_content.get("schema"):
                        response_schemas[status] = json_content["schema"]

                # Determine if auth required
                requires_auth = bool(details.get("security", spec.get("security", [])))

                endpoint = APIEndpoint(
                    path=path,
                    method=method.upper(),
                    description=details.get("summary", details.get("description", "")),
                    parameters=parameters,
                    request_schema=request_schema,
                    response_schema=response_schemas.get("200", response_schemas.get("201")),
                    requires_auth=requires_auth,
                )
                endpoints.append(endpoint)

        return endpoints

    def _extract_domain_terms(self, spec: Dict) -> List[DomainTerm]:
        """Extract domain terminology from API descriptions and schemas."""
        terms = []
        seen = set()

        # Extract from component schemas
        schemas = spec.get("components", {}).get("schemas", {})
        for name, schema in schemas.items():
            if name.lower() not in seen:
                terms.append(DomainTerm(
                    term=name,
                    definition=schema.get("description", f"Data model: {name}"),
                    aliases=[],
                    context="api_schema",
                ))
                seen.add(name.lower())

        # Extract from tags
        for tag in spec.get("tags", []):
            name = tag.get("name", "")
            if name.lower() not in seen:
                terms.append(DomainTerm(
                    term=name,
                    definition=tag.get("description", f"API tag: {name}"),
                    aliases=[],
                    context="api_tag",
                ))
                seen.add(name.lower())

        return terms

    def _extract_auth_requirements(self, spec: Dict) -> Dict[str, Any]:
        """Extract authentication requirements from OpenAPI spec."""
        security_schemes = spec.get("components", {}).get("securitySchemes", {})

        auth_info = {
            "schemes": {},
            "global_security": spec.get("security", []),
        }

        for name, scheme in security_schemes.items():
            auth_info["schemes"][name] = {
                "type": scheme.get("type"),
                "scheme": scheme.get("scheme"),
                "bearerFormat": scheme.get("bearerFormat"),
                "flows": scheme.get("flows"),
            }

        return auth_info


class ReadmeIngester:
    """
    Ingests README.md files to extract:
    - Project description
    - Tech stack hints
    - Setup instructions
    - Architecture notes
    """

    def ingest(self, readme_path: str) -> IngestionResult:
        """
        Ingest a README.md file.

        Args:
            readme_path: Path to README.md file

        Returns:
            IngestionResult with extracted information
        """
        result = IngestionResult(source=IngestionSource.README, success=False)

        try:
            path = Path(readme_path)
            if not path.exists():
                result.errors.append(f"README not found: {readme_path}")
                return result

            content = path.read_text()

            # Parse sections
            sections = self._parse_sections(content)
            result.data["sections"] = sections

            # Extract tech stack hints
            tech_hints = self._extract_tech_hints(content)
            result.data["tech_hints"] = tech_hints

            # Extract setup commands
            setup_commands = self._extract_setup_commands(content)
            result.data["setup_commands"] = setup_commands

            # Extract URLs
            urls = self._extract_urls(content)
            result.data["urls"] = urls

            result.success = True
            logger.info(f"Ingested README with {len(sections)} sections")

        except Exception as e:
            result.errors.append(f"Error ingesting README: {str(e)}")
            logger.exception("README ingestion failed")

        return result

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """Parse README into sections by headers."""
        sections = {}
        current_section = "overview"
        current_content = []

        for line in content.split("\n"):
            # Check for headers
            header_match = re.match(r"^(#{1,3})\s+(.+)$", line)
            if header_match:
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                current_section = header_match.group(2).lower().strip()
                current_section = re.sub(r"[^\w\s]", "", current_section)
                current_section = current_section.replace(" ", "_")
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _extract_tech_hints(self, content: str) -> Dict[str, List[str]]:
        """Extract technology hints from README content."""
        hints = {
            "frontend": [],
            "backend": [],
            "database": [],
            "testing": [],
            "devops": [],
        }

        # Common technology patterns
        tech_patterns = {
            "frontend": [
                r"\b(React|Vue|Angular|Svelte|Next\.js|Nuxt)\b",
                r"\b(TypeScript|JavaScript|ES6)\b",
                r"\b(Tailwind|Bootstrap|Material[- ]UI)\b",
            ],
            "backend": [
                r"\b(Django|Flask|FastAPI|Express|Spring|Rails)\b",
                r"\b(Python|Node\.js|Java|Ruby|Go|Rust)\b",
                r"\b(REST|GraphQL|gRPC)\b",
            ],
            "database": [
                r"\b(PostgreSQL|MySQL|MongoDB|Redis|SQLite)\b",
                r"\b(Prisma|SQLAlchemy|Mongoose)\b",
            ],
            "testing": [
                r"\b(Playwright|Cypress|Selenium|Jest|pytest)\b",
                r"\b(Mocha|Jasmine|RSpec|JUnit)\b",
            ],
            "devops": [
                r"\b(Docker|Kubernetes|AWS|GCP|Azure)\b",
                r"\b(GitHub Actions|CircleCI|Jenkins)\b",
            ],
        }

        content_lower = content.lower()

        for category, patterns in tech_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                hints[category].extend(matches)
            hints[category] = list(set(hints[category]))

        return hints

    def _extract_setup_commands(self, content: str) -> List[str]:
        """Extract setup/installation commands from code blocks."""
        commands = []

        # Match code blocks
        code_blocks = re.findall(r"```(?:bash|sh|shell)?\n(.*?)```", content, re.DOTALL)

        for block in code_blocks:
            for line in block.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    # Filter for likely setup commands
                    if any(cmd in line for cmd in ["npm", "pip", "yarn", "pnpm", "docker", "make", "git"]):
                        commands.append(line)

        return commands

    def _extract_urls(self, content: str) -> List[str]:
        """Extract URLs from README."""
        url_pattern = r'https?://[^\s\)\]\>]+'
        urls = re.findall(url_pattern, content)
        return list(set(urls))


class TestPatternIngester:
    """
    Analyzes existing test files to extract:
    - Naming conventions
    - Assertion patterns
    - Fixture usage
    - Test organization
    """

    def ingest(self, test_directory: str) -> IngestionResult:
        """
        Ingest test files from a directory.

        Args:
            test_directory: Path to test directory

        Returns:
            IngestionResult with extracted patterns
        """
        result = IngestionResult(source=IngestionSource.EXISTING_TESTS, success=False)

        try:
            test_dir = Path(test_directory)
            if not test_dir.exists():
                result.errors.append(f"Test directory not found: {test_directory}")
                return result

            # Find test files
            test_files = self._find_test_files(test_dir)
            result.data["test_files_count"] = len(test_files)

            # Analyze patterns
            patterns = []
            naming_conventions = self._analyze_naming(test_files)
            result.data["naming_conventions"] = naming_conventions

            # Extract assertion patterns
            assertion_patterns = self._analyze_assertions(test_files)
            result.data["assertion_patterns"] = assertion_patterns

            # Extract fixture patterns
            fixture_patterns = self._analyze_fixtures(test_files)
            result.data["fixture_patterns"] = fixture_patterns

            # Create TestPattern objects from naming conventions
            for name, pattern_list in naming_conventions.items():
                if pattern_list:  # Only create if we have examples
                    examples = pattern_list if isinstance(pattern_list, list) else [str(pattern_list)]
                    patterns.append(TestPattern(
                        pattern_type="naming",
                        pattern=f"{name}: naming convention",
                        examples=examples[:5],  # Limit to 5 examples
                        frequency=len(examples),
                    ))

            result.data["patterns"] = patterns
            result.success = True
            logger.info(f"Analyzed {len(test_files)} test files")

        except Exception as e:
            result.errors.append(f"Error ingesting tests: {str(e)}")
            logger.exception("Test pattern ingestion failed")

        return result

    def _find_test_files(self, test_dir: Path) -> List[Path]:
        """Find all test files in directory."""
        test_files = []

        # Python test files
        test_files.extend(test_dir.rglob("test_*.py"))
        test_files.extend(test_dir.rglob("*_test.py"))

        # JavaScript/TypeScript test files
        test_files.extend(test_dir.rglob("*.test.js"))
        test_files.extend(test_dir.rglob("*.test.ts"))
        test_files.extend(test_dir.rglob("*.spec.js"))
        test_files.extend(test_dir.rglob("*.spec.ts"))

        return test_files

    def _analyze_naming(self, test_files: List[Path]) -> Dict[str, Any]:
        """Analyze test naming conventions."""
        conventions = {
            "file_patterns": [],
            "function_patterns": [],
            "class_patterns": [],
        }

        for test_file in test_files[:10]:  # Sample first 10 files
            content = test_file.read_text()

            # Extract function names
            if test_file.suffix == ".py":
                func_matches = re.findall(r"def (test_\w+)", content)
                conventions["function_patterns"].extend(func_matches[:5])

                class_matches = re.findall(r"class (Test\w+)", content)
                conventions["class_patterns"].extend(class_matches[:5])
            else:
                # JS/TS patterns
                it_matches = re.findall(r"it\(['\"](.+?)['\"]", content)
                conventions["function_patterns"].extend(it_matches[:5])

                describe_matches = re.findall(r"describe\(['\"](.+?)['\"]", content)
                conventions["class_patterns"].extend(describe_matches[:5])

        # Deduplicate and get examples
        conventions["function_patterns"] = list(set(conventions["function_patterns"]))[:10]
        conventions["class_patterns"] = list(set(conventions["class_patterns"]))[:10]
        conventions["file_patterns"] = [f.name for f in test_files[:5]]

        return conventions

    def _analyze_assertions(self, test_files: List[Path]) -> Dict[str, int]:
        """Analyze assertion patterns used in tests."""
        assertion_counts = {}

        assertion_patterns = [
            (r"\bassert\s+", "assert"),
            (r"\.assertEqual\(", "assertEqual"),
            (r"\.assertTrue\(", "assertTrue"),
            (r"\.assertIn\(", "assertIn"),
            (r"expect\(.+\)\.to", "expect...to"),
            (r"expect\(.+\)\.toBe", "expect...toBe"),
            (r"\.should\.", "should"),
        ]

        for test_file in test_files[:10]:
            content = test_file.read_text()
            for pattern, name in assertion_patterns:
                count = len(re.findall(pattern, content))
                assertion_counts[name] = assertion_counts.get(name, 0) + count

        return assertion_counts

    def _analyze_fixtures(self, test_files: List[Path]) -> Dict[str, Any]:
        """Analyze fixture usage patterns."""
        fixtures = {
            "pytest_fixtures": [],
            "setup_teardown": [],
            "mocks": [],
        }

        for test_file in test_files[:10]:
            if test_file.suffix != ".py":
                continue

            content = test_file.read_text()

            # pytest fixtures
            fixture_matches = re.findall(r"@pytest\.fixture[^\n]*\ndef (\w+)", content)
            fixtures["pytest_fixtures"].extend(fixture_matches)

            # setup/teardown
            if "def setup" in content or "def setUp" in content:
                fixtures["setup_teardown"].append("setup")
            if "def teardown" in content or "def tearDown" in content:
                fixtures["setup_teardown"].append("teardown")

            # mock usage
            if "@mock" in content or "Mock(" in content or "patch(" in content:
                fixtures["mocks"].append(test_file.name)

        fixtures["pytest_fixtures"] = list(set(fixtures["pytest_fixtures"]))
        fixtures["setup_teardown"] = list(set(fixtures["setup_teardown"]))
        fixtures["mocks"] = list(set(fixtures["mocks"]))

        return fixtures


class TechStackDetector:
    """
    Detects technology stack from project files:
    - package.json (Node.js projects)
    - requirements.txt / pyproject.toml (Python projects)
    - Dockerfile
    - CI/CD config files
    """

    def detect(self, project_root: str) -> TechStackInfo:
        """
        Detect tech stack from project files.

        Args:
            project_root: Path to project root directory

        Returns:
            TechStackInfo with detected technologies
        """
        root = Path(project_root)

        frontend = self._detect_frontend(root)
        backend = self._detect_backend(root)
        database = self._detect_database(root)
        testing = self._detect_testing(root)
        ci_cd = self._detect_cicd(root)

        return TechStackInfo(
            frontend=frontend or "Unknown",
            backend=backend or "Unknown",
            database=database or "Unknown",
            testing=testing or "Unknown",
            ci_cd=ci_cd or "Unknown",
        )

    def _detect_frontend(self, root: Path) -> Optional[str]:
        """Detect frontend framework."""
        package_json = root / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                if "react" in deps:
                    version = deps.get("react", "")
                    return f"React {version}".strip()
                elif "vue" in deps:
                    return f"Vue {deps.get('vue', '')}".strip()
                elif "angular" in deps or "@angular/core" in deps:
                    return f"Angular {deps.get('@angular/core', '')}".strip()
                elif "svelte" in deps:
                    return f"Svelte {deps.get('svelte', '')}".strip()
                elif "next" in deps:
                    return f"Next.js {deps.get('next', '')}".strip()
            except Exception:
                pass

        return None

    def _detect_backend(self, root: Path) -> Optional[str]:
        """Detect backend framework."""
        # Check Python
        requirements = root / "requirements.txt"
        pyproject = root / "pyproject.toml"

        python_deps = ""
        if requirements.exists():
            python_deps = requirements.read_text().lower()
        elif pyproject.exists():
            python_deps = pyproject.read_text().lower()

        if python_deps:
            if "django" in python_deps:
                return "Django"
            elif "fastapi" in python_deps:
                return "FastAPI"
            elif "flask" in python_deps:
                return "Flask"

        # Check Node.js
        package_json = root / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                if "express" in deps:
                    return f"Express.js {deps.get('express', '')}".strip()
                elif "fastify" in deps:
                    return f"Fastify {deps.get('fastify', '')}".strip()
                elif "nest" in deps or "@nestjs/core" in deps:
                    return "NestJS"
            except Exception:
                pass

        return None

    def _detect_database(self, root: Path) -> Optional[str]:
        """Detect database from config files."""
        databases = []

        # Check docker-compose
        docker_compose = root / "docker-compose.yml"
        if docker_compose.exists():
            content = docker_compose.read_text().lower()
            if "postgres" in content:
                databases.append("PostgreSQL")
            if "mysql" in content:
                databases.append("MySQL")
            if "mongo" in content:
                databases.append("MongoDB")
            if "redis" in content:
                databases.append("Redis")

        # Check Python dependencies
        requirements = root / "requirements.txt"
        if requirements.exists():
            content = requirements.read_text().lower()
            if "psycopg" in content:
                databases.append("PostgreSQL")
            if "pymysql" in content or "mysqlclient" in content:
                databases.append("MySQL")
            if "pymongo" in content:
                databases.append("MongoDB")

        return ", ".join(databases) if databases else None

    def _detect_testing(self, root: Path) -> Optional[str]:
        """Detect testing framework."""
        testing_tools = []

        # Check Python
        requirements = root / "requirements.txt"
        if requirements.exists():
            content = requirements.read_text().lower()
            if "pytest" in content:
                testing_tools.append("pytest")
            if "playwright" in content:
                testing_tools.append("Playwright")
            if "selenium" in content:
                testing_tools.append("Selenium")

        # Check Node.js
        package_json = root / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                if "playwright" in deps or "@playwright/test" in deps:
                    testing_tools.append("Playwright")
                if "cypress" in deps:
                    testing_tools.append("Cypress")
                if "jest" in deps:
                    testing_tools.append("Jest")
            except Exception:
                pass

        return " + ".join(testing_tools) if testing_tools else None

    def _detect_cicd(self, root: Path) -> Optional[str]:
        """Detect CI/CD configuration."""
        ci_tools = []

        if (root / ".github" / "workflows").exists():
            ci_tools.append("GitHub Actions")
        if (root / ".gitlab-ci.yml").exists():
            ci_tools.append("GitLab CI")
        if (root / "Jenkinsfile").exists():
            ci_tools.append("Jenkins")
        if (root / ".circleci").exists():
            ci_tools.append("CircleCI")
        if (root / "azure-pipelines.yml").exists():
            ci_tools.append("Azure DevOps")

        return ", ".join(ci_tools) if ci_tools else None


class KnowledgeIngester:
    """
    Main class for ingesting knowledge from multiple sources.
    Coordinates the various specialized ingesters.
    """

    def __init__(self):
        self.openapi_ingester = OpenAPIIngester()
        self.readme_ingester = ReadmeIngester()
        self.test_pattern_ingester = TestPatternIngester()
        self.tech_stack_detector = TechStackDetector()

    def ingest_all(self, project_root: str) -> Dict[str, IngestionResult]:
        """
        Ingest knowledge from all available sources in a project.

        Args:
            project_root: Path to project root

        Returns:
            Dict of source name to IngestionResult
        """
        root = Path(project_root)
        results = {}

        # Detect tech stack
        tech_stack = self.tech_stack_detector.detect(project_root)
        results["tech_stack"] = IngestionResult(
            source=IngestionSource.REQUIREMENTS_TXT,
            success=True,
            data={"tech_stack": tech_stack},
        )

        # Ingest README
        readme_paths = [
            root / "README.md",
            root / "readme.md",
            root / "README.rst",
        ]
        for readme_path in readme_paths:
            if readme_path.exists():
                results["readme"] = self.readme_ingester.ingest(str(readme_path))
                break

        # Ingest OpenAPI specs
        openapi_paths = [
            root / "openapi.json",
            root / "openapi.yaml",
            root / "swagger.json",
            root / "swagger.yaml",
            root / "docs" / "openapi.json",
            root / "api" / "openapi.json",
        ]
        for spec_path in openapi_paths:
            if spec_path.exists():
                results["openapi"] = self.openapi_ingester.ingest(str(spec_path))
                break

        # Ingest test patterns
        test_dirs = [
            root / "tests",
            root / "test",
            root / "e2e",
            root / "__tests__",
        ]
        for test_dir in test_dirs:
            if test_dir.exists():
                results["tests"] = self.test_pattern_ingester.ingest(str(test_dir))
                break

        return results

    async def ingest_openapi_url(self, url: str) -> IngestionResult:
        """
        Ingest OpenAPI spec from a URL.

        Args:
            url: URL to OpenAPI specification

        Returns:
            IngestionResult with extracted data
        """
        import aiohttp

        result = IngestionResult(source=IngestionSource.OPENAPI, success=False)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        result.errors.append(f"Failed to fetch OpenAPI: HTTP {response.status}")
                        return result

                    content = await response.text()

                    # Try to parse as JSON first, then YAML
                    try:
                        spec = json.loads(content)
                    except json.JSONDecodeError:
                        spec = yaml.safe_load(content)

                    # Use the same extraction logic
                    endpoints = self.openapi_ingester._extract_endpoints(spec)
                    terms = self.openapi_ingester._extract_domain_terms(spec)
                    auth = self.openapi_ingester._extract_auth_requirements(spec)

                    result.data = {
                        "endpoints": endpoints,
                        "domain_terms": terms,
                        "auth_requirements": auth,
                        "api_info": spec.get("info", {}),
                    }
                    result.success = True

        except Exception as e:
            result.errors.append(f"Error fetching OpenAPI: {str(e)}")
            logger.exception("OpenAPI URL ingestion failed")

        return result
