"""
Memory Management Utilities
"""

from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import BaseMessage
import json
import os

class MemoryManager:
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.memory_file = f"memory_{session_id}.json"
        self.memory = ConversationBufferWindowMemory(
            k=20,
            return_messages=True,
            memory_key="chat_history"
        )
        self.load_memory()
    
    def save_memory(self):
        """Save memory to file"""
        try:
            messages = []
            for msg in self.memory.chat_memory.messages:
                messages.append({
                    "type": msg.type,
                    "content": msg.content
                })
            
            with open(self.memory_file, 'w') as f:
                json.dump(messages, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def load_memory(self):
        """Load memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    messages = json.load(f)
                
                for msg in messages:
                    if msg["type"] == "human":
                        self.memory.chat_memory.add_user_message(msg["content"])
                    else:
                        self.memory.chat_memory.add_ai_message(msg["content"])
        except Exception as e:
            print(f"Error loading memory: {e}")
    
    def clear_memory(self):
        """Clear all memory"""
        self.memory.clear()
        if os.path.exists(self.memory_file):
            os.remove(self.memory_file)
    
    def get_memory(self):
        """Get current memory"""
        return self.memory