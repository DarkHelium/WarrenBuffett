#!/usr/bin/env python3
"""
Test script for the enhanced Warren Buffett system prompts with knowledge base
"""

import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_enhanced_prompts():
    """Test the enhanced Warren Buffett system prompts"""
    
    print("Testing Enhanced Warren Buffett System Prompts")
    print("=" * 50)
    
    try:
        from prompts.system_prompts import (
            WARREN_BUFFETT_SYSTEM_PROMPT,
            get_enhanced_warren_buffett_prompt,
            search_buffett_knowledge,
            get_buffett_knowledge_stats
        )
        
        # Test 1: Basic prompt (backward compatibility)
        print("\n1. Testing basic prompt (backward compatibility):")
        basic_prompt = WARREN_BUFFETT_SYSTEM_PROMPT
        print(f"Basic prompt length: {len(basic_prompt):,} characters")
        print(f"First 200 characters: {basic_prompt[:200]}...")
        
        # Test 2: Enhanced prompt with knowledge base
        print("\n2. Testing enhanced prompt with knowledge base:")
        enhanced_prompt = get_enhanced_warren_buffett_prompt()
        print(f"Enhanced prompt length: {len(enhanced_prompt):,} characters")
        print(f"Knowledge base included: {'WARREN BUFFETT COMPLETE KNOWLEDGE BASE' in enhanced_prompt}")
        
        # Test 3: Knowledge base statistics
        print("\n3. Testing knowledge base statistics:")
        stats = get_buffett_knowledge_stats()
        if stats:
            print(f"Books: {stats.get('books_count', 'N/A')}")
            print(f"Transcripts: {stats.get('transcripts_count', 'N/A')}")
            print(f"Total characters: {stats.get('total_characters', 'N/A'):,}")
            print(f"Total words: {stats.get('total_words', 'N/A'):,}")
        else:
            print("Knowledge base statistics not available")
        
        # Test 4: Search functionality
        print("\n4. Testing search functionality:")
        search_terms = ["circle of competence", "intrinsic value", "margin of safety"]
        
        for term in search_terms:
            matches = search_buffett_knowledge(term)
            print(f"Search for '{term}': {len(matches)} matches found")
            if matches:
                # Show first match preview
                first_match = matches[0]
                preview = first_match.get('content', '')[:100] + "..." if len(first_match.get('content', '')) > 100 else first_match.get('content', '')
                print(f"  First match from {first_match.get('source', 'Unknown')}: {preview}")
        
        # Test 5: Prompt comparison
        print("\n5. Prompt size comparison:")
        size_difference = len(enhanced_prompt) - len(basic_prompt)
        print(f"Basic prompt: {len(basic_prompt):,} characters")
        print(f"Enhanced prompt: {len(enhanced_prompt):,} characters")
        print(f"Knowledge base adds: {size_difference:,} characters")
        print(f"Enhancement factor: {len(enhanced_prompt) / len(basic_prompt):.1f}x larger")
        
        print("\n✅ All tests completed successfully!")
        print("\nUsage recommendations:")
        print("- Use WARREN_BUFFETT_SYSTEM_PROMPT for basic analysis")
        print("- Use get_enhanced_warren_buffett_prompt() for comprehensive analysis with full knowledge")
        print("- Use search_buffett_knowledge() to find specific content")
        print("- Use get_buffett_knowledge_stats() to get knowledge base information")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure the warren_buffett_knowledge_loader.py is in the correct location")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_enhanced_prompts()