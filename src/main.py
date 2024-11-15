from llm_interface import LLMInterface
from memory_manager import MemoryManager

def main():
    llm = LLMInterface()
    memory_manager = MemoryManager()
    
    # Apply decay to memories on start
    memory_manager.apply_decay()

    print("Welcome to the Local LLM Assistant!")

    while True:
        prompt = input("\nYou: ")

        if prompt.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Include active memories in the prompt context
        active_memories = memory_manager.get_active_memories()
        memory_context = "\n".join([m["content"] for m in active_memories])
        full_prompt = f"{memory_context}\n{prompt}"

        response = llm.generate_response(full_prompt)

        if response:
            print(f"Assistant: {response}")
            # Save the interaction as a new memory
            memory_manager.add_memory(content=response, category="conversation", priority=3)
        else:
            print("Assistant: Sorry, I couldn’t process that request.")

if __name__ == "__main__":
    main()
