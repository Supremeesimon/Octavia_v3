"""
Interactive CLI for testing Octavia's conversation system
"""

import asyncio
import sys
import os
from pathlib import Path

# Ensure src directory is in Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.consciousness.interface.conversation_handler import ConversationHandler

async def interactive_chat(api_key):
    # Create conversation handler with provided API key
    handler = ConversationHandler(api_key=api_key)
    
    print("🤖 Octavia Interactive Chat Test")
    print("Type 'exit' to end the conversation\n")
    
    try:
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            # Exit condition
            if user_input.lower() == 'exit':
                print("\n👋 Ending conversation.")
                break
            
            # Process message
            response = await handler.process_message(user_input)
            print(f"Octavia: {response}\n")
    
    except KeyboardInterrupt:
        print("\n\n👋 Chat interrupted. Goodbye!")

if __name__ == "__main__":
    # Prompt for API key if not provided
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        api_key = input("Please enter your Gemini API Key: ").strip()
    
    # Run the async chat function
    asyncio.run(interactive_chat(api_key))
