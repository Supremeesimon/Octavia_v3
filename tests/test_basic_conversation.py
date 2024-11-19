"""
Basic test for Octavia's conversation system
"""

import asyncio
import os
from pathlib import Path
from src.consciousness.interface.conversation_handler import ConversationHandler

async def main():
    # Create a test conversation handler
    handler = ConversationHandler()
    
    # Test basic conversation
    messages = [
        "Hello, I'm Simon",
        "What can you help me with?",
        "Tell me about yourself"
    ]
    
    print("\n🧪 Testing Basic Conversation Flow\n")
    
    for message in messages:
        print(f"User: {message}")
        response = await handler.process_message(message)
        print(f"Octavia: {response}\n")
        await asyncio.sleep(1)  # Small delay between messages
    
    print("✅ Basic conversation test complete!")

if __name__ == "__main__":
    asyncio.run(main())
