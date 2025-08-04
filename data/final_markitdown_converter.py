#!/usr/bin/env python3
"""
Professional Markitdown to Markdown Converter

This script converts markitdown's formatted output into clean, professional markdown.
Specifically handles financial documents with complex table structures.

Usage:
    python professional_markitdown_converter.py input.md [output.md]
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


class ProfessionalMarkitdownConverter:
    def __init__(self):
        self.lines = []
        self.output_lines = []
        
    def load_file(self, file_path: str) -> None:
        """Load the markitdown file with proper encoding detection."""
        try:
            encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    self.lines = content.split('\n')
                    print(f"✅ Successfully loaded file with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"Could not decode file {file_path}")
                
        except FileNotFoundError:
            raise FileNotFoundError(f"File {file_path} not found")
    
    def is_spaced_header(self, line: str) -> bool:
        """Detect spaced headers like 'H I G H L I G H T S'."""
        cleaned = re.sub(r'\s+', ' ', line.strip())
        if len(cleaned) < 3:
            return False
        
        words = cleaned.split(' ')
        if len(words) < 3:
            return False
        
        # Count single uppercase letters and short uppercase words
        single_letters = sum(1 for word in words if len(word) == 1 and word.isupper())
        short_uppercase = sum(1 for word in words if len(word) <= 3 and word.isupper() and word.isalpha())
        
        return single_letters >= len(words) * 0.5 or short_uppercase >= len(words) * 0.7
    
    def convert_spaced_header(self, line: str, level: int = 1) -> str:
        """Convert spaced header to proper markdown."""
        cleaned = re.sub(r'\s+', ' ', line.strip())
        words = cleaned.split(' ')
        
        result_words = []
        current_word = []
        
        for word in words:
            if len(word) == 1 and word.isalpha():
                current_word.append(word)
            else:
                if current_word:
                    result_words.append(''.join(current_word))
                    current_word = []
                if word.strip():
                    result_words.append(word)
        
        if current_word:
            result_words.append(''.join(current_word))
        
        header_text = ' '.join(result_words)
        return f"{'#' * level} {header_text}"
    
    def find_financial_table_start(self, start_idx: int) -> Tuple[List[str], List[str], int]:
        """Find and extract financial table headers and quarters."""
        i = start_idx
        financial_headers = []
        quarter_headers = []
        
        # First, collect financial metric headers
        while i < len(self.lines):
            line = self.lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Stop when we hit quarter data or numeric data
            if re.match(r'^Q\d-\d{4}|^\d{1,3}$|^[\d,.$\s%-]+$', line):
                break
            
            # Collect financial metrics
            if (line and 
                len(line) > 3 and 
                not line.startswith('#') and
                not line.startswith('(') and
                any(keyword in line.lower() for keyword in [
                    'revenue', 'income', 'margin', 'cash', 'eps', 'ebitda', 
                    'profit', 'expenses', 'expenditures', 'flow', 'assets'
                ])):
                financial_headers.append(line)
            
            i += 1
        
        # Now find quarter headers
        while i < len(self.lines):
            line = self.lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Look for quarter patterns
            quarters_in_line = re.findall(r'Q\d-\d{4}', line)
            if quarters_in_line:
                quarter_headers.extend(quarters_in_line)
                
                # Check next few lines for more quarters
                j = i + 1
                while j < len(self.lines) and j < i + 5:
                    next_line = self.lines[j].strip()
                    if not next_line:
                        j += 1
                        continue
                    more_quarters = re.findall(r'Q\d-\d{4}', next_line)
                    if more_quarters:
                        quarter_headers.extend(more_quarters)
                        i = j
                    else:
                        break
                    j += 1
                
                i += 1
                break
            i += 1
        
        return financial_headers, quarter_headers, i
    
    def extract_financial_data(self, start_idx: int, num_quarters: int, num_metrics: int) -> Tuple[List[List[str]], int]:
        """Extract financial data organized by quarters."""
        i = start_idx
        data_by_quarter = [[] for _ in range(num_quarters)]
        
        while i < len(self.lines):
            line = self.lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Stop if we hit non-numeric content
            if not re.search(r'[\d,.$%-]', line) and len(line) > 10:
                break
            
            # Process numeric data
            if re.search(r'[\d,.$%-]', line):
                # Handle single column of data (vertical layout)
                if not re.search(r'\s{2,}', line):  # No multi-column spacing
                    # Single value - add to first available quarter
                    for quarter_idx in range(num_quarters):
                        if len(data_by_quarter[quarter_idx]) < num_metrics:
                            data_by_quarter[quarter_idx].append(line)
                            break
                else:
                    # Multi-column data
                    values = re.split(r'\s{2,}', line)
                    values = [v.strip() for v in values if v.strip()]
                    
                    for idx, value in enumerate(values):
                        if idx < num_quarters:
                            data_by_quarter[idx].append(value)
            
            i += 1
        
        return data_by_quarter, i
    
    def create_financial_table(self, headers: List[str], quarters: List[str], data_by_quarter: List[List[str]]) -> List[str]:
        """Create a properly formatted markdown table."""
        if not headers or not quarters or not data_by_quarter:
            return []
        
        table_lines = []
        
        # Create table header
        table_header = ["Metric"] + quarters + ["YoY"]
        table_lines.append("| " + " | ".join(table_header) + " |")
        table_lines.append("| " + " | ".join(["-" * max(3, len(h)) for h in table_header]) + " |")
        
        # Create data rows
        max_rows = max(len(data_by_quarter[0]) if data_by_quarter else 0, len(headers))
        
        for row_idx in range(min(len(headers), max_rows)):
            row_data = [headers[row_idx]]
            
            # Add data for each quarter
            for quarter_data in data_by_quarter[:len(quarters)]:
                if row_idx < len(quarter_data):
                    row_data.append(quarter_data[row_idx])
                else:
                    row_data.append("")
            
            # Add YoY column (placeholder)
            row_data.append("")
            
            # Ensure we have the right number of columns
            while len(row_data) < len(table_header):
                row_data.append("")
            
            table_lines.append("| " + " | ".join(row_data) + " |")
        
        return table_lines
    
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract document metadata."""
        metadata = {}
        
        if 'tesla' in content.lower():
            metadata['company'] = 'Tesla'
        
        quarter_match = re.search(r'Q([1-4])', content)
        if quarter_match:
            metadata['quarter'] = f"Q{quarter_match.group(1)}"
        
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
        """Clean up formatting issues."""
        # Fix special characters
        line = line.replace('Æ', "'")
        line = line.replace('û', "—")
        line = line.replace('ü', "—")
        
        # Clean up multiple spaces
        line = re.sub(r'\s+', ' ', line)
        
        return line.strip()
    
    def format_highlight_line(self, line: str) -> str:
        """Format lines in the highlights section."""
        # Look for key financial metrics
        if '$' in line and ('B' in line or 'M' in line):
            if ' of ' in line:
                parts = line.split(' of ', 1)
                if len(parts) == 2:
                    return f"**{parts[0].strip()}:** {parts[1].strip()}"
            elif ' in ' in line:
                parts = line.split(' in ', 1)
                if len(parts) == 2 and 'Q' in parts[1]:
                    return f"**{parts[0].strip()}:** {parts[1].strip()}"
        
        # Format percentage increases
        if 'by over' in line and '%' in line:
            return f"**{line}**"
        
        return line
    
    def convert(self, input_file: str, output_file: str = None) -> None:
        """Main conversion function."""
        self.load_file(input_file)
        
        if output_file is None:
            output_file = input_file.replace('.md', '_professional.md')
        
        # Extract metadata
        content = '\n'.join(self.lines)
        metadata = self.extract_metadata(content)
        
        # Add frontmatter
        self.output_lines.extend(self.add_frontmatter(metadata))
        
        i = 0
        in_highlights = False
        
        while i < len(self.lines):
            line = self.lines[i]
            cleaned_line = self.clean_line(line)
            
            # Skip empty lines at the start
            if not cleaned_line and len(self.output_lines) <= 10:
                i += 1
                continue
            
            # Check for spaced headers
            if self.is_spaced_header(cleaned_line):
                header_level = 1
                if 'summary' in cleaned_line.lower():
                    header_level = 2
                elif 'financial' in cleaned_line.lower():
                    header_level = 2
                
                converted_header = self.convert_spaced_header(cleaned_line, header_level)
                self.output_lines.append(converted_header)
                self.output_lines.append("")
                
                # Track if we're in highlights section
                if 'highlights' in cleaned_line.lower():
                    in_highlights = True
                else:
                    in_highlights = False
                
                # Handle financial summary table
                if 'financial' in cleaned_line.lower() and 'summary' in cleaned_line.lower():
                    headers, quarters, next_i = self.find_financial_table_start(i + 1)
                    
                    if headers and quarters:
                        print(f"📊 Found {len(headers)} financial metrics and {len(quarters)} quarters")
                        
                        data_by_quarter, final_i = self.extract_financial_data(
                            next_i, len(quarters), len(headers)
                        )
                        
                        table_lines = self.create_financial_table(headers, quarters, data_by_quarter)
                        
                        if table_lines:
                            self.output_lines.extend(table_lines)
                            self.output_lines.append("")
                            print(f"✅ Created financial table with {len(table_lines)} rows")
                        
                        i = final_i
                        continue
                
                i += 1
                continue
            
            # Regular line processing
            if cleaned_line:
                if in_highlights:
                    formatted_line = self.format_highlight_line(cleaned_line)
                else:
                    formatted_line = cleaned_line
                
                self.output_lines.append(formatted_line)
            else:
                self.output_lines.append("")
            
            i += 1
        
        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.output_lines))
        
        print(f"\n🎉 Conversion completed!")
        print(f"📄 Input: {input_file}")
        print(f"📄 Output: {output_file}")
        print(f"📊 Generated {len(self.output_lines)} lines of formatted markdown")


def main():
    parser = argparse.ArgumentParser(
        description="Professional Markitdown to Markdown Converter"
    )
    parser.add_argument("input_file", help="Input markitdown file")
    parser.add_argument("output_file", nargs='?', help="Output markdown file (optional)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not Path(args.input_file).exists():
        print(f"❌ Error: Input file {args.input_file} does not exist")
        sys.exit(1)
    
    converter = ProfessionalMarkitdownConverter()
    
    try:
        converter.convert(args.input_file, args.output_file)
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
