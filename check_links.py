#!/usr/bin/env python3
"""
Link checker script for the DC Helicopters repository.
Checks all links in markdown files, HTML files, and configuration files.
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

class LinkChecker:
    def __init__(self, repository_path='.'):
        self.repo_path = Path(repository_path)
        self.broken_links = []
        self.checked_links = set()
        self.link_results = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
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
        
        # Direct URLs (http/https)
        url_pattern = r'https?://[^\s<>"\')}\]]*'
        direct_urls = re.findall(url_pattern, content)
        for url in direct_urls:
            # Avoid duplicates with markdown/html links
            if not any(link['url'] == url for link in links):
                links.append({
                    'url': url.strip(),
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
    
    def check_url(self, url):
        """Check if a URL is accessible."""
        if url in self.checked_links:
            return self.link_results[url]
        
        self.checked_links.add(url)
        
        try:
            print(f"Checking: {url}")
            response = self.session.head(url, timeout=10, allow_redirects=True)
            
            # Some servers don't support HEAD requests, try GET
            if response.status_code == 405 or response.status_code == 404:
                response = self.session.get(url, timeout=10, allow_redirects=True)
            
            is_working = response.status_code < 400
            result = {
                'working': is_working,
                'status_code': response.status_code,
                'final_url': response.url
            }
            
            self.link_results[url] = result
            time.sleep(0.5)  # Be respectful to servers
            return result
            
        except requests.exceptions.RequestException as e:
            result = {
                'working': False,
                'status_code': None,
                'error': str(e),
                'final_url': url
            }
            self.link_results[url] = result
            return result
    
    def check_yaml_links(self, file_path):
        """Check links in YAML files."""
        links = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Try to parse as YAML
            try:
                data = yaml.safe_load(content)
                if data:
                    yaml_text = yaml.dump(data)
                    links.extend(self.find_links_in_text(yaml_text, file_path))
            except yaml.YAMLError:
                pass
            
            # Also check raw content for URLs
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
        """Generate a comprehensive report of link checking results."""
        total_links = 0
        broken_count = 0
        
        print("\n" + "="*80)
        print("LINK CHECK REPORT")
        print("="*80)
        
        for file_path, links in all_links.items():
            if not links:
                continue
                
            print(f"\n📄 {file_path}")
            print("-" * len(file_path))
            
            for link in links:
                total_links += 1
                result = self.check_url(link['url'])
                
                status = "✅ WORKING" if result['working'] else "❌ BROKEN"
                print(f"  Line {link['line']:3d}: {status} - {link['url']}")
                
                if not result['working']:
                    broken_count += 1
                    self.broken_links.append({
                        'file': file_path,
                        'line': link['line'],
                        'url': link['url'],
                        'text': link['text'],
                        'type': link['type'],
                        'error': result.get('error', f"HTTP {result.get('status_code', 'Unknown')}")
                    })
                    
                    if result.get('status_code'):
                        print(f"           Status: {result['status_code']}")
                    if result.get('error'):
                        print(f"           Error: {result['error']}")
        
        print(f"\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total links checked: {total_links}")
        print(f"Working links: {total_links - broken_count}")
        print(f"Broken links: {broken_count}")
        
        if self.broken_links:
            print(f"\n❌ BROKEN LINKS DETAILS:")
            print("-" * 40)
            for i, broken in enumerate(self.broken_links, 1):
                print(f"{i}. {broken['url']}")
                print(f"   File: {broken['file']} (line {broken['line']})")
                print(f"   Error: {broken['error']}")
                if broken['text']:
                    print(f"   Link text: {broken['text']}")
                print()
        else:
            print("\n🎉 All links are working!")
        
        return {
            'total_links': total_links,
            'broken_count': broken_count,
            'broken_links': self.broken_links
        }
    
    def save_results(self, results):
        """Save results to a JSON file."""
        output_file = self.repo_path / 'link_check_results.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📝 Detailed results saved to: {output_file}")

def main():
    checker = LinkChecker()
    
    print("🔍 Starting link check for DC Helicopters repository...")
    all_links = checker.scan_files()
    
    if not any(all_links.values()):
        print("No external links found to check.")
        return
    
    results = checker.generate_report(all_links)
    checker.save_results(results)
    
    # Exit with error code if broken links found
    sys.exit(1 if results['broken_count'] > 0 else 0)

if __name__ == "__main__":
    main()