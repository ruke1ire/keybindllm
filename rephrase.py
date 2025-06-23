#!/usr/bin/env python3
"""
Rephrase Service - Main entry point

Usecase: 
    - This script is to be run with systemd
    - The script first ensures that ollama is running with a model determined through some env variable
    - User presses ctrl+alt+(a number determined through REPHRASE_KEYNUM environment variable (default is 0)) when selecting a text. 
        - If text is not selected then do nothing
    - The script then sends the following to ollama
        - system prompt: Explaining that it's supposed to correct any grammatical errors, and make improvements to the writing while keeping the original tone and meaning. 
        - user prompt: The text selected by the user
    - The script then replaces the selected text with the response

This is the backwards-compatible entry point that uses the new modular structure.
"""

from rephrase_service import main

if __name__ == "__main__":
    main()