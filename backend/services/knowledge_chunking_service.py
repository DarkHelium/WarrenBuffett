"""
Knowledge Chunking Service
Breaks down the massive Warren Buffett knowledge base into manageable chunks
and processes them through multiple AI calls to stay within token limits.
"""

import asyncio
import tiktoken
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import json

from core.config import Config
from prompts.warren_buffett_knowledge_loader import get_warren_buffett_knowledge
from services.llm_service import LLMService

logger = logging.getLogger(__name__)


class KnowledgeChunkingService:
    """
    Service to chunk and process Warren Buffett knowledge base
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.llm_service = LLMService(config)
        self.encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        self.max_tokens_per_chunk = 8000  # Conservative limit for gpt-4o-mini
        self.overlap_tokens = 200  # Overlap between chunks for context
        self.processed_knowledge = {}
        self.knowledge_summaries = []
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def chunk_knowledge_base(self, knowledge_text: str) -> List[str]:
        """
        Break down the knowledge base into manageable chunks
        """
        chunks = []
        tokens = self.encoding.encode(knowledge_text)
        
        start_idx = 0
        while start_idx < len(tokens):
            # Calculate end index for this chunk
            end_idx = min(start_idx + self.max_tokens_per_chunk, len(tokens))
            
            # Extract chunk tokens
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            chunks.append(chunk_text)
            
            # Move start index with overlap
            start_idx = end_idx - self.overlap_tokens
            
            if start_idx >= len(tokens):
                break
        
        logger.info(f"Created {len(chunks)} knowledge chunks")
        return chunks
    
    async def process_knowledge_chunk(self, chunk: str, chunk_index: int) -> Dict[str, Any]:
        """
        Process a single knowledge chunk using LLM
        """
        try:
            # Create a specialized prompt for this chunk
            processing_prompt = f"""
            You are analyzing Warren Buffett knowledge chunk {chunk_index + 1}.
            
            Your task is to extract and structure the most important information:
            
            1. INVESTMENT PRINCIPLES: List key investment principles mentioned
            2. STRATEGIES: Identify specific investment strategies and methodologies
            3. METRICS: Note any quantitative criteria or metrics mentioned
            4. INSIGHTS: Capture key insights and wisdom
            5. QUOTES: Extract memorable quotes (if any)
            
            Knowledge chunk:
            {chunk}
            
            Please provide a structured response in this format:
            PRINCIPLES:
            - [principle 1]
            - [principle 2]
            
            STRATEGIES:
            - [strategy 1]
            - [strategy 2]
            
            METRICS:
            - [metric 1]
            - [metric 2]
            
            INSIGHTS:
            - [insight 1]
            - [insight 2]
            
            QUOTES:
            - "[quote 1]"
            - "[quote 2]"
            """
            
            # Process with LLM
            response = await self.llm_service.generate_response(processing_prompt)
            
            # Parse the structured response
            parsed_result = self._parse_structured_response(response)
            
            return {
                'chunk_index': chunk_index,
                'principles': parsed_result.get('principles', []),
                'strategies': parsed_result.get('strategies', []),
                'metrics': parsed_result.get('metrics', []),
                'insights': parsed_result.get('insights', []),
                'quotes': parsed_result.get('quotes', []),
                'raw_response': response,
                'processed': True
            }
            
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_index}: {e}")
            return {
                'chunk_index': chunk_index,
                'error': str(e),
                'processed': False
            }
    
    def _parse_structured_response(self, response: str) -> Dict[str, List[str]]:
        """Parse the structured response from LLM"""
        result = {
            'principles': [],
            'strategies': [],
            'metrics': [],
            'insights': [],
            'quotes': []
        }
        
        current_section = None
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if line.upper().startswith('PRINCIPLES:'):
                current_section = 'principles'
                continue
            elif line.upper().startswith('STRATEGIES:'):
                current_section = 'strategies'
                continue
            elif line.upper().startswith('METRICS:'):
                current_section = 'metrics'
                continue
            elif line.upper().startswith('INSIGHTS:'):
                current_section = 'insights'
                continue
            elif line.upper().startswith('QUOTES:'):
                current_section = 'quotes'
                continue
            
            # Extract list items
            if current_section and line.startswith('- '):
                item = line[2:].strip()
                if item:
                    result[current_section].append(item)
        
        return result
    
    async def process_full_knowledge_base(self) -> Dict[str, Any]:
        """
        Process the entire Warren Buffett knowledge base in chunks
        """
        logger.info("Starting full knowledge base processing...")
        
        # Load the complete knowledge base
        full_knowledge = get_warren_buffett_knowledge()
        total_tokens = self.count_tokens(full_knowledge)
        
        logger.info(f"Total knowledge base tokens: {total_tokens:,}")
        
        # Break into chunks
        chunks = self.chunk_knowledge_base(full_knowledge)
        
        # Process chunks with rate limiting
        processed_chunks = []
        semaphore = asyncio.Semaphore(2)  # Limit concurrent processing to avoid rate limits
        
        async def process_with_semaphore(chunk, index):
            async with semaphore:
                result = await self.process_knowledge_chunk(chunk, index)
                # Add a small delay to avoid rate limiting
                await asyncio.sleep(1)
                return result
        
        # Process all chunks
        tasks = [
            process_with_semaphore(chunk, i) 
            for i, chunk in enumerate(chunks)
        ]
        
        processed_chunks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile results
        successful_chunks = [
            chunk for chunk in processed_chunks 
            if isinstance(chunk, dict) and chunk.get('processed', False)
        ]
        
        failed_chunks = [
            chunk for chunk in processed_chunks 
            if isinstance(chunk, Exception) or not chunk.get('processed', False)
        ]
        
        # Aggregate insights
        aggregated_knowledge = self._aggregate_processed_chunks(successful_chunks)
        
        logger.info(f"Successfully processed {len(successful_chunks)}/{len(chunks)} chunks")
        if failed_chunks:
            logger.warning(f"Failed to process {len(failed_chunks)} chunks")
        
        return {
            'total_chunks': len(chunks),
            'successful_chunks': len(successful_chunks),
            'failed_chunks': len(failed_chunks),
            'aggregated_knowledge': aggregated_knowledge,
            'processing_stats': {
                'total_tokens': total_tokens,
                'tokens_per_chunk': self.max_tokens_per_chunk,
                'overlap_tokens': self.overlap_tokens
            }
        }
    
    def _aggregate_processed_chunks(self, processed_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate insights from all processed chunks
        """
        all_principles = []
        all_strategies = []
        all_metrics = []
        all_insights = []
        all_quotes = []
        
        for chunk in processed_chunks:
            if chunk.get('principles'):
                all_principles.extend(chunk['principles'])
            if chunk.get('strategies'):
                all_strategies.extend(chunk['strategies'])
            if chunk.get('metrics'):
                all_metrics.extend(chunk['metrics'])
            if chunk.get('insights'):
                all_insights.extend(chunk['insights'])
            if chunk.get('quotes'):
                all_quotes.extend(chunk['quotes'])
        
        return {
            'investment_principles': list(set(all_principles)),  # Remove duplicates
            'investment_strategies': list(set(all_strategies)),
            'quantitative_metrics': list(set(all_metrics)),
            'key_insights': list(set(all_insights)),
            'memorable_quotes': list(set(all_quotes)),
            'total_processed_chunks': len(processed_chunks)
        }
    
    def get_condensed_knowledge_for_prompt(self) -> str:
        """
        Get a condensed version of the processed knowledge for system prompts
        """
        if not self.processed_knowledge:
            logger.warning("Knowledge base not yet processed")
            return ""
        
        aggregated = self.processed_knowledge.get('aggregated_knowledge', {})
        
        condensed_prompt = f"""
WARREN BUFFETT INVESTMENT WISDOM (Processed from {aggregated.get('total_processed_chunks', 0)} knowledge chunks)

KEY INVESTMENT PRINCIPLES:
{chr(10).join(f"• {principle}" for principle in aggregated.get('investment_principles', [])[:25])}

INVESTMENT STRATEGIES:
{chr(10).join(f"• {strategy}" for strategy in aggregated.get('investment_strategies', [])[:20])}

QUANTITATIVE METRICS & CRITERIA:
{chr(10).join(f"• {metric}" for metric in aggregated.get('quantitative_metrics', [])[:15])}

CRITICAL INSIGHTS:
{chr(10).join(f"• {insight}" for insight in aggregated.get('key_insights', [])[:20])}

MEMORABLE QUOTES:
{chr(10).join(f'• "{quote}"' for quote in aggregated.get('memorable_quotes', [])[:10])}
"""
        
        return condensed_prompt
    
    async def initialize_knowledge_base(self) -> bool:
        """
        Initialize and process the knowledge base
        """
        try:
            self.processed_knowledge = await self.process_full_knowledge_base()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {e}")
            return False
    
    def save_processed_knowledge(self, filepath: str):
        """Save processed knowledge to file in JSON Lines (.jsonl) format"""
        # Ensure the file has a .jsonl extension
        filepath = str(Path(filepath).with_suffix('.jsonl'))
        with open(filepath, 'w', encoding='utf-8') as f:
            # Each processed knowledge object is written on a single line
            json.dump(self.processed_knowledge, f, ensure_ascii=False)
            f.write('\n')
    
    def load_processed_knowledge(self, filepath: str) -> bool:
        """Load processed knowledge from file in JSON Lines (.jsonl) format"""
        try:
            filepath = str(Path(filepath).with_suffix('.jsonl'))
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                self.processed_knowledge = json.loads(first_line) if first_line else {}
            return True
        except Exception as e:
            logger.error(f"Failed to load processed knowledge: {e}")
            return False
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def chunk_knowledge_base(self, knowledge_text: str) -> List[str]:
        """
        Break down the knowledge base into manageable chunks
        """
        chunks = []
        tokens = self.encoding.encode(knowledge_text)
        
        start_idx = 0
        while start_idx < len(tokens):
            # Calculate end index for this chunk
            end_idx = min(start_idx + self.max_tokens_per_chunk, len(tokens))
            
            # Extract chunk tokens
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            chunks.append(chunk_text)
            
            # Move start index with overlap
            start_idx = end_idx - self.overlap_tokens
            
            if start_idx >= len(tokens):
                break
        
        logger.info(f"Created {len(chunks)} knowledge chunks")
        return chunks
    
    async def process_knowledge_chunk(self, chunk: str, chunk_index: int) -> Dict[str, Any]:
        """
        Process a single knowledge chunk using SmolAgent
        """
        try:
            # Create a specialized prompt for this chunk
            processing_prompt = f"""
            You are analyzing Warren Buffett knowledge chunk {chunk_index + 1}.
            
            Your task is to:
            1. Extract the most important investment principles
            2. Identify specific strategies and methodologies
            3. Note any quantitative metrics or criteria mentioned
            4. Capture memorable quotes or key insights
            5. Summarize actionable advice
            
            Knowledge chunk:
            {chunk}
            
            Please provide a structured analysis focusing on practical investment wisdom.
            """
            
            # Process with SmolAgent
            result = await asyncio.to_thread(
                self.agent.run,
                processing_prompt
            )
            
            return {
                'chunk_index': chunk_index,
                'summary': result.get('summary', ''),
                'principles': result.get('principles', []),
                'insights': result.get('insights', []),
                'quotes': result.get('quotes', []),
                'metrics': result.get('metrics', {}),
                'processed': True
            }
            
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_index}: {e}")
            return {
                'chunk_index': chunk_index,
                'error': str(e),
                'processed': False
            }
    
    async def process_full_knowledge_base(self) -> Dict[str, Any]:
        """
        Process the entire Warren Buffett knowledge base in chunks
        """
        logger.info("Starting full knowledge base processing...")
        
        # Load the complete knowledge base
        full_knowledge = get_warren_buffett_knowledge()
        total_tokens = self.count_tokens(full_knowledge)
        
        logger.info(f"Total knowledge base tokens: {total_tokens:,}")
        
        # Break into chunks
        chunks = self.chunk_knowledge_base(full_knowledge)
        
        # Process chunks concurrently (but with rate limiting)
        processed_chunks = []
        semaphore = asyncio.Semaphore(3)  # Limit concurrent processing
        
        async def process_with_semaphore(chunk, index):
            async with semaphore:
                return await self.process_knowledge_chunk(chunk, index)
        
        # Process all chunks
        tasks = [
            process_with_semaphore(chunk, i) 
            for i, chunk in enumerate(chunks)
        ]
        
        processed_chunks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile results
        successful_chunks = [
            chunk for chunk in processed_chunks 
            if isinstance(chunk, dict) and chunk.get('processed', False)
        ]
        
        failed_chunks = [
            chunk for chunk in processed_chunks 
            if isinstance(chunk, Exception) or not chunk.get('processed', False)
        ]
        
        # Aggregate insights
        aggregated_knowledge = self._aggregate_processed_chunks(successful_chunks)
        
        logger.info(f"Successfully processed {len(successful_chunks)}/{len(chunks)} chunks")
        if failed_chunks:
            logger.warning(f"Failed to process {len(failed_chunks)} chunks")
        
        return {
            'total_chunks': len(chunks),
            'successful_chunks': len(successful_chunks),
            'failed_chunks': len(failed_chunks),
            'aggregated_knowledge': aggregated_knowledge,
            'processing_stats': {
                'total_tokens': total_tokens,
                'tokens_per_chunk': self.max_tokens_per_chunk,
                'overlap_tokens': self.overlap_tokens
            }
        }
    
    def _aggregate_processed_chunks(self, processed_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate insights from all processed chunks
        """
        all_principles = []
        all_insights = []
        all_quotes = []
        all_metrics = {}
        summaries = []
        
        for chunk in processed_chunks:
            if chunk.get('principles'):
                all_principles.extend(chunk['principles'])
            if chunk.get('insights'):
                all_insights.extend(chunk['insights'])
            if chunk.get('quotes'):
                all_quotes.extend(chunk['quotes'])
            if chunk.get('metrics'):
                all_metrics.update(chunk['metrics'])
            if chunk.get('summary'):
                summaries.append(chunk['summary'])
        
        return {
            'investment_principles': list(set(all_principles)),  # Remove duplicates
            'key_insights': list(set(all_insights)),
            'memorable_quotes': list(set(all_quotes)),
            'quantitative_metrics': all_metrics,
            'chunk_summaries': summaries,
            'total_processed_chunks': len(processed_chunks)
        }
    
    def get_condensed_knowledge_for_prompt(self) -> str:
        """
        Get a condensed version of the processed knowledge for system prompts
        """
        if not self.processed_knowledge:
            logger.warning("Knowledge base not yet processed")
            return ""
        
        aggregated = self.processed_knowledge.get('aggregated_knowledge', {})
        
        condensed_prompt = f"""
WARREN BUFFETT INVESTMENT WISDOM (Processed from {aggregated.get('total_processed_chunks', 0)} knowledge chunks)

KEY INVESTMENT PRINCIPLES:
{chr(10).join(f"• {principle}" for principle in aggregated.get('investment_principles', [])[:20])}

CRITICAL INSIGHTS:
{chr(10).join(f"• {insight}" for insight in aggregated.get('key_insights', [])[:15])}

MEMORABLE QUOTES:
{chr(10).join(f'• "{quote}"' for quote in aggregated.get('memorable_quotes', [])[:10])}

QUANTITATIVE METRICS:
{chr(10).join(f"• {metric}: {value}" for metric, value in aggregated.get('quantitative_metrics', {}).items())}
"""
        
        return condensed_prompt
    
    async def initialize_knowledge_base(self) -> bool:
        """
        Initialize and process the knowledge base
        """
        try:
            self.processed_knowledge = await self.process_full_knowledge_base()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {e}")
            return False
    
    def save_processed_knowledge(self, filepath: str):
        """Save processed knowledge to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.processed_knowledge, f, indent=2, ensure_ascii=False)
    
    def load_processed_knowledge(self, filepath: str) -> bool:
        """Load processed knowledge from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.processed_knowledge = json.load(f)
            return True
        except Exception as e:
            logger.error(f"Failed to load processed knowledge: {e}")
            return False