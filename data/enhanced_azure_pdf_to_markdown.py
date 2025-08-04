#!/usr/bin/env python3
"""
Clean Azure Document Intelligence PDF to Markdown Converter

Uses Azure's native markdown output for high-quality conversion.

IMPORTANT: Free tier (F0) processes only the first 2 pages of any document.
For full document processing, upgrade to paid tier (S0).

Prerequisites:
    pip install azure-ai-documentintelligence python-dotenv
"""

import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("💡 Install python-dotenv for .env file support: pip install python-dotenv")

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentContentFormat


def smart_chunk_markdown(markdown_content: str, base_filename: str, max_chunk_size: int = 4000) -> list[str]:
    """
    Intelligently chunk markdown content while preserving table and section integrity.
    
    Args:
        markdown_content: The markdown content to chunk
        base_filename: Base filename for chunk files (without extension)
        max_chunk_size: Maximum characters per chunk (approximate)
    
    Returns:
        List of created chunk filenames
    """
    print(f"\n🧩 Starting intelligent chunking (max ~{max_chunk_size} chars per chunk)...")
    
    lines = markdown_content.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0
    in_table = False
    in_html_table = False
    chunk_files = []
    
    for i, line in enumerate(lines):
        line_size = len(line) + 1  # +1 for newline
        
        # Detect table boundaries
        if line.strip().startswith('|') and '|' in line.strip()[1:]:
            in_table = True
        elif in_table and line.strip() == '' and i + 1 < len(lines):
            # Check if next non-empty line is still a table
            next_content_line = next((lines[j] for j in range(i + 1, len(lines)) if lines[j].strip()), '')
            if not (next_content_line.startswith('|') and '|' in next_content_line[1:]):
                in_table = False
        
        # Detect HTML table boundaries
        if '<table>' in line.lower():
            in_html_table = True
        elif '</table>' in line.lower():
            in_html_table = False
        
        # Check if we should start a new chunk
        should_break = (
            current_size + line_size > max_chunk_size and  # Size limit reached
            not in_table and  # Not in a markdown table
            not in_html_table and  # Not in an HTML table
            current_chunk and  # Not empty chunk
            (line.startswith('#') or  # New section header
             (line.strip() == '' and i + 1 < len(lines) and lines[i + 1].startswith('#')))  # Empty line before header
        )
        
        if should_break:
            # Save current chunk
            chunk_content = '\n'.join(current_chunk).strip()
            if chunk_content:
                chunk_filename = f"{base_filename}_chunk_{len(chunks) + 1:02d}.md"
                with open(chunk_filename, 'w', encoding='utf-8') as f:
                    f.write(chunk_content)
                chunks.append(chunk_content)
                chunk_files.append(chunk_filename)
                print(f"📄 Created chunk {len(chunks)}: {chunk_filename} ({current_size} chars)")
            
            # Start new chunk
            current_chunk = [line] if line.strip() else []
            current_size = line_size if line.strip() else 0
        else:
            # Add line to current chunk
            current_chunk.append(line)
            current_size += line_size
    
    # Save final chunk
    if current_chunk:
        chunk_content = '\n'.join(current_chunk).strip()
        if chunk_content:
            chunk_filename = f"{base_filename}_chunk_{len(chunks) + 1:02d}.md"
            with open(chunk_filename, 'w', encoding='utf-8') as f:
                f.write(chunk_content)
            chunks.append(chunk_content)
            chunk_files.append(chunk_filename)
            print(f"📄 Created chunk {len(chunks)}: {chunk_filename} ({current_size} chars)")
    
    print(f"✅ Created {len(chunk_files)} intelligent chunks")
    return chunk_files


def convert_pdf_to_markdown(pdf_path: str = "PL-200T00A-ENU-TrainerPrepGuide.pdf", output_path: str = None, create_chunks: bool = True, chunk_size: int = 4000) -> str:
    """Convert PDF to markdown using Azure Document Intelligence with optional chunking."""
    
    # Configuration
    endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT') or "https://leanrag.cognitiveservices.azure.com/"
    key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    if not key:
        raise ValueError("Azure Document Intelligence key not found. Please set AZURE_DOCUMENT_INTELLIGENCE_KEY in .env file")
    
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Determine output path
    base_filename = Path(pdf_path).stem
    if output_path is None:
        output_path = f"{base_filename}_azure_clean.md"
    
    print(f"✅ Converting {pdf_path} to {output_path}")
    if create_chunks:
        print(f"🧩 Will create intelligent chunks (~{chunk_size} chars each)")
    print(f"📍 Endpoint: {endpoint}")
    
    # Initialize client
    client = DocumentIntelligenceClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(key)
    )
    
    # Read PDF
    with open(pdf_path, "rb") as pdf_file:
        pdf_content = pdf_file.read()
    
    print("🔍 Starting Azure analysis with native markdown output...")
    
    # Use Azure's built-in markdown conversion
    poller = client.begin_analyze_document(
        "prebuilt-layout", 
        AnalyzeDocumentRequest(bytes_source=pdf_content),
        output_content_format=DocumentContentFormat.MARKDOWN
    )
    
    print("⏳ Waiting for analysis to complete...")
    result = poller.result()
    
    print(f"✅ Analysis completed!")
    print(f"📊 Format: {result.content_format}")
    print(f"📄 Pages: {len(result.pages)}")
    
    # Log structural elements for intelligent chunking
    if hasattr(result, 'sections') and result.sections:
        print(f"📑 Sections found: {len(result.sections)}")
    if hasattr(result, 'tables') and result.tables:
        print(f"📋 Tables found: {len(result.tables)}")
    if hasattr(result, 'paragraphs') and result.paragraphs:
        print(f"📝 Paragraphs found: {len(result.paragraphs)}")
    
    # Check if we hit the free tier limit
    if len(result.pages) == 2:
        print("⚠️  NOTE: Only 2 pages processed. If this is unexpected, check your Azure pricing tier.")
    else:
        print(f"🎉 Processed full document: {len(result.pages)} pages (paid tier active)")
    
    if hasattr(result, 'content') and result.content:
        # Save complete Azure markdown
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.content)
        
        print(f"💾 Saved complete markdown to: {output_path}")
        print(f"📏 Content length: {len(result.content)} characters")
        
        # Create intelligent chunks if requested
        if create_chunks:
            chunk_files = smart_chunk_markdown(result.content, base_filename, chunk_size)
            print(f"📦 Created {len(chunk_files)} chunk files")
            return output_path, chunk_files
        
        return output_path
    else:
        raise Exception("No markdown content found in Azure response")


def main():
    """Main function for debugging."""
    import sys
    
    # Check if PDF file is provided as command line argument
    pdf_file = sys.argv[1] if len(sys.argv) > 1 else "PL-200T00A-ENU-TrainerPrepGuide.pdf"
    
    try:
        result = convert_pdf_to_markdown(pdf_file)
        
        if isinstance(result, tuple):
            output_file, chunk_files = result
            print(f"\n🎉 Success! Azure native markdown: {output_file}")
            print(f"📦 Created {len(chunk_files)} chunk files:")
            for chunk_file in chunk_files:
                print(f"   📄 {chunk_file}")
        else:
            print(f"\n🎉 Success! Azure native markdown: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
