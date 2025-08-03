#!/usr/bin/env python3
"""
Simple PDF to Text Converter
Extracts text from PDF files using pdfminer.six
"""

import os
import sys
from pathlib import Path
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams


def pdf_to_text(pdf_path, output_path=None):
    """
    Convert PDF to text file
    
    Args:
        pdf_path (str): Path to the PDF file
        output_path (str, optional): Path for output text file. If None, uses PDF name with .txt extension
    
    Returns:
        str: Extracted text content
    """
    try:
        # Extract text from PDF
        print(f"Extracting text from: {pdf_path}")
        
        # Configure layout parameters for better text extraction
        laparams = LAParams(
            boxes_flow=0.5,
            word_margin=0.1,
            char_margin=2.0,
            line_margin=0.5
        )
        
        text = extract_text(pdf_path, laparams=laparams)
        
        # Clean up the text
        text = text.strip()
        
        # Determine output path
        if output_path is None:
            pdf_file = Path(pdf_path)
            output_path = pdf_file.parent / f"{pdf_file.stem}.txt"
        
        # Write to text file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Text extracted successfully!")
        print(f"Output saved to: {output_path}")
        print(f"Text length: {len(text)} characters")
        
        return text
        
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_txt_converter.py <pdf_file> [output_file]")
        print("Example: python pdf_to_txt_converter.py document.pdf")
        print("Example: python pdf_to_txt_converter.py document.pdf output.txt")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check if PDF file exists
    if not os.path.exists(pdf_file):
        print(f"Error: PDF file '{pdf_file}' not found!")
        sys.exit(1)
    
    # Convert PDF to text
    text = pdf_to_text(pdf_file, output_file)
    
    if text:
        print("\n" + "="*50)
        print("PREVIEW (first 500 characters):")
        print("="*50)
        print(text[:500])
        if len(text) > 500:
            print("...")
        print("="*50)


if __name__ == "__main__":
    main()