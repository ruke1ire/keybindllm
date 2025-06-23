#!/usr/bin/env python3
"""
Base service for AI-powered text processing services.
Handles keyboard shortcuts, ollama communication, and service infrastructure.
"""

import os
import sys
import time
import subprocess
import requests
import json
import threading
import logging
from abc import ABC, abstractmethod
from pynput import keyboard
from pynput.keyboard import Key, Listener

# Configure logging
log_level = logging.DEBUG if os.getenv('DEBUG') else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaseAIService(ABC):
    """Base class for AI-powered text processing services"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'gemma3')
        self.keynum = int(os.getenv('REPHRASE_KEYNUM', '0'))  # TODO: Make this more generic
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        
        # Track pressed keys for combination detection
        self.pressed_keys = set()
        
        logger.info(f"Initializing {service_name} service")
        logger.info(f"Model: {self.ollama_model}")
        logger.info(f"Shortcut: Ctrl+Alt+{self.keynum}")
    
    def ensure_ollama_running(self):
        """Ensure ollama service is running and model is loaded"""
        # Step 1: Check if ollama service is responding
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✓ Ollama service is running")
            else:
                logger.error("✗ Ollama service not responding")
                return False
        except requests.exceptions.RequestException:
            logger.info("Ollama not responding, attempting to start...")
            
            try:
                # Try to start ollama service
                subprocess.run(['systemctl', '--user', 'start', 'ollama'], check=True)
                time.sleep(3)  # Give it time to start
                
                # Verify it's running
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
                if response.status_code != 200:
                    logger.error("Failed to start Ollama service")
                    return False
                logger.info("✓ Ollama service started successfully")
            except (subprocess.CalledProcessError, requests.exceptions.RequestException) as e:
                logger.error(f"✗ Failed to start ollama: {e}")
                return False
        
        # Step 2: Check if the specific model is available
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            models_data = response.json()
            available_models = [model['name'].split(':')[0] for model in models_data.get('models', [])]
            
            logger.info(f"Available models: {available_models}")
            
            if self.ollama_model not in available_models:
                logger.warning(f"⚠️  Model '{self.ollama_model}' not found in available models")
                logger.info(f"Attempting to pull model '{self.ollama_model}'...")
                
                # Try to pull the model
                pull_response = requests.post(f"{self.ollama_url}/api/pull", 
                                            json={"name": self.ollama_model}, 
                                            timeout=300)  # 5 minutes timeout for model download
                
                if pull_response.status_code == 200:
                    logger.info(f"✓ Model '{self.ollama_model}' pulled successfully")
                else:
                    logger.error(f"✗ Failed to pull model '{self.ollama_model}': {pull_response.text}")
                    return False
            else:
                logger.info(f"✓ Model '{self.ollama_model}' is available")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to check/pull model: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Unexpected error checking model: {e}")
            return False
        
        # Step 3: Test the model with a simple request
        try:
            logger.info(f"Testing model '{self.ollama_model}' with a simple request...")
            test_payload = {
                "model": self.ollama_model,
                "messages": [{"role": "user", "content": "test"}],
                "stream": False
            }
            
            test_response = requests.post(f"{self.ollama_url}/api/chat", 
                                        json=test_payload, timeout=30)
            
            if test_response.status_code == 200:
                logger.info(f"✅ Model '{self.ollama_model}' is loaded and responding")
                return True
            else:
                logger.error(f"✗ Model test failed: {test_response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Model test failed: {e}")
            return False
    
    def send_to_ollama(self, system_prompt: str, user_input: str) -> str:
        """Send text to ollama for processing"""
        try:
            logger.info(f"🤖 Sending text to {self.ollama_model} for processing...")
            logger.debug(f"Input text length: {len(user_input)} characters")
            
            payload = {
                "model": self.ollama_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "stream": False
            }
            
            response = requests.post(f"{self.ollama_url}/api/chat", 
                                   json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            processed_text = result['message']['content'].strip()
            
            logger.info(f"✅ Text processed successfully (length: {len(processed_text)} characters)")
            logger.debug(f"Model response: {result}")
            return processed_text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to process text: {e}")
            return None
        except KeyError as e:
            logger.error(f"❌ Unexpected response format from Ollama: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error during processing: {e}")
            return None
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this service"""
        pass
    
    @abstractmethod
    def process_trigger(self):
        """Handle the service-specific processing when shortcut is triggered"""
        pass
    
    def handle_shortcut(self):
        """Handle the keyboard shortcut trigger - calls service-specific processing"""
        logger.info(f"🚀 {self.service_name} shortcut detected, processing...")
        
        try:
            self.process_trigger()
        except Exception as e:
            logger.error(f"❌ Error in {self.service_name} processing: {e}")
    
    def on_press(self, key):
        """Handle key press events"""
        try:
            self.pressed_keys.add(key)
            
            # Debug logging
            logger.debug(f"Key pressed: {key}")
            logger.debug(f"Currently pressed keys: {self.pressed_keys}")
            
            # Check for Ctrl+Alt+[number] combination
            ctrl_pressed = Key.ctrl_l in self.pressed_keys or Key.ctrl_r in self.pressed_keys
            alt_pressed = Key.alt_l in self.pressed_keys or Key.alt_r in self.pressed_keys
            
            # Debug the modifier keys
            if ctrl_pressed or alt_pressed:
                logger.info(f"Modifiers detected - Ctrl: {ctrl_pressed}, Alt: {alt_pressed}")
            
            if ctrl_pressed and alt_pressed:
                logger.info(f"Ctrl+Alt detected! Checking for number key...")
                try:
                    # Check if the pressed key is our target number
                    if hasattr(key, 'char') and key.char is not None:
                        logger.info(f"Character key pressed: '{key.char}', target: '{self.keynum}'")
                        if key.char == str(self.keynum):
                            logger.info(f"🎯 SHORTCUT TRIGGERED: Ctrl+Alt+{self.keynum}")
                            # Run in separate thread to avoid blocking the listener
                            threading.Thread(target=self.handle_shortcut, daemon=True).start()
                    else:
                        logger.debug(f"Non-character key: {key}")
                except AttributeError as e:
                    logger.debug(f"Key attribute error: {e}")
        except Exception as e:
            logger.error(f"Error in on_press: {e}")
    
    def on_release(self, key):
        """Handle key release events"""
        try:
            self.pressed_keys.discard(key)
        except KeyError:
            pass
    
    def run(self):
        """Main service loop"""
        logger.info(f"Starting {self.service_name} service with model: {self.ollama_model}")
        logger.info(f"Listening for Ctrl+Alt+{self.keynum}")
        
        # Ensure ollama is running
        if not self.ensure_ollama_running():
            logger.error("Failed to ensure ollama is running")
            sys.exit(1)
        
        # Start keyboard listener
        try:
            listener = Listener(
                on_press=self.on_press, 
                on_release=self.on_release,
                suppress=False  # Don't suppress keys, just listen
            )
            listener.start()
            logger.info("Keyboard listener started. Press Ctrl+Alt+{} to trigger {}.".format(self.keynum, self.service_name))
            logger.info("Set DEBUG=1 environment variable for detailed key logging")
            
            # Keep the main thread alive
            try:
                while listener.running:
                    listener.join(timeout=1.0)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                listener.stop()
                
        except Exception as e:
            logger.error(f"Keyboard listener failed: {e}")
            logger.error("This might be a permissions issue. Try running with sudo or check X11 access.")
            raise


def main():
    """Main entry point for testing the base service"""
    logger.error("BaseAIService is an abstract class and cannot be run directly.")
    logger.info("Please run a specific service implementation (e.g., rephrase.py)")
    sys.exit(1)


if __name__ == "__main__":
    main() 