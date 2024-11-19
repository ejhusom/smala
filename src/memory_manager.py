import os
import json
import fcntl
from datetime import datetime, timedelta
from utils import save_conversation_to_file

class MemoryManager:
    def __init__(self, memory_file="memories/memory.json", decay_threshold=2, decay_days=30, llm=None):
        self.memory_file = memory_file
        self.decay_threshold = decay_threshold
        self.decay_days = decay_days
        self.llm = llm
        self.memories = self.load_memories()

    def load_memories(self):
        """Load memories with file lock for concurrency safety."""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        memories = []

        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as file:
                fcntl.flock(file, fcntl.LOCK_SH)
                memories = json.load(file)
                fcntl.flock(file, fcntl.LOCK_UN)
        return memories

    def save_memories(self):
        """Save memories with file lock for concurrency safety."""
        with open(self.memory_file, "w") as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            json.dump(self.memories, file, indent=2)
            fcntl.flock(file, fcntl.LOCK_UN)

    def add_memory(self, content, category="general", priority=3):
        timestamp = datetime.now().isoformat()
        memory_prefix = f"This is a {category} memory with priority {priority}/5 from a conversation held on {timestamp.split('T')[0]}: "

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
            if memory["priority"] < self.decay_threshold and datetime.fromisoformat(memory["timestamp"]) < cutoff_date:
                memory["active"] = False
        self.save_memories()

    def get_active_memories(self):
        # Return only active memories for use in context
        return [m for m in self.memories if m.get("active", True)]

    def remember(self, text, category="general", priority=3):
        """Summarizes the text using the LLM and stores it as a memory."""
        # Prepare the message history for summarization
        messages = [
                {"role": "user", "content": self.llm.settings.get("system_message_how_to_remember_information_in_prompt")},
                {"role": "user", "content": text}
        ]
        # Generate the summary or relevant info from the LLM
        summary = self.llm.generate_response(
                messages, 
                system_message=self.llm.settings.get("system_message_how_to_remember_information_in_prompt")
        )

        if summary:
            self.add_memory(summary, category, priority)


    def summarize_and_save(self, conversation, conversation_file):
        """Summarize the conversation and save it to memories."""
        conversation_text = "\n".join([entry["content"] for entry in conversation])
        messages = [
                {"role": "user", "content": self.llm.settings.get("system_message_how_to_extract_relevant_info_for_memory")},
                {"role": "user", "content": conversation_text}
        ]
        summary = self.llm.generate_response(
                messages,
                system_message=self.llm.settings.get("system_message_how_to_extract_relevant_info_for_memory")
        )

        if summary:
            self.add_memory(content=summary, category="conversation_summary", priority=self.llm.settings.get("priority_conversation_summaries"))
            print("Assistant: The conversation has been summarized and saved.")

            # Add summary to conversation as well
            conversation.append({"role": "assistant", "content": summary})

            save_conversation_to_file(conversation, conversation_file)

        return summary

    def build_memory_context(self):
        """Retrieve and format active memories for conversation context."""
        active_memories = self.get_active_memories()
        memory_context = self.llm.settings.get("system_message_how_to_use_memories")
        memory_context += "\n".join([m["content"] for m in active_memories])
        return memory_context
