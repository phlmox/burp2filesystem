# Burp2Filesystem

A Python tool to extract Burp Suite's XML export into a filesystem structure. Developed with Cursor & Claude.

## Features

- Extract base64 encoded responses from Burp Suite XML export
- Organize responses into directory structure based on URL paths
- Filter URLs based on domain scope (include/exclude)
- Support for regex patterns in domain filtering
- Configurable file extension filtering
- Save and load configurations
- Command-line interface with short and long argument options

## Installation

1. Clone the repository:
```bash
git clone https://github.com/phlmox/burp2filesystem.git
cd burp2filesystem
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python extract_burp.py -i burp_export.xml
```

### Command Line Arguments

| Short | Long | Description |
|-------|------|-------------|
| `-i` | `--items` | Path to Burp Suite XML export file (required) |
| `-c` | `--config` | Path to config file (default: config.json) |
| `-o` | `--output-dir` | Output directory for extracted files |
| `-is` | `--in-scope` | Comma-separated list of in-scope domains |
| `-os` | `--out-scope` | Comma-separated list of out-of-scope domains |
| `-ue` | `--unwanted-ext` | Comma-separated list of unwanted file extensions |
| `-ut` | `--unwanted-types` | Comma-separated list of unwanted content types |
| `-s` | `--save-config` | Save the current configuration to config file |
| `-r` | `--regex` | Enable regex pattern matching for domains |

### Examples

1. Basic extraction with output directory:
```bash
python extract_burp.py -i export.xml -o extracted_files
```

2. Filter by domains:
```bash
python extract_burp.py -i export.xml -is example.com,test.com -os dev.example.com
```

3. Using regex patterns:
```bash
python extract_burp.py -i export.xml -is ".*\.example\.com" -os "dev\." -r
```

4. Exclude file extensions:
```bash
python extract_burp.py -i export.xml -ue .jpg,.png,.gif,.css,.js
```

5. Save configuration for reuse:
```bash
python extract_burp.py -i export.xml -is example.com -ue .jpg,.png -s
```

### Configuration File

The tool can save and load configurations from a JSON file. Example config.json:
```json
{
    "in_scope_domains": ["example.com", "test.com"],
    "out_scope_domains": ["dev.example.com"],
    "unwanted_extensions": [".jpg", ".png", ".gif"],
    "unwanted_content_types": [],
    "output_dir": "output",
    "use_regex": false
}
```

## Output Structure

The tool creates a directory structure based on the URL paths:
```
output/
├── example.com/
│   ├── path1/
│   │   └── page.txt
│   └── path2/
│       └── index.txt
└── test.com/
    └── index.txt
```
