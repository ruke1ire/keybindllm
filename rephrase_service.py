#!/usr/bin/env python3
"""
Rephrase service implementation.
Handles text selection, rephrasing via Ollama, and text replacement.
"""

import subprocess
import time
import logging
from base_service import BaseAIService

logger = logging.getLogger(__name__)


class RephraseService(BaseAIService):
    """Service for rephrasing selected text using AI"""
    
    def __init__(self):
        super().__init__("Rephrase")
        self.system_prompt = ("Please correct any grammatical errors and make improvements to the writing "
                            "while keeping the original tone and meaning. If you cannot rephrase it, "
                            "or change is not needed, return <null>. Return only the improved text "
                            "without any explanations or additional commentary.")
    
    def get_system_prompt(self) -> str:
        """Return the system prompt for rephrasing"""
        return self.system_prompt
    
    def get_selected_text(self):
        """Get currently selected text using xclip"""
        try:
            logger.info("📖 Attempting to get selected text...")

            # Try primary selection first (X11 mouse selection)
            result = subprocess.run(['xclip', '-selection', 'primary', '-o'], 
                                  capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0 and result.stdout.strip():
                selected_text = result.stdout.strip()
                logger.info(f"✓ Found text in primary selection: '{selected_text[:30]}...'")
                return selected_text
            
            logger.warning("⚠️  No text found in primary selection")
            return None
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  xclip failed: {e}")
            return None
        except subprocess.TimeoutExpired:
            logger.warning("⚠️  xclip timed out")
            return None
        except Exception as e:
            logger.warning(f"⚠️  Unexpected error getting selected text: {e}")
            return None
    
    def replace_selected_text(self, new_text):
        """Replace selected text with new text"""
        try:
            logger.info("🔄 Starting text replacement process...")
            
            # Save current clipboard content
            try:
                current_clipboard = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                                 capture_output=True, text=True, timeout=2).stdout
                logger.debug(f"Saved current clipboard: '{current_clipboard[:50]}...'")
            except:
                current_clipboard = ""
                logger.debug("Could not save current clipboard")
            
            # Copy new text to clipboard
            logger.info("📋 Copying new text to clipboard...")
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                     stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_text)
            
            # Verify clipboard content
            time.sleep(0.1)
            try:
                clipboard_check = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                               capture_output=True, text=True, timeout=2).stdout
                logger.info(f"✓ Clipboard now contains: '{clipboard_check[:50]}...'")
            except:
                logger.warning("Could not verify clipboard content")
            
            # Simulate Ctrl+V to paste
            logger.info("⌨️  Simulating Ctrl+V keypress...")
            time.sleep(0.2)  # Slightly longer delay
            subprocess.run(['xdotool', 'key', 'ctrl+v'], check=True, timeout=5)
            
            # Give some time for the paste to complete
            time.sleep(0.2)
            
            # Restore original clipboard (optional)
            if current_clipboard:
                try:
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                             stdin=subprocess.PIPE, text=True)
                    process.communicate(input=current_clipboard)
                    logger.debug("✓ Original clipboard restored")
                except:
                    logger.debug("Could not restore original clipboard")
            
            logger.info("✅ Text replacement process completed")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to replace text: {e}")
            return False
        except subprocess.TimeoutExpired as e:
            logger.error(f"❌ Text replacement timed out: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during text replacement: {e}")
            return False
    
    def process_trigger(self):
        """Handle the rephrase trigger - main rephrase logic"""
        # Get selected text (rephrase-specific requirement)
        selected_text = self.get_selected_text()
        if not selected_text:
            logger.info("❌ No text selected, ignoring")
            return
        
        logger.info("=" * 60)
        logger.info(f"📝 ORIGINAL TEXT:")
        logger.info(f"'{selected_text}'")
        logger.info("=" * 60)
        
        # Rephrase the text using the base service's ollama communication
        rephrased_text = self.send_to_ollama(self.get_system_prompt(), f'text to rephrase: {selected_text}')
        if not rephrased_text:
            logger.error("❌ Failed to rephrase text")
            return
        
        # Check if the LLM returned <null> (no changes needed)
        if rephrased_text.strip() == "<null>":
            logger.info("ℹ️  No changes needed - text is already well-written or the system was unable to rephrase it.")
            return
        
        logger.info("=" * 60)
        logger.info(f"✨ REPHRASED TEXT:")
        logger.info(f"'{rephrased_text}'")
        logger.info("=" * 60)
        
        # Replace the selected text (rephrase-specific action)
        success = self.replace_selected_text(rephrased_text)
        if success:
            logger.info("✅ Text replacement completed successfully!")
        else:
            logger.error("❌ Text replacement failed!")


def main():
    """Main entry point for the rephrase service"""
    try:
        service = RephraseService()
        service.run()
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Service failed: {e}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main() 