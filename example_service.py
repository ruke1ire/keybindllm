#!/usr/bin/env python3
"""
Example service implementation.
Shows how to create new AI services using the base infrastructure.

This example service:
1. Listens for Ctrl+Alt+1 (set REPHRASE_KEYNUM=1)
2. Takes any input text (doesn't require selection)
3. Summarizes the text using AI
4. Logs the result (doesn't replace text)
"""

import logging
from base_service import BaseAIService

logger = logging.getLogger(__name__)


class SummaryService(BaseAIService):
    """Example service for summarizing text using AI"""
    
    def __init__(self):
        super().__init__("Summary")
        self.system_prompt = ("Please provide a concise summary of the following text. "
                            "Keep it brief and capture the main points. "
                            "Return only the summary without any explanations.")
    
    def get_system_prompt(self) -> str:
        """Return the system prompt for summarization"""
        return self.system_prompt
    
    def get_input_text(self):
        """Get input text - for this example, we'll use clipboard content"""
        import subprocess
        
        try:
            logger.info("📖 Getting text from clipboard...")
            
            # Get clipboard content
            result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                  capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0 and result.stdout.strip():
                text = result.stdout.strip()
                logger.info(f"✓ Found text in clipboard: '{text[:50]}...'")
                return text
                
            logger.warning("⚠️  No text found in clipboard")
            return None
            
        except Exception as e:
            logger.warning(f"⚠️  Error getting text: {e}")
            return None
    
    def process_trigger(self):
        """Handle the summary trigger - main summary logic"""
        # Get input text (this service doesn't require text selection)
        input_text = self.get_input_text()
        if not input_text:
            logger.info("❌ No text available, ignoring")
            return
        
        logger.info("=" * 60)
        logger.info(f"📝 ORIGINAL TEXT:")
        logger.info(f"'{input_text}'")
        logger.info("=" * 60)
        
        # Summarize the text using the base service's ollama communication
        summary = self.send_to_ollama(self.get_system_prompt(), input_text)
        if not summary:
            logger.error("❌ Failed to summarize text")
            return
        
        logger.info("=" * 60)
        logger.info(f"📄 SUMMARY:")
        logger.info(f"'{summary}'")
        logger.info("=" * 60)
        
        # For this example, we just log the result
        # You could implement different actions here:
        # - Save to file
        # - Show in notification
        # - Copy to clipboard
        # - Replace text
        logger.info("✅ Summary completed successfully!")


def main():
    """Main entry point for the summary service"""
    try:
        service = SummaryService()
        service.run()
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Service failed: {e}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main() 