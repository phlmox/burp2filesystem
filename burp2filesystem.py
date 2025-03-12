import os
import base64
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import argparse
import json
import re
from typing import List, Set

class Config:
    def __init__(self):
        self.in_scope_domains: Set[str] = set()
        self.out_scope_domains: Set[str] = set()
        self.unwanted_extensions: Set[str] = set()
        self.unwanted_content_types: Set[str] = set()
        self.output_dir: str = "output"
        self.use_regex: bool = False

    def save(self, filename: str = "config.json"):
        with open(filename, 'w') as f:
            json.dump({
                'in_scope_domains': list(self.in_scope_domains),
                'out_scope_domains': list(self.out_scope_domains),
                'unwanted_extensions': list(self.unwanted_extensions),
                'unwanted_content_types': list(self.unwanted_content_types),
                'output_dir': self.output_dir,
                'use_regex': self.use_regex
            }, f, indent=4)

    def load(self, filename: str = "config.json"):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                self.in_scope_domains = set(data.get('in_scope_domains', []))
                self.out_scope_domains = set(data.get('out_scope_domains', []))
                self.unwanted_extensions = set(data.get('unwanted_extensions', []))
                self.unwanted_content_types = set(data.get('unwanted_content_types', []))
                self.output_dir = data.get('output_dir', 'output')
                self.use_regex = data.get('use_regex', False)

def create_directory_structure(base_path, url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path_parts = parsed_url.path.strip('/').split('/')
    
    current_path = os.path.join(base_path, domain)
    os.makedirs(current_path, exist_ok=True)
    
    for part in path_parts[:-1]:
        if part:
            current_path = os.path.join(current_path, part)
            os.makedirs(current_path, exist_ok=True)
    
    return current_path

def get_filename(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    if not path_parts or not path_parts[-1]:
        return 'index.txt'
    return f"{path_parts[-1]}.txt"

def is_url_in_scope(url: str, config: Config) -> bool:
    domain = urlparse(url).netloc
    
    if not config.in_scope_domains:
        if config.use_regex:
            return not any(re.search(pattern, domain) for pattern in config.out_scope_domains)
        return domain not in config.out_scope_domains
    
    if config.use_regex:
        if any(re.search(pattern, domain) for pattern in config.out_scope_domains):
            return False
        return any(re.search(pattern, domain) for pattern in config.in_scope_domains)
    else:
        if domain in config.out_scope_domains:
            return False
        for scope_domain in config.in_scope_domains:
            if domain == scope_domain or domain.endswith('.' + scope_domain):
                return True
    
    return False

def should_process_url(url: str, config: Config) -> bool:
    if not is_url_in_scope(url, config):
        return False
        
    path = urlparse(url).path.lower()
    return not any(path.endswith(ext) for ext in config.unwanted_extensions)

def extract_items(xml_file: str, config: Config):
    os.makedirs(config.output_dir, exist_ok=True)
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    for item in root.findall('.//item'):
        url_elem = item.find('url')
        if url_elem is None:
            continue
            
        url = url_elem.text
        
        if not should_process_url(url, config):
            continue
            
        response_elem = item.find('response')
        if response_elem is None:
            continue
            
        try:
            response_data = base64.b64decode(response_elem.text)
            target_dir = create_directory_structure(config.output_dir, url)
            filename = get_filename(url)
            file_path = os.path.join(target_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(response_data)
                
            print(f"Saved response to: {file_path}")
            
        except Exception as e:
            print(f"Error processing item with URL {url}: {str(e)}")

def parse_list_arg(arg_value: str) -> Set[str]:
    if not arg_value:
        return set()
    return set(item.strip() for item in arg_value.split(',') if item.strip())

def main():
    parser = argparse.ArgumentParser(description='Extract base64 encoded XML items into filesystem')
    parser.add_argument('--items', '-i', required=True, help='Items file; Path to the XML file containing base64 encoded items')
    parser.add_argument('--config', '-c', default='config.json', help='Config file; Path to config file (default: config.json)')
    parser.add_argument('--output-dir', '-o', help='Output directory for extracted files')
    parser.add_argument('--in-scope', '-is', help='Comma-separated list of in-scope domains or regex patterns')
    parser.add_argument('--out-scope', '-os', help='Comma-separated list of out-of-scope domains or regex patterns')
    parser.add_argument('--unwanted-ext', '-ue', help='Comma-separated list of unwanted file extensions')
    parser.add_argument('--unwanted-types', '-ut', help='Comma-separated list of unwanted content types')
    parser.add_argument('--save-config', '-s', action='store_true', help='Save the current configuration to config file')
    parser.add_argument('--regex', '-r', action='store_true', help='Use regex patterns for in-scope and out-scope domains')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.items):
        print(f"Error: File {args.items} does not exist")
        return

    config = Config()
    
    if os.path.exists(args.config):
        config.load(args.config)
    
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.in_scope:
        config.in_scope_domains = parse_list_arg(args.in_scope)
    if args.out_scope:
        config.out_scope_domains = parse_list_arg(args.out_scope)
    if args.unwanted_ext:
        config.unwanted_extensions = parse_list_arg(args.unwanted_ext)
    if args.unwanted_types:
        config.unwanted_content_types = parse_list_arg(args.unwanted_types)
    if args.regex:
        config.use_regex = True
    
    if args.save_config:
        config.save(args.config)
        print(f"Configuration saved to {args.config}")
    
    extract_items(args.items, config)

if __name__ == "__main__":
    main()