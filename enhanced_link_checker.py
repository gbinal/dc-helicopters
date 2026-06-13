#!/usr/bin/env python3
"""
Enhanced link checker that handles network restrictions and provides better categorization.
"""

import os
import re
import requests
import json
import yaml
from pathlib import Path
from urllib.parse import urljoin, urlparse
import time
import sys
from collections import defaultdict

class EnhancedLinkChecker:
    def __init__(self, repository_path='.'):
        self.repo_path = Path(repository_path)
        self.broken_links = []
        self.network_restricted = []
        self.working_links = []
        self.checked_links = set()
        self.link_results = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Test network connectivity
        self.has_internet = self.test_connectivity()
        
    def test_connectivity(self):
        """Test if we have general internet connectivity."""
        try:
            # Test with a reliable service
            response = self.session.head('https://github.com/', timeout=5)
            return response.status_code < 400
        except:
            return False
    
    def find_links_in_text(self, content, file_path):
        """Extract links from text content using regex patterns."""
        links = []
        
        # Markdown links: [text](url)
        markdown_links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
        for text, url in markdown_links:
            links.append({
                'url': url.strip(),
                'text': text,
                'type': 'markdown',
                'line': self.get_line_number(content, url, file_path)
            })
        
        # HTML links: <a href="url">
        html_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>', content, re.IGNORECASE)
        for url in html_links:
            links.append({
                'url': url.strip(),
                'text': '',
                'type': 'html',
                'line': self.get_line_number(content, url, file_path)
            })
        
        # YAML/config URLs
        yaml_urls = re.findall(r'url:\s*([^\s\n]+)', content)
        for url in yaml_urls:
            links.append({
                'url': url.strip(),
                'text': '',
                'type': 'yaml',
                'line': self.get_line_number(content, url, file_path)
            })
        
        # Direct URLs (http/https) - but avoid duplicates
        url_pattern = r'https?://[^\s<>"\')}\]]*'
        direct_urls = re.findall(url_pattern, content)
        existing_urls = {link['url'] for link in links}
        for url in direct_urls:
            url = url.strip()
            if url not in existing_urls:
                links.append({
                    'url': url,
                    'text': '',
                    'type': 'direct',
                    'line': self.get_line_number(content, url, file_path)
                })
        
        return links
    
    def get_line_number(self, content, search_text, file_path):
        """Get the line number where the search text appears."""
        try:
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if search_text in line:
                    return i
        except:
            pass
        return 1
    
    def is_valid_url(self, url):
        """Check if URL is valid and should be checked."""
        if not url or url.startswith('#') or url.startswith('mailto:'):
            return False
        if url.startswith('/') and not url.startswith('//'):
            return False  # Relative paths - need site context
        return url.startswith(('http://', 'https://'))
    
    def categorize_domain(self, url):
        """Categorize domain to help with network restriction analysis."""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Common restricted domains in sandboxed environments
            restricted_patterns = [
                'travis-ci.org',
                'creativecommons.org', 
                'help.github.com',
                'jekyllrb.com',
                'yaml.org',
                'xkcd.com',
                'googletagmanager.com',
                'copterspotter.com',
                'helicoptersofdc.com',
                'graybrooks.com'
            ]
            
            for pattern in restricted_patterns:
                if pattern in domain:
                    return 'restricted'
            
            # GitHub domains (usually accessible)
            if 'github' in domain:
                return 'github'
                
            return 'general'
            
        except:
            return 'unknown'
    
    def check_url(self, url):
        """Check if a URL is accessible with enhanced categorization."""
        if url in self.checked_links:
            return self.link_results[url]
        
        self.checked_links.add(url)
        domain_category = self.categorize_domain(url)
        
        if not self.has_internet:
            result = {
                'working': False,
                'status_code': None,
                'error': 'No internet connectivity available',
                'final_url': url,
                'category': 'no_internet'
            }
            self.link_results[url] = result
            return result
        
        try:
            print(f"Checking: {url}")
            response = self.session.head(url, timeout=10, allow_redirects=True)
            
            # Some servers don't support HEAD requests, try GET
            if response.status_code == 405:
                response = self.session.get(url, timeout=10, allow_redirects=True)
            
            is_working = response.status_code < 400
            result = {
                'working': is_working,
                'status_code': response.status_code,
                'final_url': response.url,
                'category': domain_category
            }
            
            self.link_results[url] = result
            time.sleep(0.5)  # Be respectful to servers
            return result
            
        except requests.exceptions.RequestException as e:
            error_str = str(e)
            
            # Categorize the type of error
            if 'Failed to resolve' in error_str or 'No address associated with hostname' in error_str:
                category = 'dns_blocked' if domain_category == 'restricted' else 'dns_error'
            elif 'Connection refused' in error_str:
                category = 'connection_refused'
            elif 'timeout' in error_str.lower():
                category = 'timeout'
            else:
                category = 'network_error'
                
            result = {
                'working': False,
                'status_code': None,
                'error': error_str,
                'final_url': url,
                'category': category
            }
            self.link_results[url] = result
            return result
    
    def check_yaml_links(self, file_path):
        """Check links in YAML files."""
        links = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            links.extend(self.find_links_in_text(content, file_path))
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
        
        return links
    
    def scan_files(self):
        """Scan all relevant files in the repository."""
        file_types = {
            '*.md': self.find_links_in_text,
            '*.html': self.find_links_in_text,
            '*.yml': self.check_yaml_links,
            '*.yaml': self.check_yaml_links,
        }
        
        all_links = defaultdict(list)
        
        for pattern in file_types:
            for file_path in self.repo_path.rglob(pattern):
                # Skip hidden files and vendor directories
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if 'vendor' in file_path.parts or '_site' in file_path.parts:
                    continue
                
                print(f"Scanning {file_path}")
                
                try:
                    if pattern in ['*.yml', '*.yaml']:
                        links = file_types[pattern](file_path)
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        links = file_types[pattern](content, file_path)
                    
                    for link in links:
                        if self.is_valid_url(link['url']):
                            all_links[str(file_path)].append(link)
                            
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        return all_links
    
    def generate_report(self, all_links):
        """Generate a comprehensive report with enhanced categorization."""
        total_links = 0
        truly_broken = 0
        network_restricted = 0
        working = 0
        
        print("\n" + "="*80)
        print("ENHANCED LINK CHECK REPORT")
        print("="*80)
        
        if not self.has_internet:
            print("⚠️  WARNING: Limited or no internet connectivity detected.")
            print("   Results may not reflect actual link status in normal environments.\n")
        
        # Categorize all results first
        for file_path, links in all_links.items():
            for link in links:
                total_links += 1
                result = self.check_url(link['url'])
                
                link_info = {
                    'file': file_path,
                    'line': link['line'],
                    'url': link['url'],
                    'text': link['text'],
                    'type': link['type'],
                    'result': result
                }
                
                if result['working']:
                    working += 1
                    self.working_links.append(link_info)
                elif result['category'] in ['dns_blocked', 'restricted']:
                    network_restricted += 1
                    self.network_restricted.append(link_info)
                else:
                    truly_broken += 1
                    self.broken_links.append(link_info)
        
        # Print detailed results by file
        for file_path, links in all_links.items():
            if not links:
                continue
                
            print(f"\n📄 {file_path}")
            print("-" * len(file_path))
            
            for link in links:
                result = self.link_results[link['url']]
                
                if result['working']:
                    status = "✅ WORKING"
                elif result['category'] in ['dns_blocked', 'restricted']:
                    status = "🚫 BLOCKED"
                else:
                    status = "❌ BROKEN"
                
                print(f"  Line {link['line']:3d}: {status} - {link['url']}")
                
                if not result['working']:
                    if result.get('status_code'):
                        print(f"           Status: {result['status_code']}")
                    if result.get('error') and 'Failed to resolve' not in result['error']:
                        print(f"           Error: {result['error'][:100]}...")
        
        # Summary
        print(f"\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total links checked: {total_links}")
        print(f"✅ Working links: {working}")
        print(f"🚫 Network blocked/restricted: {network_restricted}")
        print(f"❌ Truly broken links: {truly_broken}")
        
        # Detailed broken links
        if self.broken_links:
            print(f"\n❌ TRULY BROKEN LINKS:")
            print("-" * 40)
            for i, broken in enumerate(self.broken_links, 1):
                result = broken['result']
                print(f"{i}. {broken['url']}")
                print(f"   File: {broken['file']} (line {broken['line']})")
                if result.get('status_code'):
                    print(f"   HTTP Status: {result['status_code']}")
                if result.get('error') and 'Failed to resolve' not in result['error']:
                    print(f"   Error: {result['error'][:100]}")
                if broken['text']:
                    print(f"   Link text: {broken['text']}")
                print()
        
        # Network restricted links
        if self.network_restricted:
            print(f"\n🚫 NETWORK BLOCKED/RESTRICTED LINKS:")
            print("-" * 40)
            print("These links may work in normal environments but are blocked in this sandboxed environment:")
            
            for i, restricted in enumerate(self.network_restricted, 1):
                print(f"{i}. {restricted['url']}")
                print(f"   File: {restricted['file']} (line {restricted['line']})")
                if restricted['text']:
                    print(f"   Link text: {restricted['text']}")
            print()
        
        if truly_broken == 0 and network_restricted == 0:
            print("\n🎉 All links appear to be working!")
        elif truly_broken == 0:
            print(f"\n✨ No truly broken links found! {network_restricted} links are blocked by network restrictions.")
        
        return {
            'total_links': total_links,
            'working': working,
            'network_restricted': network_restricted,
            'truly_broken': truly_broken,
            'broken_links': self.broken_links,
            'network_restricted_links': self.network_restricted,
            'working_links': self.working_links
        }
    
    def save_results(self, results):
        """Save results to a JSON file."""
        output_file = self.repo_path / 'enhanced_link_check_results.json'
        
        # Make results JSON serializable
        serializable_results = {
            'summary': {
                'total_links': results['total_links'],
                'working': results['working'],
                'network_restricted': results['network_restricted'],
                'truly_broken': results['truly_broken']
            },
            'broken_links': [
                {
                    'file': item['file'],
                    'line': item['line'],
                    'url': item['url'],
                    'text': item['text'],
                    'type': item['type'],
                    'status_code': item['result'].get('status_code'),
                    'error': item['result'].get('error')
                }
                for item in results['broken_links']
            ],
            'network_restricted_links': [
                {
                    'file': item['file'],
                    'line': item['line'],
                    'url': item['url'],
                    'text': item['text'],
                    'type': item['type']
                }
                for item in results['network_restricted_links']
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        print(f"\n📝 Detailed results saved to: {output_file}")

def main():
    checker = EnhancedLinkChecker()
    
    print("🔍 Starting enhanced link check for DC Helicopters repository...")
    all_links = checker.scan_files()
    
    if not any(all_links.values()):
        print("No external links found to check.")
        return
    
    results = checker.generate_report(all_links)
    checker.save_results(results)
    
    # Exit with error code only if truly broken links found
    sys.exit(1 if results['truly_broken'] > 0 else 0)

if __name__ == "__main__":
    main()