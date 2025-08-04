#!/usr/bin/env python3
"""
Ultimate Markitdown to Markdown Converter

This script converts markitdown's UTF-16 formatted output into clean, professional markdown.
Designed specifically for financial documents with complex table structures like Tesla earnings reports.

Usage:
    python ultimate_markitdown_converter.py input.md [output.md]
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


class UltimateMarkitdownConverter:
    def __init__(self):
        self.lines = []
        self.output_lines = []
        
    def load_file(self, file_path: str) -> None:
        """Load file with encoding detection."""
        encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                self.lines = content.split('\n')
                print(f"✅ Loaded with {encoding} encoding ({len(self.lines)} lines)")
                return
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"Could not decode file {file_path}")
    
    def is_spaced_header(self, line: str) -> bool:
        """Detect spaced headers like 'H I G H L I G H T S'."""
        cleaned = re.sub(r'\s+', ' ', line.strip())
        if len(cleaned) < 5:
            return False
        
        words = cleaned.split(' ')
        if len(words) < 3:
            return False
        
        # Look for pattern of single letters or short uppercase words
        single_letters = sum(1 for word in words if len(word) == 1 and word.isupper())
        short_caps = sum(1 for word in words if len(word) <= 4 and word.isupper() and word.isalpha())
        
        return single_letters >= 3 or short_caps >= len(words) * 0.7
    
    def convert_spaced_header(self, line: str, level: int = 1) -> str:
        """Convert spaced header to markdown."""
        cleaned = re.sub(r'\s+', ' ', line.strip())
        words = cleaned.split(' ')
        
        result_words = []
        current_letters = []
        
        for word in words:
            if len(word) == 1 and word.isalpha():
                current_letters.append(word)
            else:
                if current_letters:
                    result_words.append(''.join(current_letters))
                    current_letters = []
                if word.strip():
                    result_words.append(word)
        
        if current_letters:
            result_words.append(''.join(current_letters))
        
        header_text = ' '.join(result_words)
        return f"{'#' * level} {header_text}"
    
    def extract_financial_summary_table(self, start_idx: int) -> Tuple[List[str], int]:
        """Extract the complete financial summary table."""
        print(f"🔍 Extracting financial table starting at line {start_idx}")
        
        i = start_idx
        financial_metrics = []
        quarters = []
        data_matrix = []
        
        # Skip unaudited note and header info
        while i < len(self.lines) and i < start_idx + 20:
            line = self.lines[i].strip()
            if line and not line.startswith('(') and len(line) > 5:
                break
            i += 1
        
        # Collect financial metric names
        print(f"📊 Collecting financial metrics from line {i}")
        while i < len(self.lines):
            line = self.lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Stop when we hit quarters or numbers
            if re.match(r'^Q\d-\d{4}|^\d+$', line):
                break
            
            # Collect metric names (lines with financial terms)
            if (len(line) > 5 and 
                not line.startswith('#') and 
                not line.startswith('(') and
                not re.match(r'^[\d,.$\s%-]+$', line)):
                financial_metrics.append(line)
                print(f"   📈 Added metric: {line}")
            
            i += 1
        
        # Find quarters
        print(f"📅 Looking for quarters from line {i}")
        while i < len(self.lines):
            line = self.lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Look for quarter patterns
            found_quarters = re.findall(r'Q\d-\d{4}', line)
            if found_quarters:
                quarters.extend(found_quarters)
                print(f"   📅 Found quarters in line {i}: {found_quarters}")
                
                # Check next few lines for more quarters
                for j in range(i + 1, min(i + 5, len(self.lines))):
                    next_line = self.lines[j].strip()
                    more_quarters = re.findall(r'Q\d-\d{4}', next_line)
                    if more_quarters:
                        quarters.extend(more_quarters)
                        print(f"   📅 Found more quarters in line {j}: {more_quarters}")
                        i = j
                
                i += 1
                break
            i += 1
        
        # Find YoY column if it exists
        yoy_found = False
        if i < len(self.lines):
            line = self.lines[i].strip()
            if 'YoY' in line or 'yoy' in line.lower():
                quarters.append('YoY')
                yoy_found = True
                print(f"   📊 Found YoY column")
                i += 1
        
        print(f"📊 Final quarters: {quarters}")
        print(f"📈 Final metrics: {len(financial_metrics)} items")
        
        # Now collect the data - it should be organized in columns
        print(f"📊 Collecting data from line {i}")
        
        # Initialize data structure
        num_quarters = len(quarters)
        data_by_quarter = [[] for _ in range(num_quarters)]
        
        # Process data lines
        data_lines_processed = 0
        while i < len(self.lines) and data_lines_processed < len(financial_metrics) * 2:
            line = self.lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Stop if we hit a new section
            if (line.startswith('#') or 
                self.is_spaced_header(line) or
                (len(line) > 50 and not re.search(r'[\d,.$%-]', line))):
                break
            
            # Process lines with numeric data
            if re.search(r'[\d,.$%-]', line):
                print(f"   📊 Processing data line {i}: {line[:50]}...")
                
                # Check if this is multi-column data (separated by 2+ spaces)
                if re.search(r'\s{2,}', line):
                    # Multi-column format
                    values = re.split(r'\s{2,}', line)
                    values = [v.strip() for v in values if v.strip()]
                    print(f"      🔢 Multi-column: {values}")
                    
                    for col_idx, value in enumerate(values):
                        if col_idx < num_quarters:
                            data_by_quarter[col_idx].append(value)
                else:
                    # Single column - add to first available quarter column
                    for col_idx in range(num_quarters):
                        if len(data_by_quarter[col_idx]) < len(financial_metrics):
                            data_by_quarter[col_idx].append(line)
                            print(f"      🔢 Single value to column {col_idx}: {line}")
                            break
                
                data_lines_processed += 1
            
            i += 1
        
        # Create the markdown table
        if financial_metrics and quarters and any(data_by_quarter):
            table_lines = []
            
            # Header row
            header_row = ["Metric"] + quarters
            table_lines.append("| " + " | ".join(header_row) + " |")
            table_lines.append("| " + " | ".join(["-" * max(3, len(h)) for h in header_row]) + " |")
            
            # Data rows
            for metric_idx, metric in enumerate(financial_metrics):
                row_data = [metric]
                
                # Add data for each quarter
                for quarter_data in data_by_quarter:
                    if metric_idx < len(quarter_data):
                        row_data.append(quarter_data[metric_idx])
                    else:
                        row_data.append("")
                
                # Ensure row has correct number of columns
                while len(row_data) < len(header_row):
                    row_data.append("")
                
                table_lines.append("| " + " | ".join(row_data) + " |")
            
            print(f"✅ Created table with {len(table_lines)} lines")
            return table_lines, i
        
        print("❌ Could not create table - insufficient data")
        return [], i
    
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract document metadata."""
        metadata = {}
        
        # Company detection
        if 'tesla' in content.lower():
            metadata['company'] = 'Tesla'
        
        # Quarter detection  
        quarter_match = re.search(r'Q([1-4])', content)
        if quarter_match:
            metadata['quarter'] = f"Q{quarter_match.group(1)}"
        
        # Year detection
        year_match = re.search(r'20\d{2}', content)
        if year_match:
            metadata['year'] = year_match.group(0)
        
        metadata['document_type'] = 'earnings_report'
        metadata['source'] = 'markitdown_converted'
        
        return metadata
    
    def add_frontmatter(self, metadata: Dict[str, Any]) -> List[str]:
        """Add YAML frontmatter."""
        lines = ["---"]
        for key, value in metadata.items():
            lines.append(f"{key}: {value}")
        lines.append("---")
        lines.append("")
        return lines
    
    def clean_line(self, line: str) -> str:
        """Clean formatting issues."""
        # Fix common character issues
        line = line.replace('Æ', "'")
        line = line.replace('û', "—")
        line = line.replace('ü', "—")
        
        # Clean multiple spaces
        line = re.sub(r'\s+', ' ', line)
        
        return line.strip()\n    \n    def format_highlights_line(self, line: str) -> str:\n        \"\"\"Format highlight section lines.\"\"\"\n        # Bold key financial metrics\n        if '$' in line and ('B' in line or 'M' in line):\n            if ' of ' in line:\n                parts = line.split(' of ', 1)\n                if len(parts) == 2:\n                    return f\"**{parts[0].strip()}:** {parts[1].strip()}\"\n            elif ' in Q' in line:\n                parts = line.split(' in Q', 1)\n                if len(parts) == 2:\n                    return f\"**{parts[0].strip()}:** in Q{parts[1].strip()}\"\n        \n        # Bold percentage increases\n        if 'by over' in line and '%' in line:\n            return f\"**{line}**\"\n        \n        return line\n    \n    def convert(self, input_file: str, output_file: str = None) -> None:\n        \"\"\"Main conversion function.\"\"\"\n        self.load_file(input_file)\n        \n        if output_file is None:\n            output_file = input_file.replace('.md', '_ultimate.md')\n        \n        # Extract metadata\n        content = '\\n'.join(self.lines)\n        metadata = self.extract_metadata(content)\n        \n        # Add frontmatter\n        self.output_lines.extend(self.add_frontmatter(metadata))\n        \n        i = 0\n        in_highlights = False\n        \n        while i < len(self.lines):\n            line = self.lines[i]\n            cleaned_line = self.clean_line(line)\n            \n            # Skip empty lines at start\n            if not cleaned_line and len(self.output_lines) <= 10:\n                i += 1\n                continue\n            \n            # Check for spaced headers\n            if self.is_spaced_header(cleaned_line):\n                header_level = 1\n                if 'summary' in cleaned_line.lower():\n                    header_level = 2\n                elif 'financial' in cleaned_line.lower():\n                    header_level = 2\n                \n                converted_header = self.convert_spaced_header(cleaned_line, header_level)\n                self.output_lines.append(converted_header)\n                self.output_lines.append(\"\")\n                \n                # Track highlights section\n                if 'highlights' in cleaned_line.lower():\n                    in_highlights = True\n                else:\n                    in_highlights = False\n                \n                # Handle financial summary with table extraction\n                if 'financial' in cleaned_line.lower() and 'summary' in cleaned_line.lower():\n                    print(f\"🔍 Processing financial summary at line {i}\")\n                    table_lines, next_i = self.extract_financial_summary_table(i + 1)\n                    \n                    if table_lines:\n                        self.output_lines.extend(table_lines)\n                        self.output_lines.append(\"\")\n                        i = next_i\n                        continue\n                \n                i += 1\n                continue\n            \n            # Regular line processing\n            if cleaned_line:\n                if in_highlights:\n                    formatted_line = self.format_highlights_line(cleaned_line)\n                else:\n                    formatted_line = cleaned_line\n                \n                self.output_lines.append(formatted_line)\n            else:\n                self.output_lines.append(\"\")\n            \n            i += 1\n        \n        # Write output\n        with open(output_file, 'w', encoding='utf-8') as f:\n            f.write('\\n'.join(self.output_lines))\n        \n        print(f\"\\n🎉 Conversion completed!\")\n        print(f\"📄 Input: {input_file}\")\n        print(f\"📄 Output: {output_file}\")\n        print(f\"📊 Generated {len(self.output_lines)} lines\")\n\n\ndef main():\n    parser = argparse.ArgumentParser(\n        description=\"Ultimate Markitdown to Markdown Converter\"\n    )\n    parser.add_argument(\"input_file\", help=\"Input markitdown file\")\n    parser.add_argument(\"output_file\", nargs='?', help=\"Output markdown file\")\n    parser.add_argument(\"--verbose\", \"-v\", action=\"store_true\", help=\"Verbose output\")\n    \n    args = parser.parse_args()\n    \n    if not Path(args.input_file).exists():\n        print(f\"❌ Error: Input file {args.input_file} does not exist\")\n        sys.exit(1)\n    \n    converter = UltimateMarkitdownConverter()\n    \n    try:\n        converter.convert(args.input_file, args.output_file)\n    except Exception as e:\n        print(f\"❌ Error: {e}\")\n        if args.verbose:\n            import traceback\n            traceback.print_exc()\n        sys.exit(1)\n\n\nif __name__ == \"__main__\":\n    main()
