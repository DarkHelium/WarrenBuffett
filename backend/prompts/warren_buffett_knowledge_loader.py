#!/usr/bin/env python3
"""
Warren Buffett Knowledge Loader
Provides access to the complete Warren Buffett dataset for system prompts
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import json


class WarrenBuffettKnowledgeBase:
    """
    Loads and provides access to Warren Buffett books, transcripts, and interviews
    """
    
    def __init__(self):
        self._data = None
        self._books = None
        self._transcripts = None
        self._loaded = False
    
    def _load_data(self):
        """Load all Warren Buffett data from files"""
        if self._loaded:
            return
        
        base_dir = Path(__file__).parent.parent / "agent" / "warren-buffett-dataset"
        extracted_texts_dir = base_dir / "extracted_texts"
        transcripts_dir = base_dir / "transcripts_raw"
        knowledge_base_file = base_dir / "warren_buffett_knowledge_base.txt"
        
        self._data = {}
        self._books = {}
        self._transcripts = {}
        
        # Load extracted texts (books)
        if extracted_texts_dir.exists():
            for file_path in extracted_texts_dir.glob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            key = f"BOOK_{file_path.stem}"
                            self._data[key] = content
                            self._books[file_path.stem] = content
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        # Load transcripts
        if transcripts_dir.exists():
            for file_path in transcripts_dir.glob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            key = f"TRANSCRIPT_{file_path.stem}"
                            self._data[key] = content
                            self._transcripts[file_path.stem] = content
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        # Load main knowledge base file
        if knowledge_base_file.exists():
            try:
                with open(knowledge_base_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self._data["KNOWLEDGE_BASE"] = content
            except Exception as e:
                print(f"Error loading {knowledge_base_file}: {e}")
        
        self._loaded = True
    
    def get_all_data(self) -> Dict[str, str]:
        """Get all Warren Buffett data"""
        self._load_data()
        return self._data.copy()
    
    def get_books(self) -> Dict[str, str]:
        """Get all Warren Buffett books"""
        self._load_data()
        return self._books.copy()
    
    def get_transcripts(self) -> Dict[str, str]:
        """Get all Warren Buffett transcripts and interviews"""
        self._load_data()
        return self._transcripts.copy()
    
    def search_content(self, query: str, case_sensitive: bool = False) -> List[Dict[str, str]]:
        """
        Search for content across all Warren Buffett data
        
        Args:
            query: Search term
            case_sensitive: Whether to perform case-sensitive search
            
        Returns:
            List of matches with source and excerpt
        """
        self._load_data()
        matches = []
        
        search_query = query if case_sensitive else query.lower()
        
        for source, content in self._data.items():
            search_content = content if case_sensitive else content.lower()
            
            if search_query in search_content:
                # Find the position and extract context
                pos = search_content.find(search_query)
                start = max(0, pos - 200)
                end = min(len(content), pos + len(query) + 200)
                excerpt = content[start:end]
                
                matches.append({
                    'source': source,
                    'excerpt': excerpt,
                    'position': pos
                })
        
        return matches
    
    def get_formatted_knowledge_base(self) -> str:
        """
        Get the complete formatted knowledge base for system prompts
        
        Returns:
            str: Formatted knowledge base content
        """
        self._load_data()
        
        sections = []
        
        # Main knowledge base file
        if "KNOWLEDGE_BASE" in self._data:
            sections.append("========================================")
            sections.append("WARREN BUFFETT COMPREHENSIVE KNOWLEDGE BASE")
            sections.append("========================================")
            sections.append(self._data["KNOWLEDGE_BASE"])
        
        # Books section
        if self._books:
            sections.append("========================================")
            sections.append("WARREN BUFFETT BOOKS & LITERATURE")
            sections.append("========================================")
            sections.append("The following books contain Warren Buffett's investment philosophy, strategies, and wisdom:")
            
            for filename, content in self._books.items():
                book_name = filename.replace("_", " ").replace("(Z-Library)", "").strip()
                sections.append(f"\n--- {book_name} ---")
                sections.append(content)
        
        # Transcripts section
        if self._transcripts:
            sections.append("\n========================================")
            sections.append("WARREN BUFFETT INTERVIEWS & TRANSCRIPTS")
            sections.append("========================================")
            sections.append("The following transcripts contain Warren Buffett's actual words from interviews, shareholder meetings, and speeches:")
            
            for filename, content in self._transcripts.items():
                transcript_name = filename.replace("_", " ").replace("-", " ").title()
                sections.append(f"\n--- {transcript_name} ---")
                sections.append(content)
        
        return "\n".join(sections)
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the knowledge base"""
        self._load_data()
        
        total_chars = sum(len(content) for content in self._data.values())
        
        return {
            'total_files': len(self._data),
            'books_count': len(self._books),
            'transcripts_count': len(self._transcripts),
            'knowledge_base_included': 1 if "KNOWLEDGE_BASE" in self._data else 0,
            'total_characters': total_chars,
            'total_words': sum(len(content.split()) for content in self._data.values())
        }


# Global instance
_knowledge_base = WarrenBuffettKnowledgeBase()


def get_warren_buffett_knowledge() -> str:
    """
    Get the complete Warren Buffett knowledge base for system prompts
    
    Returns:
        str: Formatted knowledge base content
    """
    return _knowledge_base.get_formatted_knowledge_base()


def search_warren_buffett_content(query: str) -> List[Dict[str, str]]:
    """
    Search Warren Buffett content for specific terms
    
    Args:
        query: Search term
        
    Returns:
        List of matches with source and excerpt
    """
    return _knowledge_base.search_content(query)


def get_knowledge_stats() -> Dict[str, int]:
    """Get statistics about the Warren Buffett knowledge base"""
    return _knowledge_base.get_stats()


if __name__ == "__main__":
    # Test the knowledge base
    kb = WarrenBuffettKnowledgeBase()
    stats = kb.get_stats()
    
    print("Warren Buffett Knowledge Base Statistics:")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Books: {stats['books_count']}")
    print(f"  Transcripts: {stats['transcripts_count']}")
    print(f"  Total characters: {stats['total_characters']:,}")
    print(f"  Total words: {stats['total_words']:,}")
    
    # Test search
    print("\nTesting search for 'circle of competence':")
    matches = kb.search_content("circle of competence")
    print(f"Found {len(matches)} matches")
    
    for i, match in enumerate(matches[:3]):  # Show first 3 matches
        print(f"\nMatch {i+1} from {match['source']}:")
        print(f"  {match['excerpt'][:200]}...")