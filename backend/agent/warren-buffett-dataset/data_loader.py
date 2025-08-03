#!/usr/bin/env python3
"""
Warren Buffett Dataset Loader
Loads all text files from extracted_texts and transcripts_raw directories
"""

import os
from pathlib import Path
from typing import Dict, List


def load_all_warren_buffett_data() -> Dict[str, str]:
    """
    Load all Warren Buffett texts and transcripts
    
    Returns:
        Dict[str, str]: Dictionary with filename as key and content as value
    """
    base_dir = Path(__file__).parent
    extracted_texts_dir = base_dir / "extracted_texts"
    transcripts_dir = base_dir / "transcripts_raw"
    
    all_data = {}
    
    # Load extracted texts (books)
    if extracted_texts_dir.exists():
        for file_path in extracted_texts_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        all_data[f"BOOK_{file_path.stem}"] = content
                        print(f"Loaded book: {file_path.name} ({len(content):,} chars)")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    # Load transcripts
    if transcripts_dir.exists():
        for file_path in transcripts_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        all_data[f"TRANSCRIPT_{file_path.stem}"] = content
                        print(f"Loaded transcript: {file_path.name} ({len(content):,} chars)")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    return all_data


def create_knowledge_base_section(data: Dict[str, str]) -> str:
    """
    Create a formatted knowledge base section for system prompts
    
    Args:
        data: Dictionary of loaded Warren Buffett content
        
    Returns:
        str: Formatted knowledge base section
    """
    sections = []
    
    # Group by type
    books = {k: v for k, v in data.items() if k.startswith("BOOK_")}
    transcripts = {k: v for k, v in data.items() if k.startswith("TRANSCRIPT_")}
    
    # Books section
    if books:
        sections.append("========================================")
        sections.append("WARREN BUFFETT BOOKS & LITERATURE")
        sections.append("========================================")
        
        for key, content in books.items():
            book_name = key.replace("BOOK_", "").replace("_", " ").title()
            sections.append(f"\n--- {book_name} ---")
            sections.append(content)
    
    # Transcripts section
    if transcripts:
        sections.append("\n========================================")
        sections.append("WARREN BUFFETT INTERVIEWS & TRANSCRIPTS")
        sections.append("========================================")
        
        for key, content in transcripts.items():
            transcript_name = key.replace("TRANSCRIPT_", "").replace("_", " ").title()
            sections.append(f"\n--- {transcript_name} ---")
            sections.append(content)
    
    return "\n".join(sections)


def main():
    """Main function to load and display data statistics"""
    print("Loading Warren Buffett dataset...")
    data = load_all_warren_buffett_data()
    
    if not data:
        print("No data found!")
        return
    
    print(f"\nLoaded {len(data)} files:")
    
    total_chars = 0
    books_count = 0
    transcripts_count = 0
    
    for key, content in data.items():
        char_count = len(content)
        total_chars += char_count
        
        if key.startswith("BOOK_"):
            books_count += 1
        elif key.startswith("TRANSCRIPT_"):
            transcripts_count += 1
        
        print(f"  {key}: {char_count:,} characters")
    
    print(f"\nSummary:")
    print(f"  Books: {books_count}")
    print(f"  Transcripts: {transcripts_count}")
    print(f"  Total characters: {total_chars:,}")
    
    # Create knowledge base section
    knowledge_base = create_knowledge_base_section(data)
    
    # Save to file for inspection
    output_file = Path(__file__).parent / "warren_buffett_knowledge_base.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(knowledge_base)
    
    print(f"\nKnowledge base section saved to: {output_file}")
    print(f"Knowledge base size: {len(knowledge_base):,} characters")


if __name__ == "__main__":
    main()