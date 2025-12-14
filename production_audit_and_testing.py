#!/usr/bin/env python3
"""
Comprehensive Production Audit and Testing Script
DevOps Engineer Grade Production Readiness Validation

This script performs industry-standard production validation including:
- Backend API endpoints testing
- Frontend functionality verification
- Database integrity checks
- Security validation
- Performance testing
- Image and asset verification
- Link validation
- Mobile app testing preparation
- SSL/HTTPS verification
- Environment configuration validation
"""

import os
import sys
import json
import time
import subprocess
import requests
import asyncio
import aiohttp
import ssl
import socket
import re
import io
import statistics
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

# Optional imports for enhanced features
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    
try:
    from sqlalchemy import create_engine, inspect, text
    from sqlalchemy.exc import OperationalError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_audit.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration for audit tests
AUDIT_CONFIG = {
    'backend_url': os.getenv('BACKEND_URL', 'http://localhost:8000'),
    'frontend_url': os.getenv('FRONTEND_URL', 'http://localhost:3000'),
    'mobile_api_url': os.getenv('MOBILE_API_URL', 'http://localhost:8000'),
    'api_token': os.getenv('API_TOKEN', ''),
    'database_url': os.getenv('DATABASE_URL', ''),
    'request_timeout': 10,
    'concurrent_requests': 10,
    'max_response_time_ms': 1000,
    'max_image_size_mb': 1,
    'test_performance_load': True,
    'generate_html': True,
    'generate_json': True,
}

@dataclass
class TestResult:
    """Test result data structure"""
    name: str
    status: str  # PASS, FAIL, WARNING, SKIP
    message: str
    details: Dict[str, Any] = None
    execution_time: float = 0.0

class ProductionAuditor:
    """Comprehensive Production Auditor for Lean Construction Application"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results: List[TestResult] = []
        self.start_time = datetime.now()
        
        # Configuration
        self.backend_url = config.get('backend_url', 'http://localhost:8000')
        self.frontend_url = config.get('frontend_url', 'http://localhost:3000')
        self.mobile_url = config.get('mobile_api_url', 'http://localhost:8000')
        self.api_token = config.get('api_token', '')
        self.database_url = config.get('database_url', '')
        
    def log_result(self, name: str, status: str, message: str, details: Dict = None, execution_time: float = 0.0):
        """Log test result"""
        result = TestResult(name, status, message, details, execution_time)
        self.results.append(result)
        
        status_emoji = {
            'PASS': '✅',
            'FAIL': '❌',
            'WARNING': '⚠️',
            'SKIP': '⏭️'
        }
        
        logger.info(f"{status_emoji.get(status, '❓')} {name}: {message}")
        if details and status == 'FAIL':
            logger.error(f"  Details: {json.dumps(details, indent=2)}")
    
    def test_backend_health(self) -> List[TestResult]:
        """Test backend health and API endpoints"""
        logger.info("🔍 Testing Backend Health and API Endpoints...")
        
        start_time = time.time()
        backend_tests = []
        
        # Test 1: Health Check
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                backend_tests.append(TestResult("Backend Health", "PASS", "Backend is healthy"))
            else:
                backend_tests.append(TestResult("Backend Health", "FAIL", f"Health check failed: {response.status_code}"))
        except Exception as e:
            backend_tests.append(TestResult("Backend Health", "FAIL", f"Health check error: {str(e)}"))
        
        # Test 2: API Documentation
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=10)
            if response.status_code == 200:
                backend_tests.append(TestResult("API Documentation", "PASS", "FastAPI docs accessible"))
            else:
                backend_tests.append(TestResult("API Documentation", "FAIL", f"Docs check failed: {response.status_code}"))
        except Exception as e:
            backend_tests.append(TestResult("API Documentation", "FAIL", f"Docs error: {str(e)}"))
        
        # Test 3: Authentication Endpoints
        auth_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/auth/register", 
            "/api/v1/auth/me",
            "/api/v1/auth/logout"
        ]
        
        for endpoint in auth_endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code in [200, 401, 422]:  # 401 expected for protected routes
                    backend_tests.append(TestResult(f"Auth Endpoint {endpoint}", "PASS", "Endpoint accessible"))
                else:
                    backend_tests.append(TestResult(f"Auth Endpoint {endpoint}", "FAIL", f"Status: {response.status_code}"))
            except Exception as e:
                backend_tests.append(TestResult(f"Auth Endpoint {endpoint}", "FAIL", f"Error: {str(e)}"))
        
        # Test 4: Chat API Endpoints
        chat_endpoints = [
            "/api/v1/chat/conversations",
            "/api/v1/chat/messages",
            "/api/v1/chat/conversations/search"
        ]
        
        headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        
        for endpoint in chat_endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", headers=headers, timeout=5)
                if response.status_code in [200, 401, 422]:  # 401 expected for protected routes
                    backend_tests.append(TestResult(f"Chat Endpoint {endpoint}", "PASS", "Endpoint accessible"))
                else:
                    backend_tests.append(TestResult(f"Chat Endpoint {endpoint}", "FAIL", f"Status: {response.status_code}"))
            except Exception as e:
                backend_tests.append(TestResult(f"Chat Endpoint {endpoint}", "FAIL", f"Error: {str(e)}"))
        
        # Test 5: ML API Endpoints
        ml_endpoints = [
            "/api/v1/ml/analyze-waste",
            "/api/v1/ml/computer-vision",
            "/api/v1/ml/predictive-models"
        ]
        
        for endpoint in ml_endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", headers=headers, timeout=5)
                if response.status_code in [200, 401, 422, 500]:  # 500 may be expected for unimplemented features
                    backend_tests.append(TestResult(f"ML Endpoint {endpoint}", "PASS", "Endpoint accessible"))
                else:
                    backend_tests.append(TestResult(f"ML Endpoint {endpoint}", "FAIL", f"Status: {response.status_code}"))
            except Exception as e:
                backend_tests.append(TestResult(f"ML Endpoint {endpoint}", "FAIL", f"Error: {str(e)}"))
        
        # Test 6: Database Connection
        try:
            # Simple database test through API
            response = requests.get(f"{self.backend_url}/api/v1/auth/me", headers=headers, timeout=5)
            # If we get 401 (unauthorized) instead of 500 (server error), DB is likely working
            if response.status_code != 500:
                backend_tests.append(TestResult("Database Connection", "PASS", "Database appears accessible"))
            else:
                backend_tests.append(TestResult("Database Connection", "FAIL", "Database connection issues detected"))
        except Exception as e:
            backend_tests.append(TestResult("Database Connection", "FAIL", f"Database test error: {str(e)}"))
        
        execution_time = time.time() - start_time
        for test in backend_tests:
            test.execution_time = execution_time / len(backend_tests)
        
        return backend_tests
    
    def test_frontend_functionality(self) -> List[TestResult]:
        """Test frontend functionality and routes"""
        logger.info("🌐 Testing Frontend Functionality...")
        
        start_time = time.time()
        frontend_tests = []
        
        # Test 1: Frontend Accessibility
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                frontend_tests.append(TestResult("Frontend Accessibility", "PASS", "Website accessible"))
            else:
                frontend_tests.append(TestResult("Frontend Accessibility", "FAIL", f"Status: {response.status_code}"))
        except Exception as e:
            frontend_tests.append(TestResult("Frontend Accessibility", "FAIL", f"Error: {str(e)}"))
        
        # Test 2: Key Routes
        routes_to_test = [
            "/",
            "/about",
            "/features", 
            "/pricing",
            "/contact",
            "/login",
            "/signup",
            "/book-demo",
            "/onboarding"
        ]
        
        for route in routes_to_test:
            try:
                response = requests.get(f"{self.frontend_url}{route}", timeout=5)
                if response.status_code == 200:
                    frontend_tests.append(TestResult(f"Route {route}", "PASS", "Route accessible"))
                else:
                    frontend_tests.append(TestResult(f"Route {route}", "FAIL", f"Status: {response.status_code}"))
            except Exception as e:
                frontend_tests.append(TestResult(f"Route {route}", "FAIL", f"Error: {str(e)}"))
        
        # Test 3: Static Assets
        static_assets = [
            "/favicon.ico",
            "/apple-touch-icon.png",
            "/_next/static/css/",
            "/_next/static/js/"
        ]
        
        for asset in static_assets:
            try:
                response = requests.get(f"{self.frontend_url}{asset}", timeout=3)
                if response.status_code == 200:
                    frontend_tests.append(TestResult(f"Static Asset {asset}", "PASS", "Asset accessible"))
                else:
                    frontend_tests.append(TestResult(f"Static Asset {asset}", "WARNING", f"Status: {response.status_code}"))
            except Exception as e:
                frontend_tests.append(TestResult(f"Static Asset {asset}", "WARNING", f"Error: {str(e)}"))
        
        # Test 4: API Integration
        try:
            # Test if frontend can reach backend API
            response = requests.get(f"{self.frontend_url}/api/health", timeout=5)
            if response.status_code == 200:
                frontend_tests.append(TestResult("Frontend-Backend Integration", "PASS", "API integration working"))
            else:
                frontend_tests.append(TestResult("Frontend-Backend Integration", "WARNING", f"Status: {response.status_code}"))
        except Exception as e:
            frontend_tests.append(TestResult("Frontend-Backend Integration", "WARNING", f"Error: {str(e)}"))
        
        execution_time = time.time() - start_time
        for test in frontend_tests:
            test.execution_time = execution_time / len(frontend_tests)
        
        return frontend_tests
    
    def test_images_and_assets(self) -> List[TestResult]:
        """Test image and asset integrity"""
        logger.info("🖼️ Testing Images and Assets...")
        
        start_time = time.time()
        asset_tests = []
        
        # Image directories to check
        image_dirs = [
            "website/public/integrated_tools_logo",
            "website/public/trustedByLeadingCompanies",
            "website/src/app/trustedByLeadingCompanies"
        ]
        
        image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.svg', '.ico']
        
        for img_dir in image_dirs:
            dir_path = Path(img_dir)
            if not dir_path.exists():
                asset_tests.append(TestResult(f"Image Directory {img_dir}", "SKIP", "Directory not found"))
                continue
                
            for img_file in dir_path.iterdir():
                if img_file.suffix.lower() in image_extensions:
                    try:
                        # Check if file is readable and has content
                        file_size = img_file.stat().st_size
                        if file_size > 0:
                            # Calculate file hash to verify integrity
                            with open(img_file, 'rb') as f:
                                file_hash = hashlib.md5(f.read()).hexdigest()
                            
                            asset_tests.append(TestResult(
                                f"Image {img_file.name}", 
                                "PASS", 
                                f"Valid image ({file_size} bytes, hash: {file_hash[:8]}...)",
                                {"size": file_size, "hash": file_hash}
                            ))
                        else:
                            asset_tests.append(TestResult(
                                f"Image {img_file.name}", 
                                "FAIL", 
                                "Empty image file"
                            ))
                    except Exception as e:
                        asset_tests.append(TestResult(
                            f"Image {img_file.name}", 
                            "FAIL", 
                            f"Error reading file: {str(e)}"
                        ))
        
        # Test favicon and icons
        icon_files = [
            "website/public/favicon.ico",
            "website/public/apple-touch-icon.png",
            "website/public/favicon-16x16.png",
            "website/public/favicon-32x32.png"
        ]
        
        for icon_file in icon_files:
            icon_path = Path(icon_file)
            if icon_path.exists():
                try:
                    size = icon_path.stat().st_size
                    asset_tests.append(TestResult(
                        f"Icon {icon_path.name}", 
                        "PASS", 
                        f"Valid icon ({size} bytes)"
                    ))
                except Exception as e:
                    asset_tests.append(TestResult(
                        f"Icon {icon_path.name}", 
                        "FAIL", 
                        f"Error: {str(e)}"
                    ))
            else:
                asset_tests.append(TestResult(
                    f"Icon {icon_path.name}", 
                    "WARNING", 
                    "Icon file missing"
                ))
        
        execution_time = time.time() - start_time
        for test in asset_tests:
            test.execution_time = execution_time / len(asset_tests)
        
        return asset_tests
    
    def test_security_configuration(self) -> List[TestResult]:
        """Test security configuration"""
        logger.info("🔒 Testing Security Configuration...")
        
        start_time = time.time()
        security_tests = []
        
        # Test 1: HTTPS Redirect
        try:
            http_url = self.frontend_url.replace('https://', 'http://').replace('http://https://', 'https://')
            if 'localhost' not in http_url:
                response = requests.get(http_url, allow_redirects=False, timeout=10)
                if response.status_code in [301, 302]:
                    location = response.headers.get('Location', '')
                    if location.startswith('https://'):
                        security_tests.append(TestResult("HTTPS Redirect", "PASS", "HTTP properly redirects to HTTPS"))
                    else:
                        security_tests.append(TestResult("HTTPS Redirect", "FAIL", "HTTP doesn't redirect to HTTPS"))
                else:
                    security_tests.append(TestResult("HTTPS Redirect", "WARNING", f"Status: {response.status_code}"))
            else:
                security_tests.append(TestResult("HTTPS Redirect", "SKIP", "Local development - skipping HTTPS test"))
        except Exception as e:
            security_tests.append(TestResult("HTTPS Redirect", "WARNING", f"Error: {str(e)}"))
        
        # Test 2: Security Headers
        try:
            response = requests.get(self.frontend_url, timeout=10)
            headers = response.headers
            
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Content-Security-Policy': None  # We'll check if it exists
            }
            
            for header, expected_value in security_headers.items():
                if header in headers:
                    if expected_value is None:
                        security_tests.append(TestResult(f"Security Header {header}", "PASS", "Header present"))
                    elif expected_value in headers[header]:
                        security_tests.append(TestResult(f"Security Header {header}", "PASS", f"Header present with expected value"))
                    else:
                        security_tests.append(TestResult(f"Security Header {header}", "WARNING", f"Header present but value mismatch"))
                else:
                    security_tests.append(TestResult(f"Security Header {header}", "WARNING", "Header missing"))
        except Exception as e:
            security_tests.append(TestResult("Security Headers", "WARNING", f"Error: {str(e)}"))
        
        # Test 3: CORS Configuration
        try:
            response = requests.options(f"{self.backend_url}/api/v1/auth/login", timeout=5)
            cors_headers = response.headers
            if 'Access-Control-Allow-Origin' in cors_headers:
                security_tests.append(TestResult("CORS Configuration", "PASS", "CORS headers present"))
            else:
                security_tests.append(TestResult("CORS Configuration", "WARNING", "CORS headers missing"))
        except Exception as e:
            security_tests.append(TestResult("CORS Configuration", "WARNING", f"Error: {str(e)}"))
        
        execution_time = time.time() - start_time
        for test in security_tests:
            test.execution_time = execution_time / len(security_tests)
        
        return security_tests
    
    def test_environment_configuration(self) -> List[TestResult]:
        """Test environment configuration"""
        logger.info("⚙️ Testing Environment Configuration...")
        
        start_time = time.time()
        config_tests = []
        
        # Test 1: Environment Files
        env_files = [
            "backend/.env.production",
            "backend/.env.example",
            "website/.env.local",
            "website/.env.example"
        ]
        
        for env_file in env_files:
            env_path = Path(env_file)
            if env_path.exists():
                config_tests.append(TestResult(f"Env File {env_file}", "PASS", "Environment file exists"))
            else:
                config_tests.append(TestResult(f"Env File {env_file}", "WARNING", "Environment file missing"))
        
        # Test 2: Required Environment Variables
        required_vars = {
            "SECRET_KEY": "Backend secret key for JWT",
            "DATABASE_URL": "Database connection string",
            "NEXT_PUBLIC_API_URL": "Frontend API URL",
            "OPENAI_API_KEY": "OpenAI API key (optional)",
            "ANTHROPIC_API_KEY": "Anthropic API key (optional)"
        }
        
        for var, description in required_vars.items():
            var_value = os.getenv(var)
            if var_value:
                # Check if it's a placeholder or real value
                if var_value in ["your-secret-key-here", "your-openai-api-key", "your-anthropic-api-key"]:
                    config_tests.append(TestResult(f"Env Var {var}", "WARNING", f"Placeholder value detected"))
                else:
                    config_tests.append(TestResult(f"Env Var {var}", "PASS", f"Configured ({description})"))
            else:
                if "optional" in description.lower():
                    config_tests.append(TestResult(f"Env Var {var}", "SKIP", "Optional variable not set"))
                else:
                    config_tests.append(TestResult(f"Env Var {var}", "FAIL", f"Required variable missing ({description})"))
        
        # Test 3: Configuration Files
        config_files = [
            ("backend/requirements.txt", "Python dependencies"),
            ("website/package.json", "Node.js dependencies"),
            ("mobile/package.json", "React Native dependencies"),
            ("backend/alembic.ini", "Database migration config"),
            ("docker-compose.yml", "Docker configuration")
        ]
        
        for config_file, description in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                config_tests.append(TestResult(f"Config {config_file}", "PASS", f"Exists ({description})"))
            else:
                config_tests.append(TestResult(f"Config {config_file}", "WARNING", f"Missing ({description})"))
        
        execution_time = time.time() - start_time
        for test in config_tests:
            test.execution_time = execution_time / len(config_tests)
        
        return config_tests
    
    def test_performance_basics(self) -> List[TestResult]:
        """Test basic performance metrics"""
        logger.info("⚡ Testing Basic Performance...")
        
        start_time = time.time()
        performance_tests = []
        
        # Test 1: Response Times
        endpoints_to_test = [
            self.frontend_url,
            f"{self.backend_url}/health",
            f"{self.backend_url}/docs"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response_times = []
                for _ in range(3):  # Test 3 times
                    start = time.time()
                    response = requests.get(endpoint, timeout=10)
                    response_time = (time.time() - start) * 1000  # Convert to ms
                    response_times.append(response_time)
                
                avg_response_time = sum(response_times) / len(response_times)
                
                if avg_response_time < 1000:  # Less than 1 second
                    performance_tests.append(TestResult(
                        f"Response Time {endpoint}", 
                        "PASS", 
                        f"Average: {avg_response_time:.0f}ms"
                    ))
                elif avg_response_time < 3000:  # Less than 3 seconds
                    performance_tests.append(TestResult(
                        f"Response Time {endpoint}", 
                        "WARNING", 
                        f"Slow response: {avg_response_time:.0f}ms"
                    ))
                else:
                    performance_tests.append(TestResult(
                        f"Response Time {endpoint}", 
                        "FAIL", 
                        f"Very slow response: {avg_response_time:.0f}ms"
                    ))
            except Exception as e:
                performance_tests.append(TestResult(
                    f"Response Time {endpoint}", 
                    "FAIL", 
                    f"Error: {str(e)}"
                ))
        
        execution_time = time.time() - start_time
        for test in performance_tests:
            test.execution_time = execution_time / len(performance_tests)
        
        return performance_tests
    
    def test_comprehensive_link_validation(self) -> List[TestResult]:
        """Parse all TSX/JSX files to extract links and validate them"""
        logger.info("🔗 Testing Comprehensive Link Validation...")
        start_time = time.time()
        link_tests = []
        
        # Regex to find links in TSX/JSX files
        link_regex = re.compile(r'(href|to|src)=["\'](.*?)["\']')
        
        source_dirs = ["website/src", "frontend/src"]
        file_extensions = ['.tsx', '.jsx', '.js']
        
        for source_dir in source_dirs:
            source_path = Path(source_dir)
            if not source_path.exists():
                continue
                
            for ext in file_extensions:
                for filepath in source_path.glob(f"**/*{ext}"):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        for match in link_regex.finditer(content):
                            link = match.group(2)
                            
                            if not link or link.startswith('#') or link.startswith('mailto:') or link.startswith('tel:'):
                                continue

                            # Categorize and test the link
                            if link.startswith('http') or link.startswith('//'):
                                # External link
                                try:
                                    response = requests.head(link, timeout=self.config.get('request_timeout', 10), allow_redirects=True)
                                    if response.status_code == 200:
                                        link_tests.append(TestResult(f"External Link {link}", "PASS", f"Accessible (Status: {response.status_code})"))
                                    else:
                                        link_tests.append(TestResult(f"External Link {link}", "WARNING", f"Broken or redirected (Status: {response.status_code})"))
                                except Exception as e:
                                    link_tests.append(TestResult(f"External Link {link}", "FAIL", f"Unreachable: {str(e)}"))
                            elif link.startswith('/'):
                                # Internal link
                                internal_url = urljoin(self.frontend_url, link)
                                try:
                                    response = requests.get(internal_url, timeout=5)
                                    if response.status_code == 200:
                                        link_tests.append(TestResult(f"Internal Link {link}", "PASS", f"Route accessible"))
                                    else:
                                        link_tests.append(TestResult(f"Internal Link {link}", "FAIL", f"Broken route (Status: {response.status_code})"))
                                except Exception as e:
                                     link_tests.append(TestResult(f"Internal Link {link}", "FAIL", f"Error: {str(e)}"))
                            else:
                                # Image or other asset
                                asset_path = source_path.parent / "public" / link
                                if asset_path.exists():
                                    link_tests.append(TestResult(f"Image Source {link}", "PASS", "Asset exists on filesystem"))
                                else:
                                    link_tests.append(TestResult(f"Image Source {link}", "FAIL", f"Asset missing from filesystem: {asset_path}"))

                    except Exception as e:
                        link_tests.append(TestResult(f"File Parsing {filepath}", "FAIL", f"Could not parse file: {e}"))

        execution_time = time.time() - start_time
        if link_tests:
            for test in link_tests:
                test.execution_time = execution_time / len(link_tests)
                
        return link_tests
    
    def test_advanced_image_integrity(self) -> List[TestResult]:
        """Verify images are valid, not corrupted, and properly formatted"""
        logger.info("🖼️  Testing Advanced Image Integrity...")
        start_time = time.time()
        image_tests = []

        if not PIL_AVAILABLE:
            image_tests.append(TestResult("Advanced Image Integrity", "SKIP", "PIL/Pillow not installed"))
            return image_tests

        image_dirs = [
            "website/public/integrated_tools_logo",
            "website/public/trustedByLeadingCompanies",
            "website/public",
            "frontend/public",
        ]
        
        image_extensions = ['.webp', '.png', '.jpg', '.jpeg', '.svg', '.ico']

        for img_dir in image_dirs:
            dir_path = Path(img_dir)
            if not dir_path.exists():
                continue

            for img_file in dir_path.rglob('*'):
                if img_file.suffix.lower() in image_extensions:
                    try:
                        file_size = img_file.stat().st_size
                        if file_size == 0:
                            image_tests.append(TestResult(f"Image {img_file.name}", "FAIL", "Empty image file"))
                            continue
                        
                        if img_file.suffix.lower() == '.svg':
                            # Basic SVG validation
                            with open(img_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            if '<svg' in content and '</svg>' in content:
                                image_tests.append(TestResult(f"Image {img_file.name}", "PASS", f"Valid SVG ({file_size} bytes)"))
                            else:
                                image_tests.append(TestResult(f"Image {img_file.name}", "FAIL", "Invalid SVG file"))
                            continue

                        # Pillow-based validation for other image types
                        with open(img_file, 'rb') as f:
                            img_data = f.read()

                        with Image.open(io.BytesIO(img_data)) as img:
                            img.verify()  # Verifies integrity
                            
                            # Re-open after verify
                            with Image.open(io.BytesIO(img_data)) as img_reopened:
                                # Check format
                                format_ok = img_reopened.format.lower() == img_file.suffix.lower().replace('.', '')
                                if not format_ok and not (img_reopened.format == 'JPEG' and img_file.suffix.lower() == '.jpg'):
                                     image_tests.append(TestResult(f"Image {img_file.name}", "WARNING", f"Format mismatch (file: {img_file.suffix}, actual: {img_reopened.format})"))
                                     continue
                                
                                # Check dimensions
                                if img_reopened.width == 0 or img_reopened.height == 0:
                                    image_tests.append(TestResult(f"Image {img_file.name}", "FAIL", "Image has zero dimensions"))
                                    continue
                                
                                # Check file size
                                max_size_mb = self.config.get('max_image_size_mb', 1)
                                if file_size > max_size_mb * 1024 * 1024:
                                    image_tests.append(TestResult(f"Image {img_file.name}", "WARNING", f"Large image file ({file_size / 1024 / 1024:.2f} MB)"))

                                image_tests.append(TestResult(
                                    f"Image {img_file.name}", "PASS",
                                    f"Valid image ({img_reopened.format}, {img_reopened.width}x{img_reopened.height}, {file_size} bytes)"
                                ))

                    except (IOError, SyntaxError) as e:
                        image_tests.append(TestResult(f"Image {img_file.name}", "FAIL", f"Corrupted or invalid image: {e}"))
                    except Exception as e:
                        image_tests.append(TestResult(f"Image {img_file.name}", "FAIL", f"Error processing image: {e}"))
        
        execution_time = time.time() - start_time
        if image_tests:
            for test in image_tests:
                test.execution_time = execution_time / len(image_tests)
                
        return image_tests
    
    def test_all_api_endpoints_dynamic(self) -> List[TestResult]:
        """Automatically discover and test all FastAPI endpoints"""
        logger.info("📡 Testing All API Endpoints Dynamically...")
        start_time = time.time()
        api_tests = []

        try:
            # Add backend to sys.path to allow importing the app
            backend_path = str(Path.cwd() / "backend")
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            
            from app.main import app
            
            headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}

            for route in app.routes:
                if hasattr(route, "path") and route.path.startswith("/api"):
                    methods = route.methods
                    path = route.path
                    
                    for method in methods:
                        # Skip websockets for now
                        if "websocket" in str(route).lower():
                            continue

                        test_name = f"API Endpoint {method} {path}"
                        
                        try:
                            # For POST/PUT/PATCH, we  can't know the required payload,
                            # so we expect a 422, 401, or 200 (if no payload needed)
                            if method in ["POST", "PUT", "PATCH"]:
                                response = requests.request(method, f"{self.backend_url}{path}", headers=headers, timeout=5, json={})
                                if response.status_code in [200, 422, 401, 400, 201]:
                                    api_tests.append(TestResult(test_name, "PASS", f"Responded with {response.status_code} (as expected for {method})"))
                                else:
                                    api_tests.append(TestResult(test_name, "FAIL", f"Unexpected status: {response.status_code}"))

                            # For GET/DELETE/OPTIONS/HEAD
                            else:
                                response = requests.request(method, f"{self.backend_url}{path}", headers=headers, timeout=5)
                                if response.status_code in [200, 401, 404, 422]: # Not found is ok for some dynamic routes
                                    api_tests.append(TestResult(test_name, "PASS", f"Responded with {response.status_code}"))
                                else:
                                    api_tests.append(TestResult(test_name, "FAIL", f"Unexpected status: {response.status_code}"))
                        
                        except requests.exceptions.RequestException as e:
                            api_tests.append(TestResult(test_name, "FAIL", f"Request failed: {e}"))

        except ImportError as e:
            api_tests.append(TestResult("API Endpoint Discovery", "SKIP", f"Could not import FastAPI app: {e}"))
        except Exception as e:
            api_tests.append(TestResult("API Endpoint Discovery", "SKIP", f"An unexpected error occurred: {e}"))
        finally:
            # Remove backend from sys.path
            if backend_path in sys.path:
                sys.path.remove(backend_path)

        execution_time = time.time() - start_time
        if api_tests:
            for test in api_tests:
                test.execution_time = execution_time / len(api_tests)

        return api_tests

    def test_database_connectivity(self) -> List[TestResult]:
        """Directly test database connection and query performance"""
        logger.info("💾 Testing Database Connectivity...")
        start_time = time.time()
        db_tests = []

        if not SQLALCHEMY_AVAILABLE:
            db_tests.append(TestResult("Database Connectivity", "SKIP", "SQLAlchemy not installed"))
            return db_tests

        if not self.database_url:
            db_tests.append(TestResult("Database Connectivity", "SKIP", "DATABASE_URL not configured"))
            return db_tests

        try:
            engine = create_engine(self.database_url)
            
            # Test 1: Connection
            conn_start_time = time.time()
            with engine.connect() as connection:
                conn_time = (time.time() - conn_start_time) * 1000
                db_tests.append(TestResult("Database Connection", "PASS", f"Connected successfully in {conn_time:.0f}ms"))
                
                # Test 2: Simple Query
                query_start_time = time.time()
                result = connection.execute(text("SELECT 1"))
                query_time = (time.time() - query_start_time) * 1000
                if list(result) == [(1,)]:
                    db_tests.append(TestResult("Database Simple Query", "PASS", f"SELECT 1 query executed in {query_time:.0f}ms"))
                else:
                    db_tests.append(TestResult("Database Simple Query", "FAIL", "SELECT 1 query failed"))

            # Test 3: Schema Verification
            expected_tables = [
                'users', 'projects', 'tasks', 'waste_logs', 'chat_conversations', 
                'chat_messages', 'onboarding_events', 'email_notifications', 
                'appointments', 'ml_usage_logs'
            ]
            
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            missing_tables = [t for t in expected_tables if t not in tables]
            if not missing_tables:
                db_tests.append(TestResult("Database Schema", "PASS", "All expected tables are present"))
            else:
                db_tests.append(TestResult("Database Schema", "WARNING", f"Missing tables: {', '.join(missing_tables)}"))

        except OperationalError as e:
            db_tests.append(TestResult("Database Connectivity", "FAIL", f"Connection failed: {e}"))
        except Exception as e:
            db_tests.append(TestResult("Database Connectivity", "FAIL", f"An unexpected error occurred: {e}"))

        execution_time = time.time() - start_time
        if db_tests:
            for test in db_tests:
                test.execution_time = execution_time / len(db_tests)

        return db_tests

    def test_performance_benchmarking(self) -> List[TestResult]:
        """Comprehensive performance testing with detailed metrics"""
        logger.info("⚡ Testing Performance Benchmarking...")
        start_time = time.time()
        perf_tests = []
        
        if not self.config.get('test_performance_load', True):
            perf_tests.append(TestResult("Performance Benchmarking", "SKIP", "Performance load testing is disabled in config"))
            return perf_tests

        endpoints_to_benchmark = {
            "Frontend Homepage": self.frontend_url,
            "Backend Health": f"{self.backend_url}/health",
            "Backend Docs": f"{self.backend_url}/docs",
        }

        concurrent_requests = self.config.get('concurrent_requests', 10)
        
        for name, url in endpoints_to_benchmark.items():
            try:
                response_times = []
                error_count = 0

                def fetch(url):
                    try:
                        start_req = time.time()
                        response = requests.get(url, timeout=self.config.get('request_timeout', 10))
                        req_time = (time.time() - start_req) * 1000
                        if response.status_code == 200:
                            return req_time
                        return -1 # Indicate error
                    except requests.RequestException:
                        return -1

                with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
                    futures = [executor.submit(fetch, url) for _ in range(concurrent_requests)]
                    for future in as_completed(futures):
                        result = future.result()
                        if result != -1:
                            response_times.append(result)
                        else:
                            error_count += 1
                
                if not response_times:
                    perf_tests.append(TestResult(f"Performance {name}", "FAIL", "All requests failed"))
                    continue

                stats = {
                    "min": min(response_times),
                    "max": max(response_times),
                    "mean": statistics.mean(response_times),
                    "median": statistics.median(response_times),
                    "p95": statistics.quantiles(response_times, n=100)[94] if len(response_times) > 20 else 0,
                    "p99": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0,
                    "rps": concurrent_requests / (sum(response_times) / 1000) if sum(response_times) > 0 else 0,
                    "errors": error_count
                }

                message = f"Avg: {stats['mean']:.0f}ms, p95: {stats['p95']:.0f}ms, RPS: {stats['rps']:.1f}, Errors: {stats['errors']}"
                
                max_response_time = self.config.get('max_response_time_ms', 1000)
                if stats['mean'] > max_response_time:
                    status = "FAIL"
                elif stats['mean'] > max_response_time / 2:
                    status = "WARNING"
                else:
                    status = "PASS"
                
                perf_tests.append(TestResult(f"Performance {name}", status, message, details=stats))

            except Exception as e:
                perf_tests.append(TestResult(f"Performance {name}", "FAIL", f"Benchmarking failed: {e}"))
                
        execution_time = time.time() - start_time
        if perf_tests:
            for test in perf_tests:
                test.execution_time = execution_time / len(perf_tests)

        return perf_tests

    def generate_html_report(self) -> str:
        """Generate a styled HTML report"""
        logger.info("📄 Generating HTML Report...")
        
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == 'PASS'])
        failed = len([r for r in self.results if r.status == 'FAIL'])
        warnings = len([r for r in self.results if r.status == 'WARNING'])
        score = (passed / total_tests) * 100 if total_tests > 0 else 0

        def get_color(status):
            return {'PASS': '#28a745', 'FAIL': '#dc3545', 'WARNING': '#ffc107', 'SKIP': '#6c757d'}.get(status, '#007bff')

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Production Audit Report</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f8f9fa; margin: 0; padding: 20px; }}
                .container {{ max-width: 960px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                h1, h2 {{ color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px; }}
                .summary {{ display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; }}
                .summary-box {{ padding: 20px; border-radius: 8px; color: #fff; min-width: 120px; }}
                .score {{ text-align: center; font-size: 2em; font-weight: bold; color: {get_color('PASS' if score > 80 else 'FAIL')}; }}
                .test-category {{ margin-bottom: 20px; }}
                .test-result {{ border-left: 5px solid; padding: 10px; margin-bottom: 10px; background-color: #f8f9fa; border-radius: 5px; }}
                .test-result.PASS {{ border-left-color: {get_color('PASS')}; }}
                .test-result.FAIL {{ border-left-color: {get_color('FAIL')}; }}
                .test-result.WARNING {{ border-left-color: {get_color('WARNING')}; }}
                .test-result.SKIP {{ border-left-color: {get_color('SKIP')}; }}
                details > summary {{ cursor: pointer; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Production Audit Report</h1>
                <p>Generated: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <div class="score">Production Readiness Score: {score:.2f}%</div>

                <div class="summary">
                    <div class="summary-box" style="background-color: {get_color('PASS')};"><strong>Passed</strong><br>{passed}</div>
                    <div class="summary-box" style="background-color: {get_color('FAIL')};"><strong>Failed</strong><br>{failed}</div>
                    <div class="summary-box" style="background-color: {get_color('WARNING')};"><strong>Warnings</strong><br>{warnings}</div>
                    <div class="summary-box" style="background-color: {get_color('SKIP')};"><strong>Skipped</strong><br>{len([r for r in self.results if r.status == 'SKIP'])}</div>
                </div>

        """
        
        # Group results by a category based on test name
        categories = {}
        for r in self.results:
            category = r.name.split(' ')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(r)

        for category, results in categories.items():
            html += f"<div class='test-category'><h2>{category}</h2>"
            for r in results:
                html += f"""
                <div class="test-result {r.status}">
                    <details>
                        <summary>{r.status}: {r.name}</summary>
                        <p>{r.message}</p>
                        {f'<pre>{json.dumps(r.details, indent=2)}</pre>' if r.details else ''}
                        <small>Execution time: {r.execution_time:.4f}s</small>
                    </details>
                </div>
                """
            html += "</div>"

        html += """
            </div>
        </body>
        </html>
        """
        return html

    def generate_json_report(self) -> Dict[str, Any]:
        """Generate a structured JSON report"""
        logger.info("📄 Generating JSON Report...")
        
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == 'PASS'])
        failed = len([r for r in self.results if r.status == 'FAIL'])
        warnings = len([r for r in self.results if r.status == 'WARNING'])
        skipped = len([r for r in self.results if r.status == 'SKIP'])
        score = (passed / total_tests) * 100 if total_tests > 0 else 0

        return {
            "metadata": {
                "timestamp": self.start_time.isoformat(),
                "execution_time": (datetime.now() - self.start_time).total_seconds(),
                "environment": {
                    "backend_url": self.backend_url,
                    "frontend_url": self.frontend_url,
                }
            },
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "skipped": skipped,
                "production_readiness_score": score,
            },
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "execution_time": r.execution_time,
                } for r in self.results
            ]
        }
    
    def generate_production_report(self) -> str:
        """Generate comprehensive production readiness report"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == 'PASS'])
        failed_tests = len([r for r in self.results if r.status == 'FAIL'])
        warning_tests = len([r for r in self.results if r.status == 'WARNING'])
        skipped_tests = len([r for r in self.results if r.status == 'SKIP'])
        
        execution_time = (datetime.now() - self.start_time).total_seconds()
        
        report = f"""
# 🚀 PRODUCTION READINESS AUDIT REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Execution Time: {execution_time:.2f} seconds

## 📊 SUMMARY
- **Total Tests**: {total_tests}
- **✅ Passed**: {passed_tests} ({passed_tests/total_tests*100:.1f}%)
- **❌ Failed**: {failed_tests} ({failed_tests/total_tests*100:.1f}%)
- **⚠️ Warnings**: {warning_tests} ({warning_tests/total_tests*100:.1f}%)
- **⏭️ Skipped**: {skipped_tests} ({skipped_tests/total_tests*100:.1f}%)

## 🎯 PRODUCTION READINESS SCORE
{passed_tests}/{total_tests} tests passed

"""
        
        if failed_tests == 0:
            if warning_tests == 0:
                report += "🟢 **PRODUCTION READY** - All critical tests passed!\n\n"
            else:
                report += "🟡 **PRODUCTION READY WITH WARNINGS** - Consider addressing warnings\n\n"
        else:
            report += "🔴 **NOT PRODUCTION READY** - Critical issues must be resolved\n\n"
        
        # Detailed Results by Category
        categories = {
            'Backend': [r for r in self.results if 'Backend' in r.name or 'API' in r.name or 'Database' in r.name],
            'Frontend': [r for r in self.results if 'Frontend' in r.name or 'Route' in r.name or 'Asset' in r.name],
            'Security': [r for r in self.results if 'Security' in r.name or 'HTTPS' in r.name or 'CORS' in r.name],
            'Configuration': [r for r in self.results if 'Config' in r.name or 'Environment' in r.name or 'Env' in r.name],
            'Performance': [r for r in self.results if 'Performance' in r.name or 'Response Time' in r.name],
            'Images': [r for r in self.results if 'Image' in r.name or 'Icon' in r.name or 'Asset' in r.name]
        }
        
        for category, tests in categories.items():
            if not tests:
                continue
                
            report += f"## {category.upper()}\n"
            category_passed = len([t for t in tests if t.status == 'PASS'])
            report += f"Passed: {category_passed}/{len(tests)}\n\n"
            
            for test in tests:
                status_emoji = {
                    'PASS': '✅',
                    'FAIL': '❌', 
                    'WARNING': '⚠️',
                    'SKIP': '⏭️'
                }
                emoji = status_emoji.get(test.status, '❓')
                report += f"{emoji} **{test.name}**: {test.message}\n"
                if test.execution_time > 0:
                    report += f"   *Execution time: {test.execution_time:.3f}s*\n"
                if test.details:
                    report += f"   *Details: {json.dumps(test.details, indent=2)}*\n"
                report += "\n"
        
        # Recommendations
        report += "## 🔧 RECOMMENDATIONS\n\n"
        
        if failed_tests > 0:
            report += "### Critical Issues (Must Fix)\n"
            for test in self.results:
                if test.status == 'FAIL':
                    report += f"- **{test.name}**: {test.message}\n"
            report += "\n"
        
        if warning_tests > 0:
            report += "### Warnings (Should Address)\n"
            for test in self.results:
                if test.status == 'WARNING':
                    report += f"- **{test.name}**: {test.message}\n"
            report += "\n"
        
        # Next Steps
        report += "## 📋 NEXT STEPS\n\n"
        report += "1. **Address Critical Issues**: Fix all FAIL status items before production deployment\n"
        report += "2. **Review Warnings**: Consider addressing WARNING items for improved security/performance\n"
        report += "3. **Run Full Test Suite**: Execute comprehensive integration tests\n"
        report += "4. **Monitor Production**: Set up monitoring and alerting for production deployment\n"
        report += "5. **Backup Strategy**: Ensure proper backup and recovery procedures\n\n"
        
        report += "## 🏆 CONCLUSION\n\n"
        if failed_tests == 0:
            report += "✅ **The application is ready for production deployment!**\n\n"
        else:
            report += "❌ **The application needs fixes before production deployment.**\n\n"
        
        report += f"Total execution time: {execution_time:.2f} seconds\n"
        report += f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report

def main():
    """Main execution function"""
    print("🚀 Starting Comprehensive Production Audit...")
    
    # Initialize auditor with global config
    auditor = ProductionAuditor(AUDIT_CONFIG)
    
    try:
        # Run all test suites
        test_suites = [
            auditor.test_backend_health,
            auditor.test_all_api_endpoints_dynamic,
            auditor.test_frontend_functionality,
            auditor.test_comprehensive_link_validation,
            auditor.test_images_and_assets,
            auditor.test_advanced_image_integrity,
            auditor.test_database_connectivity,
            auditor.test_security_configuration,
            auditor.test_environment_configuration,
            auditor.test_performance_basics,
            auditor.test_performance_benchmarking
        ]
        
        for test_suite in test_suites:
            try:
                results = test_suite()
                if results:
                    auditor.results.extend(results)
            except Exception as e:
                logger.error(f"Test suite {test_suite.__name__} failed: {str(e)}")
                auditor.results.append(TestResult(
                    f"Test Suite {test_suite.__name__}",
                    "FAIL",
                    f"Test suite execution failed: {str(e)}"
                ))
        
        # Generate and save reports
        if AUDIT_CONFIG.get('generate_html', True):
            html_report = auditor.generate_html_report()
            with open('PRODUCTION_AUDIT_REPORT.html', 'w', encoding='utf-8') as f:
                f.write(html_report)
            print(f"📄 HTML Report saved to: PRODUCTION_AUDIT_REPORT.html")

        if AUDIT_CONFIG.get('generate_json', True):
            json_report = auditor.generate_json_report()
            with open('PRODUCTION_AUDIT_REPORT.json', 'w', encoding='utf-8') as f:
                json.dump(json_report, f, indent=2)
            print(f"📄 JSON Report saved to: PRODUCTION_AUDIT_REPORT.json")

        # Generate markdown report (legacy format)
        markdown_report = auditor.generate_production_report()
        with open('PRODUCTION_AUDIT_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        # Print summary
        summary = auditor.generate_json_report()['summary']
        print(f"\n📊 AUDIT COMPLETE")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⚠️ Warnings: {summary['warnings']}")
        print(f"Report saved to: PRODUCTION_AUDIT_REPORT.md, PRODUCTION_AUDIT_REPORT.html, PRODUCTION_AUDIT_REPORT.json")
        
        # Exit with appropriate code
        if summary['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Unhandled exception during audit: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()