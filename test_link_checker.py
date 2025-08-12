#!/usr/bin/env python3
"""
Test script for the link checker to validate it works correctly.
"""

import tempfile
import os
from pathlib import Path
from check_links import LinkChecker

def test_link_extraction():
    """Test that the link checker correctly extracts links from various formats."""
    
    # Create test content with various link formats
    test_content = """
# Test Document

Here are some test links:

1. [Markdown link](https://example.com/markdown)
2. <a href="https://example.com/html">HTML link</a>
3. Direct URL: https://example.com/direct
4. Another markdown: [GitHub](https://github.com/user/repo)
5. Email link: [Contact](mailto:test@example.com) - should be ignored
6. Anchor link: [Top](#top) - should be ignored
7. Relative link: [Page](/relative/page) - should be ignored

Some more links:
- https://test.example.com/path?param=value
- [Bad example](http://broken.nonexistent.domain)
"""
    
    checker = LinkChecker('.')
    links = checker.find_links_in_text(test_content, "test.md")
    
    # Filter to only external links
    external_links = [link for link in links if checker.is_valid_url(link['url'])]
    
    expected_urls = [
        'https://example.com/markdown',
        'https://example.com/html', 
        'https://example.com/direct',
        'https://github.com/user/repo',
        'https://test.example.com/path?param=value',
        'http://broken.nonexistent.domain'
    ]
    
    found_urls = [link['url'] for link in external_links]
    
    print("🧪 Testing link extraction...")
    print(f"Expected URLs: {len(expected_urls)}")
    print(f"Found URLs: {len(found_urls)}")
    
    for expected in expected_urls:
        if expected in found_urls:
            print(f"✅ Found: {expected}")
        else:
            print(f"❌ Missing: {expected}")
    
    for found in found_urls:
        if found not in expected_urls:
            print(f"⚠️  Unexpected: {found}")
    
    return len(expected_urls) == len(found_urls) and all(url in found_urls for url in expected_urls)

def test_accessible_links():
    """Test checking links that should be accessible."""
    
    checker = LinkChecker('.')
    
    # Test a link we know should work
    result = checker.check_url('https://github.com/')
    print(f"\n🧪 Testing accessible link...")
    print(f"GitHub.com result: {result}")
    
    return result['working']

def test_broken_links():
    """Test checking links that should be broken."""
    
    checker = LinkChecker('.')
    
    # Test a link that should definitely not work
    result = checker.check_url('https://this-domain-definitely-does-not-exist-12345.com/')
    print(f"\n🧪 Testing broken link...")
    print(f"Nonexistent domain result: {result}")
    
    return not result['working']

def main():
    """Run all tests."""
    
    print("🚀 Running Link Checker Tests")
    print("=" * 50)
    
    tests = [
        ("Link Extraction", test_link_extraction),
        ("Accessible Links", test_accessible_links), 
        ("Broken Links", test_broken_links)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)