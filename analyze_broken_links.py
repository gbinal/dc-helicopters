#!/usr/bin/env python3
"""
Generate a focused broken links summary for the repository.
"""

import json
from pathlib import Path

def analyze_broken_links():
    """Analyze the link check results and categorize issues."""
    
    results_file = Path('enhanced_link_check_results.json')
    if not results_file.exists():
        print("❌ Results file not found. Run enhanced_link_checker.py first.")
        return
    
    with open(results_file) as f:
        data = json.load(f)
    
    print("🔍 ACTIONABLE BROKEN LINKS ANALYSIS")
    print("=" * 50)
    
    # Categorize broken links by type of issue
    http_errors = []
    malformed_urls = []
    dns_issues = []
    
    for link in data['broken_links']:
        url = link['url']
        error = link.get('error', '')
        status_code = link.get('status_code')
        
        if status_code in [403, 404, 500, 502, 503]:
            http_errors.append(link)
        elif '//20295326276' in url:  # Double slash issue in Flickr URL
            malformed_urls.append(link)
        elif 'Failed to resolve' in error:
            dns_issues.append(link)
        else:
            # Other network issues
            dns_issues.append(link)
    
    print(f"\n🚨 HIGH PRIORITY - HTTP Errors ({len(http_errors)} links)")
    print("-" * 40)
    for link in http_errors[:10]:  # Show first 10
        print(f"• {link['url']} (HTTP {link['status_code']})")
        print(f"  File: {link['file']} (line {link['line']})")
        if link['text']:
            print(f"  Text: {link['text']}")
        print()
    
    print(f"🔧 MEDIUM PRIORITY - Malformed URLs ({len(malformed_urls)} links)")
    print("-" * 40)
    for link in malformed_urls:
        print(f"• {link['url']}")
        print(f"  File: {link['file']} (line {link['line']})")
        print(f"  Issue: URL formatting problem")
        print()
    
    print(f"🌐 NETWORK ISSUES - DNS/Connectivity ({len(dns_issues)} links)")
    print("-" * 40)
    print("These may work in normal environments but are blocked here:")
    
    # Group by domain for cleaner output
    domains = {}
    for link in dns_issues:
        domain = link['url'].split('/')[2] if '://' in link['url'] else 'unknown'
        if domain not in domains:
            domains[domain] = []
        domains[domain].append(link)
    
    for domain, links in list(domains.items())[:10]:  # Show first 10 domains
        print(f"• {domain} ({len(links)} links)")
    
    print(f"\n📊 SUMMARY")
    print("-" * 20)
    print(f"Total broken: {len(data['broken_links'])}")
    print(f"High priority (HTTP errors): {len(http_errors)}")
    print(f"Medium priority (malformed): {len(malformed_urls)}")
    print(f"Network issues: {len(dns_issues)}")
    
    print(f"\n✅ WORKING LINKS: {data['summary']['working']}")
    print(f"🚫 NETWORK BLOCKED: {data['summary']['network_restricted']}")
    
    return {
        'http_errors': http_errors,
        'malformed_urls': malformed_urls,
        'dns_issues': dns_issues
    }

if __name__ == "__main__":
    analyze_broken_links()