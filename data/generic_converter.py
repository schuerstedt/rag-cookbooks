#!/usr/bin/env python3
"""
Generic Markitdown to Markdown Converter

This script converts markitdown output to clean markdown format.
Works with any markitdown-generated file and handles:
- Spaced headers (H I G H L I G H T S -> # HIGHLIGHTS)
- Financial tables with quarter-based data
- UTF-16 encoding issues
- Character formatting cleanup

Usage:
    python generic_markitdown_converter.py input.md [output.md]
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any


def clean_text(text: str) -> str:
    """Clean common formatting issues."""
    # Fix UTF-16 character issues
    text = text.replace('Æ', "'")
    text = text.replace('û', "—")
    text = text.replace('ü', "—")
    
    # Clean multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def is_spaced_header(line: str) -> bool:
    """Check if line is a spaced header like 'H I G H L I G H T S'."""
    cleaned = re.sub(r'\s+', ' ', line.strip())
    if len(cleaned) < 5:
        return False
    
    words = cleaned.split(' ')
    if len(words) < 3:
        return False
    
    # Count single letters and short uppercase words
    single_letters = sum(1 for word in words if len(word) == 1 and word.isupper())
    short_caps = sum(1 for word in words if len(word) <= 4 and word.isupper() and word.isalpha())
    
    return single_letters >= 3 or short_caps >= len(words) * 0.7


def convert_spaced_header(line: str, level: int = 1) -> str:
    """Convert spaced header to markdown format."""
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


def extract_metadata(content: str) -> Dict[str, Any]:
    """Extract document metadata."""
    metadata = {}
    
    # Detect company
    if 'tesla' in content.lower():
        metadata['company'] = 'Tesla'
    elif 'apple' in content.lower():
        metadata['company'] = 'Apple'
    elif 'microsoft' in content.lower():
        metadata['company'] = 'Microsoft'
    
    # Detect quarter
    quarter_match = re.search(r'Q([1-4])', content)
    if quarter_match:
        metadata['quarter'] = f"Q{quarter_match.group(1)}"
    
    # Detect year
    year_match = re.search(r'20\d{2}', content)
    if year_match:
        metadata['year'] = year_match.group(0)
    
    metadata['document_type'] = 'financial_report'
    metadata['source'] = 'markitdown_converted'
    
    return metadata


def create_frontmatter(metadata: Dict[str, Any]) -> List[str]:
    """Create YAML frontmatter."""
    lines = ["---"]
    for key, value in metadata.items():
        lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")
    return lines


def format_financial_metrics(line: str) -> str:
    """Format financial metric lines."""
    # Bold financial metrics with dollar amounts
    if '$' in line and ('B' in line or 'M' in line):
        if ' of ' in line:
            parts = line.split(' of ', 1)
            if len(parts) == 2:
                return f"**{parts[0].strip()}:** {parts[1].strip()}"
        elif ' in Q' in line:
            parts = line.split(' in Q', 1)
            if len(parts) == 2:
                return f"**{parts[0].strip()}:** in Q{parts[1].strip()}"
    
    # Bold percentage changes
    if 'by over' in line and '%' in line:
        return f"**{line}**"
    
    return line


def extract_simple_table(lines: List[str], start_idx: int) -> tuple[List[str], int]:
    """Extract a simple table from financial data."""
    table_lines = []
    i = start_idx
    headers = []
    data_rows = []
    
    # Look for financial metric headers
    while i < len(lines) and i < start_idx + 30:
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # Stop at quarters or numbers
        if re.match(r'^Q\d-\d{4}|^[\d,.$\s%-]+$', line):
            break
        
        # Collect headers (financial terms)
        if (len(line) > 5 and 
            not line.startswith('(') and
            any(term in line.lower() for term in ['revenue', 'income', 'margin', 'cash', 'eps', 'flow'])):
            headers.append(line)
        
        i += 1
    
    # Look for quarters
    quarters = []
    while i < len(lines) and i < start_idx + 50:
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        found_quarters = re.findall(r'Q\d-\d{4}', line)
        if found_quarters:
            quarters.extend(found_quarters)
            i += 1
            break
        i += 1
    
    # Collect data
    data_collected = []
    while i < len(lines) and len(data_collected) < len(headers) * len(quarters):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # Stop at new sections
        if line.startswith('#') or is_spaced_header(line):
            break
        
        # Collect numeric data
        if re.search(r'[\d,.$%-]', line):
            # Split multi-column data
            if re.search(r'\s{2,}', line):
                values = re.split(r'\s{2,}', line)
                data_collected.extend([v.strip() for v in values if v.strip()])
            else:
                data_collected.append(line)
        
        i += 1
    
    # Create table if we have enough data
    if headers and quarters and data_collected:
        table_lines.append("")
        table_lines.append("## Financial Summary Table")
        table_lines.append("")
        
        # Create header
        header_row = ["Metric"] + quarters
        table_lines.append("| " + " | ".join(header_row) + " |")
        table_lines.append("| " + " | ".join(["-" * max(3, len(h)) for h in header_row]) + " |")
        
        # Create data rows
        data_idx = 0
        for header in headers:
            row_data = [header]
            for _ in quarters:
                if data_idx < len(data_collected):
                    row_data.append(data_collected[data_idx])
                    data_idx += 1
                else:
                    row_data.append("")
            
            table_lines.append("| " + " | ".join(row_data) + " |")
        
        table_lines.append("")
    
    return table_lines, i


def convert_markitdown_file(input_file: str, output_file: str = None) -> None:
    """Main conversion function."""
    if output_file is None:
        output_file = input_file.replace('.md', '_converted.md')
    
    # Load file with encoding detection
    encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin1']
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                content = f.read()
            lines = content.split('\n')
            print(f"✅ Loaded with {encoding} encoding ({len(lines)} lines)")
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f"Could not decode {input_file}")
    
    # Extract metadata and create frontmatter
    metadata = extract_metadata(content)
    output_lines = create_frontmatter(metadata)
    
    # Process lines
    i = 0
    in_highlights = False
    
    while i < len(lines):
        line = lines[i]
        cleaned_line = clean_text(line)
        
        # Skip empty lines at start
        if not cleaned_line and len(output_lines) <= 10:
            i += 1
            continue
        
        # Check for spaced headers
        if is_spaced_header(cleaned_line):
            header_level = 1
            if any(word in cleaned_line.lower() for word in ['summary', 'financial']):
                header_level = 2
            
            converted_header = convert_spaced_header(cleaned_line, header_level)
            output_lines.append(converted_header)
            output_lines.append("")
            
            # Track highlights section
            in_highlights = 'highlights' in cleaned_line.lower()
            
            # Try to extract table for financial sections
            if 'financial' in cleaned_line.lower():
                table_lines, next_i = extract_simple_table(lines, i + 1)
                if table_lines:
                    output_lines.extend(table_lines)
                    i = next_i
                    continue
            
            i += 1
            continue
        
        # Process regular lines
        if cleaned_line:
            if in_highlights:
                formatted_line = format_financial_metrics(cleaned_line)
            else:
                formatted_line = cleaned_line
            
            output_lines.append(formatted_line)
        else:
            output_lines.append("")
        
        i += 1
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"\n🎉 Conversion completed!")
    print(f"📄 Input: {input_file}")
    print(f"📄 Output: {output_file}")
    print(f"📊 Lines: {len(output_lines)}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert markitdown output to clean markdown"
    )
    parser.add_argument("input_file", help="Input markitdown file")
    parser.add_argument("output_file", nargs='?', help="Output file (optional)")
    
    args = parser.parse_args()
    
    if not Path(args.input_file).exists():
        print(f"❌ Error: {args.input_file} not found")
        sys.exit(1)
    
    try:
        convert_markitdown_file(args.input_file, args.output_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
