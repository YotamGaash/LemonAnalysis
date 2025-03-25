import os
import json
from pathlib import Path


def create_dirs_and_files(base_path, structure):
    """
    Recursively create directories and files based on structure.

    Args:
        base_path: The base path to create structure in
        structure: Dict with directory/file structure
    """
    for name, content in structure.items():
        path = os.path.join(base_path, name)

        if isinstance(content, dict):
            # This is a directory
            os.makedirs(path, exist_ok=True)
            create_dirs_and_files(path, content)
        else:
            # This is a file
            # Create parent directory if it doesn't exist
            directory = os.path.dirname(path)
            os.makedirs(directory, exist_ok=True)

            # Create file with content
            with open(path, 'w') as f:
                f.write(content)
            print(f"Created: {path}")


def main():
    # File templates
    templates = {
        "init": "# Init file for package\n",
        "base_fetcher": """from abc import ABC, abstractmethod
from playwright.sync_api import Page

class BaseFetcher(ABC):
    \"\"\"Base class for all fetchers.\"\"\"

    def __init__(self, config=None):
        self.config = config or {}
        self.page = None

    @abstractmethod
    def initialize(self, page: Page):
        \"\"\"Initialize the fetcher with a Playwright page.\"\"\"
        self.page = page

    @abstractmethod
    def fetch(self, query: str, **kwargs):
        \"\"\"Main method to fetch data.\"\"\"
        pass

    @abstractmethod
    def extract(self, element):
        \"\"\"Extract data from elements.\"\"\"
        pass

    def close(self):
        \"\"\"Clean up resources.\"\"\"
        if self.page:
            self.page.close()
            self.page = None
""",

        "fetcher_factory": """from typing import Dict, Type
from .base_fetcher import BaseFetcher

class FetcherFactory:
    \"\"\"Factory for creating appropriate fetchers.\"\"\"

    _fetchers: Dict[str, Type[BaseFetcher]] = {}

    @classmethod
    def register(cls, fetcher_type: str, fetcher_class: Type[BaseFetcher]):
        \"\"\"Register a fetcher class with a type identifier.\"\"\"
        cls._fetchers[fetcher_type] = fetcher_class

    @classmethod
    def create(cls, fetcher_type: str, config=None):
        \"\"\"Create a fetcher of the specified type.\"\"\"
        if fetcher_type not in cls._fetchers:
            raise ValueError(f"Unknown fetcher type: {fetcher_type}")

        return cls._fetchers[fetcher_type](config)
""",
        "exceptions": """class FetcherError(Exception):
    \"\"\"Base exception for all fetcher errors.\"\"\"
    pass

class AuthenticationError(FetcherError):
    \"\"\"Raised when authentication fails.\"\"\"
    pass

class RateLimitError(FetcherError):
    \"\"\"Raised when rate limit is exceeded.\"\"\"
    pass

class DataExtractionError(FetcherError):
    \"\"\"Raised when data cannot be extracted.\"\"\"
    pass

class DetectionAvoidanceError(FetcherError):
    \"\"\"Raised when anti-bot detection occurs.\"\"\"
    pass
""",
        "platform_fetcher": """from .base_fetcher import BaseFetcher
from playwright.sync_api import Page

class {platform}Fetcher(BaseFetcher):
    \"\"\"Fetcher for {platform} platform.\"\"\"

    def __init__(self, config=None):
        super().__init__(config)
        # Platform-specific initialization

    def initialize(self, page: Page):
        \"\"\"Initialize the fetcher with a Playwright page.\"\"\"
        super().initialize(page)
        # Platform-specific initialization

    def fetch(self, query: str, **kwargs):
        \"\"\"Main method to fetch data from {platform}.\"\"\"
        # Implementation
        pass

    def extract(self, element):
        \"\"\"Extract data from {platform} elements.\"\"\"
        # Implementation
        pass

    def login(self, credentials):
        \"\"\"Log in to {platform}.\"\"\"
        # Implementation
        pass
""",
        "strategy_base": """from abc import ABC, abstractmethod

class Base{strategy}(ABC):
    \"\"\"Base class for {strategy_desc} strategies.\"\"\"

    def __init__(self, config=None):
        self.config = config or {}

    @abstractmethod
    def apply(self, page, **kwargs):
        \"\"\"Apply the strategy to the given page.\"\"\"
        pass
""",

        "strategy_implementation": """from .base_{strategy_lower} import Base{strategy}

class {name}(Base{strategy}):
    \"\"\"{description}\"\"\"

    def __init__(self, config=None):
        super().__init__(config)

    def apply(self, page, **kwargs):
        \"\"\"Apply the {name} strategy to the page.\"\"\"
        # Implementation
        pass
""",

        "util": """# Utility functions for {util_type}

def {example_function}({params}):
    \"\"\"
{description}

Args:
{args_desc}

Returns:
{returns}
\"\"\"
    # Implementation
    pass
""",
        "mock_server": """from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return "Mock Server for Fetcher Testing"

@app.route('/facebook/login')
def facebook_login():
    return render_template('facebook_login.html')

@app.route('/facebook/feed')
def facebook_feed():
    return render_template('facebook_feed.html')

@app.route('/infinite-scroll')
def infinite_scroll():
    return render_template('infinite_scroll.html')

if __name__ == "__main__":
    app.run(debug=True)
""",
        "test": """import pytest
from {module_path} import {class_name}

def test_{test_name}_initialization():
    # Test initialization
    pass

def test_{test_name}_functionality():
    # Test main functionality
    pass
""",
        "mock_templates": """<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        /* Basic styling */
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }}
        /* Additional styling here */
    </style>
</head>
<body>
    <h1>{title}</h1>
    {content}
    <script>
        // JavaScript for interactive elements
        {script}
    </script>
</body>
</html>
"""
    }

    # Structure definition
    structure = {
        "src/fetch_data": {
            "__init__.py": templates["init"],
            "base_fetcher.py": templates["base_fetcher"],
            "fetcher_factory.py": templates["fetcher_factory"],
            "exceptions.py": templates["exceptions"],
            "facebook_fetcher.py": templates["platform_fetcher"].replace(
                "{platform}",
                "Facebook"),
            "twitter_fetcher.py": templates["platform_fetcher"].replace(
                "{platform}",
                "Twitter"),
            "instagram_fetcher.py": templates["platform_fetcher"].replace(
                "{platform}",
                "Instagram"),
            "linkedin_fetcher.py": templates["platform_fetcher"].replace(
                "{platform}",
                "LinkedIn"),

            "strategies": {
                "__init__.py": templates["init"],

                "authentication": {
                    "__init__.py": templates["init"],
                    "base_auth.py": templates["strategy_base"].replace(
                        "{strategy}",
                        "Auth").replace(
                        "{strategy_desc}", "authentication"),
                    "cookie_auth.py": templates["strategy_implementation"]
                    .replace("{strategy_lower}", "auth")
                    .replace("{strategy}", "Auth")
                    .replace("{name}", "CookieAuth")
                    .replace("{description}",
                             "Authentication strategy using cookies."),
                    "credential_auth.py": templates["strategy_implementation"]
                    .replace("{strategy_lower}", "auth")
                    .replace("{strategy}", "Auth")
                    .replace("{name}", "CredentialAuth")
                    .replace("{description}",
                             "Authentication strategy using username/password."),
                    "token_auth.py": templates["strategy_implementation"]
                    .replace("{strategy_lower}", "auth")
                    .replace("{strategy}", "Auth")
                    .replace("{name}", "TokenAuth")
                    .replace("{description}",
                             "Authentication strategy using tokens.")
                },

                "scrolling": {
                    "__init__.py": templates["init"],
                    "base_scroller.py": templates["strategy_base"].replace(
                        "{strategy}", "Scroller").replace("{strategy_desc}",
                                                          "scrolling"),
                    "infinite_scroller.py": templates[
                        "strategy_implementation"]
                    .replace("{strategy_lower}", "scroller")
                    .replace("{strategy}", "Scroller")
                    .replace("{name}", "InfiniteScroller")
                    .replace("{description}",
                             "Scrolling strategy for infinite scrolling pages."),
                    "pagination_scroller.py": templates[
                        "strategy_implementation"]
                    .replace("{strategy_lower}", "scroller")
                    .replace("{strategy}", "Scroller")
                    .replace("{name}", "PaginationScroller")
                    .replace("{description}",
                             "Scrolling strategy for paginated content."),
                    "timed_scroller.py": templates["strategy_implementation"]
                    .replace("{strategy_lower}", "scroller")
                    .replace("{strategy}", "Scroller")
                    .replace("{name}", "TimedScroller")
                    .replace("{description}",
                             "Scrolling strategy with timed intervals.")
                },

                "stealth": {
                    "__init__.py": templates["init"],
                    "base_stealth.py": templates["strategy_base"].replace(
                        "{strategy}",
                        "Stealth").replace(
                        "{strategy_desc}", "anti-detection"),
                    "fingerprint_spoofer.py": templates[
                        "strategy_implementation"]
                    .replace("{strategy_lower}", "stealth")
                    .replace("{strategy}", "Stealth")
                    .replace("{name}", "FingerprintSpoofer")
                    .replace("{description}",
                             "Strategy to modify browser fingerprints."),
                    "human_behavior.py": templates["strategy_implementation"]
                    .replace("{strategy_lower}", "stealth")
                    .replace("{strategy}", "Stealth")
                    .replace("{name}", "HumanBehavior")
                    .replace("{description}",
                             "Strategy to mimic human browsing patterns."),
                    "proxy_rotator.py": templates["strategy_implementation"]
                    .replace("{strategy_lower}", "stealth")
                    .replace("{strategy}", "Stealth")
                    .replace("{name}", "ProxyRotator")
                    .replace("{description}",
                             "Strategy to rotate proxies to avoid detection."),
                    "user_agent_rotator.py": templates[
                        "strategy_implementation"]
                    .replace("{strategy_lower}", "stealth")
                    .replace("{strategy}", "Stealth")
                    .replace("{name}", "UserAgentRotator")
                    .replace("{description}",
                             "Strategy to rotate user agents.")
                }
            },

            "utils": {
                "__init__.py": templates["init"],
                "rate_limiter.py": templates["util"]
                .replace("{util_type}", "rate limiting")
                .replace("{example_function}", "limit_requests")
                .replace("{params}", "max_requests: int, period: int")
                .replace("{description}",
                         "Limit requests to a specified number in a time period.")
                .replace("{args_desc}",
                         "        max_requests: Maximum number of requests\n        period: Time period in seconds")
                .replace("{returns}",
                         "A decorator function that limits requests"),
                "request_queue.py": templates["util"]
                .replace("{util_type}", "request queuing")
                .replace("{example_function}", "queue_request")
                .replace("{params}", "url: str, priority: int = 0")
                .replace("{description}",
                         "Queue a URL for fetching with priority.")
                .replace("{args_desc}",
                         "        url: The URL to fetch\n        priority: Priority level (higher numbers = higher priority)")
                .replace("{returns}", "Queue ID for the request"),
                "selector_helper.py": templates["util"]
                .replace("{util_type}", "CSS/XPath selection")
                .replace("{example_function}", "create_dynamic_selector")
                .replace("{params}", "base_selector: str, **kwargs")
                .replace("{description}",
                         "Create a dynamic CSS selector with replaceable parameters.")
                .replace("{args_desc}",
                         "        base_selector: Base selector with placeholders\n        **kwargs: Parameters to replace in the selector")
                .replace("{returns}", "Formatted CSS selector string")
            }
        },

        "tests/fetch_data": {
            "__init__.py": templates["init"],
            "test_base_fetcher.py": templates["test"]
            .replace("{module_path}", "src.fetch_data.base_fetcher")
            .replace("{class_name}", "BaseFetcher")
            .replace("{test_name}", "base_fetcher"),
            "test_fetcher_factory.py": templates["test"]
            .replace("{module_path}", "src.fetch_data.fetcher_factory")
            .replace("{class_name}", "FetcherFactory")
            .replace("{test_name}", "fetcher_factory"),
            "test_facebook_fetcher.py": templates["test"]
            .replace("{module_path}", "src.fetch_data.facebook_fetcher")
            .replace("{class_name}", "FacebookFetcher")
            .replace("{test_name}", "facebook_fetcher"),

            "strategies": {
                "__init__.py": templates["init"],
                "authentication": {
                    "__init__.py": templates["init"],
                    "test_auth_strategies.py": templates["test"]
                    .replace("{module_path}",
                             "src.fetch_data.strategies.authentication")
                    .replace("{class_name}", "BaseAuth")
                    .replace("{test_name}", "auth_strategies")
                },
                "scrolling": {
                    "__init__.py": templates["init"],
                    "test_scroll_strategies.py": templates["test"]
                    .replace("{module_path}",
                             "src.fetch_data.strategies.scrolling")
                    .replace("{class_name}", "BaseScroller")
                    .replace("{test_name}", "scroll_strategies")
                },
                "stealth": {
                    "__init__.py": templates["init"],
                    "test_stealth_strategies.py": templates["test"]
                    .replace("{module_path}",
                             "src.fetch_data.strategies.stealth")
                    .replace("{class_name}", "BaseStealth")
                    .replace("{test_name}", "stealth_strategies")
                }
            },

            "mocks": {
                "__init__.py": templates["init"],
                "mock_server.py": templates["mock_server"],
                "templates": {
                    "facebook_login.html": templates["mock_templates"]
                    .replace("{title}", "Facebook Login Mock")
                    .replace("{content}", """
                        <form class="login-form">
                            <div>
                                <label for="email">Email or Phone:</label>
                                <input type="text" id="email" name="email" required>
                            </div>
                            <div>
                                <label for="password">Password:</label>
                                <input type="password" id="password" name="password" required>
                            </div>
                            <button type="submit" id="login-button">Log In</button>
                        </form>
                        """)
                    .replace("{script}", """
                        document.querySelector('.login-form').addEventListener('submit', function(e) {
                            e.preventDefault();
                            const email = document.getElementById('email').value;
                            const password = document.getElementById('password').value;

                            if (email === 'test@example.com' && password === 'password123') {
                                // Successful login
                                localStorage.setItem('mockLoginSuccess', 'true');
                                window.location.href = '/facebook/feed';
                            } else {
                                // Failed login
                                alert('Invalid credentials');
                            }
                        });
                        """),
                    "facebook_feed.html": templates["mock_templates"]
                    .replace("{title}", "Facebook Feed Mock")
                    .replace("{content}", """
                        <div class="feed-container">
                            <div class="post" data-id="1">
                                <div class="post-header">User One</div>
                                <div class="post-content">This is post content 1</div>
                            </div>
                            <div class="post" data-id="2">
                                <div class="post-header">User Two</div>
                                <div class="post-content">This is post content 2</div>
                            </div>
                            <!-- Initial posts -->
                        </div>
                        <div id="feed-loader">Loading more posts...</div>
                        """)
                    .replace("{script}", """
                        // Check if logged in
                        if (!localStorage.getItem('mockLoginSuccess')) {
                            window.location.href = '/facebook/login';
                        }

                        // Infinite scroll functionality
                        let postCount = 2;

                        function loadMorePosts() {
                            const feedContainer = document.querySelector('.feed-container');

                            // Add 3 more posts
                            for (let i = 0; i < 3; i++) {
                                postCount++;
                                const post = document.createElement('div');
                                post.className = 'post';
                                post.dataset.id = postCount;
                                post.innerHTML = `
                                    <div class="post-header">User ${postCount}</div>
                                    <div class="post-content">This is post content ${postCount}</div>
                                `;
                                feedContainer.appendChild(post);
                            }
                        }

                        // Detect scroll to bottom
                        window.addEventListener('scroll', function() {
                            if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
                                loadMorePosts();
                            }
                        });
                        """),
                    "infinite_scroll.html": templates["mock_templates"]
                    .replace("{title}", "Infinite Scroll Test Page")
                    .replace("{content}", """
                        <div class="content-container">
                            <div class="content-item" data-id="1">Item 1</div>
                            <div class="content-item" data-id="2">Item 2</div>
                            <div class="content-item" data-id="3">Item 3</div>
                            <div class="content-item" data-id="4">Item 4</div>
                            <div class="content-item" data-id="5">Item 5</div>
                        </div>
                        <div id="loader" class="loader">Loading...</div>
                        """)
                    .replace("{script}", """
                        let itemCount = 5;

                        function loadMoreItems() {
                            const container = document.querySelector('.content-container');
                            const loader = document.getElementById('loader');

                            loader.style.display = 'block';

                            // Simulate network delay
                            setTimeout(() => {
                                // Add 5 more items
                                for (let i = 0; i < 5; i++) {
                                    itemCount++;
                                    const item = document.createElement('div');
                                    item.className = 'content-item';
                                    item.dataset.id = itemCount;
                                    item.textContent = `Item ${itemCount}`;
                                    container.appendChild(item);
                                }

                                loader.style.display = 'none';
                            }, 800);
                        }

                        // Set up infinite scroll
                        window.addEventListener('scroll', function() {
                            if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 200) {
                                loadMoreItems();
                            }
                        });
                        """)
                },
                "static": {
                    "css": {
                        "mock_styles.css": "/* CSS styles for mock pages */"
                    },
                    "js": {
                        "mock_scripts.js": "/* JavaScript for mock pages */"
                    }
                }
            }
        },

        "config/fetcher_config.json": json.dumps({
            "fetcher": {
                "default_platform": "facebook",
                "timeout": 60000,
                "stealth_mode": True
            },
            "authentication": {
                "method": "credential",
                "cookies_path": "data/cookies",
                "tokens_path": "data/tokens"
            },
            "platforms": {
                "facebook": {
                    "base_url": "https://www.facebook.com",
                    "login_url": "https://www.facebook.com/login",
                    "selectors": {
                        "email_field": "#email",
                        "password_field": "#pass",
                        "login_button": "[data-testid='royal_login_button']",
                        "feed_posts": "[data-pagelet='FeedUnit']"
                    }
                },
                "twitter": {
                    "base_url": "https://twitter.com",
                    "login_url": "https://twitter.com/i/flow/login",
                    "selectors": {
                        "username_field": "input[name='text']",
                        "password_field": "input[name='password']",
                        "login_button": "div[data-testid='LoginForm_Login_Button']",
                        "tweets": "article[data-testid='tweet']"
                    }
                }
            },
            "stealth": {
                "user_agent_rotation": True,
                "fingerprint_spoofing": True,
                "proxy": {
                    "enabled": False,
                    "rotation_interval": 600,
                    "proxy_list": []
                },
                "human_behavior": {
                    "enabled": True,
                    "min_delay": 500,
                    "max_delay": 3000
                }
            },
            "meta": {
                "fetcher.default_platform": {
                    "type": "str",
                    "default": "facebook",
                    "choices": ["facebook", "twitter", "instagram", "linkedin"]
                },
                "fetcher.timeout": {
                    "type": "int",
                    "default": 60000,
                    "min": 1000
                },
                "fetcher.stealth_mode": {
                    "type": "bool",
                    "default": True
                }
            }
        }, indent=2),
    }

    # Get project base path (root of the project)
    script_path = Path(__file__).resolve()
    project_path = script_path.parent

    # Create directories and files
    create_dirs_and_files(project_path, structure)

    print("\nSkeleton structure created successfully!")
    print("\nNext steps:")
    print("1. Enhance playwright_util.py to integrate with the new structure")
    print("2. Update config_util.py to load fetcher_config.json")
    print("3. Begin implementing BaseFetcher functionality")
    print("4. Set up the mock server for testing")


if __name__ == "__main__":
    main()
