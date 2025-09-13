"""Enhanced URL filtering utilities for penetration testing focus"""

import re
from urllib.parse import urlparse
from typing import Set, Dict, List

# Comprehensive CDN and third-party service domains to ignore
IGNORED_DOMAINS = {
    # Google Services & CDN
    'google.com', 'googleapis.com', 'googletagmanager.com', 'google-analytics.com',
    'googlesyndication.com', 'googleadservices.com', 'gstatic.com', 'googleusercontent.com',
    'recaptcha.net', 'maps.googleapis.com', 'translate.googleapis.com',
    
    # Major CDNs
    'cloudflare.com', 'cdnjs.cloudflare.com', 'jsdelivr.com', 'unpkg.com',
    'bootstrapcdn.com', 'fontawesome.com', 'fonts.googleapis.com',
    'maxcdn.bootstrapcdn.com', 'stackpath.bootstrapcdn.com',
    'cdn.jsdelivr.net', 'unpkg.com', 'rawgit.com', 'gitcdn.link',
    
    # Amazon CDN & Services
    'amazonaws.com', 's3.amazonaws.com', 'cloudfront.net', 'd1.awsstatic.com',
    'ssl-images-amazon.com', 'amazon-adsystem.com',
    
    # Microsoft Services
    'microsoft.com', 'microsoftonline.com', 'live.com', 'office.com',
    'sharepoint.com', 'azure.com', 'visualstudio.com',
    
    # Social Media & Analytics
    'facebook.com', 'connect.facebook.net', 'twitter.com', 'linkedin.com',
    'doubleclick.net', 'adsystem.com', 'pinterest.com', 'instagram.com',
    'tiktok.com', 'youtube.com', 'youtube-nocookie.com', 'youtu.be', 'vimeo.com',
    'twimg.com', 'fbcdn.net', 'cdninstagram.com',
    
    # Analytics & Tracking
    'matomo.org', 'hotjar.com', 'mouseflow.com', 'crazyegg.com',
    'mixpanel.com', 'segment.com', 'amplitude.com', 'fullstory.com',
    'googletagservices.com', 'gtag.dev',
    
    # Ad Networks
    'adsense.com', 'admob.com', 'adsystem.com', 'googlesyndication.com',
    'amazon-adsystem.com', 'media.net', 'criteo.com', 'outbrain.com',
    'taboola.com', 'pubmatic.com',
    
    # Common JS Libraries & Widgets
    'jquery.com', 'code.jquery.com', 'ajax.googleapis.com',
    'use.fontawesome.com', 'fonts.gstatic.com', 'polyfill.io',
    'cdnjs.com', 'unpkg.com',
    
    # Other Third-party Services
    'gravatar.com', 'disqus.com', 'zendesk.com', 'intercom.io',
    'stripe.com', 'paypal.com', 'paypalobjects.com', 'captcha.com',
    'recaptcha.net', 'hcaptcha.com'
}

# Comprehensive file extensions to ignore (static assets)
IGNORED_EXTENSIONS = {
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp', '.bmp', '.tiff',
    
    # Scripts & Styles (should not be penetration tested)
    '.js', '.css', '.map', '.min.js', '.min.css',
    
    # Fonts
    '.woff', '.woff2', '.ttf', '.eot', '.otf',
    
    # Media
    '.mp4', '.mp3', '.wav', '.avi', '.mov', '.wmv', '.flv', '.webm',
    
    # Documents (typically not vulnerable endpoints)
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    
    # Archives
    '.zip', '.rar', '.tar', '.gz', '.7z',
    
    # Manifest & Config files
    '.manifest', '.xml', '.txt', '.json' # Note: APIs often use .json but as file extension
}

# Static content paths to ignore
IGNORED_PATHS = {
    '/static/', '/assets/', '/css/', '/js/', '/javascript/', '/styles/',
    '/images/', '/img/', '/pics/', '/photos/', '/media/',
    '/fonts/', '/webfonts/', '/includes/', '/vendor/', '/node_modules/',
    '/favicon.ico', '/robots.txt', '/sitemap.xml', '/sitemap/', '/sitemaps/',
    '/wp-content/', '/wp-includes/', '/wp-admin/css/', '/wp-admin/js/',
    '/.well-known/', '/manifest.json', '/sw.js', '/service-worker.js'
}

# Paths that are interesting for penetration testing
PRIORITY_PATHS = {
    '/api/', '/rest/', '/graphql', '/v1/', '/v2/', '/v3/',
    '/admin/', '/administrator/', '/manage/', '/management/', '/panel/',
    '/login', '/signin', '/signup', '/register', '/auth/', '/oauth/',
    '/user/', '/users/', '/account/', '/profile/', '/dashboard/',
    '/upload', '/download', '/file/', '/files/', '/documents/',
    '/search', '/query/', '/find/', '/lookup/',
    '/payment/', '/checkout/', '/order/', '/cart/',
    '/config/', '/settings/', '/preferences/',
    '/debug/', '/test/', '/dev/', '/development/'
}

def should_analyze_url(url: str, method: str = "GET") -> bool:
    """
    Enhanced URL analysis decision for penetration testing.
    Returns True if URL is relevant for security analysis.
    
    Priority Logic:
    1. Always analyze API endpoints and dynamic routes
    2. Skip CDN, static assets, and third-party services
    3. Prioritize POST/PUT/DELETE over GET requests
    4. Focus on authentication, admin, and user interaction endpoints
    """
    try:
        parsed = urlparse(url.lower())
        domain = parsed.netloc
        path = parsed.path
        query = parsed.query
        
        # Remove www. prefix for domain matching
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check if domain is in ignored list (CDN/Third-party)
        for ignored_domain in IGNORED_DOMAINS:
            if domain == ignored_domain or domain.endswith('.' + ignored_domain):
                return False
        
        # Check file extensions (static assets)
        for ext in IGNORED_EXTENSIONS:
            if path.endswith(ext):
                return False
        
        # Check ignored paths (static content)
        for ignored_path in IGNORED_PATHS:
            if ignored_path in path:
                return False
        
        # HIGH PRIORITY: Always analyze these paths regardless of method
        for priority_path in PRIORITY_PATHS:
            if priority_path in path:
                return True
        
        # HIGH PRIORITY: Non-GET methods are always interesting
        if method.upper() in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return True
        
        # MEDIUM PRIORITY: URLs with parameters (potential injection points)
        if query or '?' in url:
            return True
        
        # MEDIUM PRIORITY: Dynamic routes with IDs or parameters
        if re.search(r'/\d+/', path) or re.search(r'[?&]\w+=[^&]*', url):
            return True
        
        # LOW PRIORITY: Regular GET requests to pages (still analyze but lower priority)
        # Skip obvious static pages
        static_page_patterns = [
            r'\.html?$', r'/about/?$', r'/contact/?$', r'/privacy/?$', 
            r'/terms/?$', r'/help/?$', r'/faq/?$', r'/news/?$', r'/blog/?$'
        ]
        
        for pattern in static_page_patterns:
            if re.search(pattern, path):
                return False
        
        # Default: Analyze remaining URLs but with lower priority
        return True
        
    except Exception:
        # If URL parsing fails, err on the side of caution and analyze
        return True

def get_analysis_priority(url: str, method: str = "GET") -> int:
    """
    Return priority score for URL analysis (1-10, higher = more important).
    Used for queue prioritization.
    """
    try:
        parsed = urlparse(url.lower())
        path = parsed.path
        query = parsed.query
        priority = 5  # Default priority
        
        # HIGH PRIORITY (8-10)
        if method.upper() in ['POST', 'PUT', 'DELETE', 'PATCH']:
            priority += 3
        
        for high_priority_path in ['/api/', '/admin/', '/login', '/auth/', '/upload']:
            if high_priority_path in path:
                priority += 2
                break
        
        # MEDIUM PRIORITY (+1-2)
        if query or '?' in url:
            priority += 1
        
        if re.search(r'/\d+/', path):  # ID parameters
            priority += 1
        
        # Ensure priority stays in range
        return min(max(priority, 1), 10)
        
    except Exception:
        return 5

def get_main_domain(url: str) -> str:
    """Extract the main domain from a URL for grouping"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain
    except Exception:
        return "unknown"

def is_same_site_url(url: str, target_domain: str) -> bool:
    """Check if URL belongs to the same site being tested"""
    try:
        url_domain = get_main_domain(url)
        target_domain = target_domain.lower()
        
        # Remove www. from target domain too
        if target_domain.startswith('www.'):
            target_domain = target_domain[4:]
        
        return url_domain == target_domain
    except Exception:
        return False

def categorize_url(url: str, method: str = "GET") -> str:
    """Enhanced URL categorization for better analysis"""
    try:
        parsed = urlparse(url.lower())
        path = parsed.path
        
        # API endpoints (highest priority)
        if any(api_path in path for api_path in ['/api/', '/rest/', '/graphql', '/v1/', '/v2/', '/v3/']):
            return 'API'
        
        # Authentication related (high priority)
        if any(auth_path in path for auth_path in ['/login', '/auth', '/signin', '/signup', '/register', '/oauth']):
            return 'Authentication'
        
        # Admin panels (high priority)
        if any(admin_path in path for admin_path in ['/admin', '/administrator', '/management', '/dashboard', '/panel']):
            return 'Administrative'
        
        # File operations (medium-high priority)
        if any(file_path in path for file_path in ['/upload', '/download', '/file', '/files', '/documents']):
            return 'File Operations'
        
        # User-related endpoints
        if any(user_path in path for user_path in ['/user', '/users', '/account', '/profile']):
            return 'User Management'
        
        # Search functionality
        if any(search_path in path for search_path in ['/search', '/query', '/find', '/lookup']):
            return 'Search'
        
        # E-commerce/Payment
        if any(commerce_path in path for commerce_path in ['/payment', '/checkout', '/order', '/cart', '/shop']):
            return 'E-commerce'
        
        # Configuration/Settings
        if any(config_path in path for config_path in ['/config', '/settings', '/preferences']):
            return 'Configuration'
        
        # Development/Debug (often interesting)
        if any(dev_path in path for dev_path in ['/debug', '/test', '/dev', '/development']):
            return 'Development'
        
        # Method-based categorization
        if method.upper() in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return f'Dynamic ({method.upper()})'
        
        # Default web page
        return 'Web Page'
        
    except Exception:
        return 'Unknown'

def is_likely_api_endpoint(url: str, method: str = "GET") -> bool:
    """Determine if URL is likely an API endpoint"""
    try:
        parsed = urlparse(url.lower())
        path = parsed.path
        
        # Direct API paths
        if any(api_indicator in path for api_indicator in ['/api/', '/rest/', '/graphql']):
            return True
        
        # Version indicators
        if re.search(r'/v\d+/', path):
            return True
        
        # Non-GET methods often indicate API
        if method.upper() in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return True
        
        # JSON/XML endpoints
        if path.endswith('.json') or path.endswith('.xml'):
            return True
        
        return False
        
    except Exception:
        return False

def should_prioritize_for_ai_analysis(url: str, method: str = "GET") -> bool:
    """
    Determine if URL should get AI analysis vs simple pattern matching.
    Complex requests get AI analysis, simple static requests don't.
    """
    # Always AI analyze API endpoints
    if is_likely_api_endpoint(url, method):
        return True
    
    # AI analyze non-GET methods
    if method.upper() in ['POST', 'PUT', 'DELETE', 'PATCH']:
        return True
    
    # AI analyze authentication/admin endpoints
    parsed = urlparse(url.lower())
    sensitive_paths = ['/login', '/admin', '/auth', '/upload', '/config']
    if any(sensitive in parsed.path for sensitive in sensitive_paths):
        return True
    
    # Simple static pages don't need AI
    return False
