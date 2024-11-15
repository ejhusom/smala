import yaml
from datetime import datetime, timedelta
import os

class MemoryManager:
    def __init__(self, memory_file="memories/memory.yaml", decay_threshold=2, decay_days=30):
        self.memory_file = memory_file
        self.decay_threshold = decay_threshold
        self.decay_days = decay_days
        self.memories = self.load_memories()

    def load_memories(self):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        # Load the memory file, create an empty structure if it doesn’t exist
        if not os.path.exists(self.memory_file):
            self.save_memories([])  # Initialize with an empty memory list
        
        with open(self.memory_file, "r") as file:
            data = yaml.safe_load(file) or {}
            return data.get("memories", [])

    def save_memories(self, memories=None):
        if memories is not None:
            self.memories = memories
        with open(self.memory_file, "w") as file:
            yaml.dump({"memories": self.memories}, file)

    def add_memory(self, content, category="general", priority=3):
        timestamp = datetime.now().isoformat()
        memory_prefix = "This is a memory from a conversation held on {timestamp}: "
        new_memory = {
            "content": memory_prefix + content,
            "category": category,
            "priority": priority,
            "timestamp": timestamp,
            "active": True
        }
        self.memories.append(new_memory)
        self.save_memories()

    def apply_decay(self):
        cutoff_date = datetime.now() - timedelta(days=self.decay_days)
        for memory in self.memories:
            memory_date = datetime.fromisoformat(memory["timestamp"])
            if memory["priority"] < self.decay_threshold and memory_date < cutoff_date:
                memory["active"] = False  # Mark as inactive if decayed

        self.save_memories()

    def get_active_memories(self):
        # Return only active memories for use in context
        return [m for m in self.memories if m.get("active", True)]

