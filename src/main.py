import argparse
import os
import signal
import sys
from llm_interface import LLMInterface
from memory_manager import MemoryManager
from datetime import datetime


def load_conversation_from_file(file_path):
    """ Load a conversation from a file """
    if not os.path.exists(file_path):
        print(f"Warning: No existing conversation found at {file_path}. Starting a new conversation.")
        return []

    conversation = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            role, content = line.split(":", 1)
            conversation.append({"role": role.strip(), "content": content.strip()})
    return conversation


def save_conversation_to_file(conversation, file_path):
    """ Save the conversation to a text file """
    with open(file_path, "w") as file:
        for entry in conversation:
            file.write(f"{entry['role']}: {entry['content']}\n")


def summarize_and_save(conversation, memory_manager):
    """ Summarize the conversation and save it to memories """
    llm = LLMInterface()
    conversation_text = "\n".join([entry["content"] for entry in conversation])
    summary = llm.generate_response(f"Summarize the following conversation:\n{conversation_text}")

    if summary:
        memory_manager.add_memory(content=summary, category="conversation_summary", priority=5)
        print("Assistant: The conversation has been summarized and saved.")

    return summary


def handle_exit(signal, frame):
    """ Graceful exit handler to summarize and save the conversation """
    print("\nGracefully shutting down. Summarizing conversation...")
    summarize_and_save(conversation, memory_manager)
    save_conversation_to_file(conversation, conversation_file)
    sys.exit(0)


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Start a conversation with the LLM assistant.")
    parser.add_argument(
        "--conversation-file",
        "-f",
        type=str,
        help="Path to a previous conversation file to continue.",
        default=None
    )
    args = parser.parse_args()

    # Set up the memory manager and LLM interface
    llm = LLMInterface()
    memory_manager = MemoryManager()

    # Load conversation history if a file is provided
    if args.conversation_file:
        conversation = load_conversation_from_file(args.conversation_file)
        conversation_file = args.conversation_file
    else:
        conversation = []
        conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        conversation_file = f"conversations/{conversation_id}.txt"
        os.makedirs(os.path.dirname(conversation_file), exist_ok=True)

    # Register signal handler for graceful shutdown (Ctrl+C or exit command)
    signal.signal(signal.SIGINT, handle_exit)

    print("Welcome to the Local LLM Assistant!")

    first_prompt = True  # Flag to track if it's the first prompt of the conversation

    try:
        while True:
            prompt = input("\nYou: ")

            if prompt.lower() == "exit":
                print("Goodbye!")
                break

            # Save the user message as part of the conversation
            conversation.append({"role": "user", "content": prompt})

            # Add system message as the first message in the history
            message_history = [{"role": "system", "content": llm.system_message}] 

            if first_prompt:
                # Include active memories in the prompt context
                active_memories = memory_manager.get_active_memories()
                memory_context = "\n".join([m["content"] for m in active_memories])
                message_history.append({"role": "system", "content": memory_context})
                first_prompt = False  # Mark first prompt as processed

            message_history.extend(conversation)

            # Get the response based on the full message history
            response = llm.generate_response(message_history)

            if response:
                print(f"Assistant: {response}")
                conversation.append({"role": "assistant", "content": response})

                # Optionally store the conversation in the file as we go
                save_conversation_to_file(conversation, conversation_file)
            else:
                print("Assistant: Sorry, I couldn’t process that request.")

    except KeyboardInterrupt:
        # Handle unexpected shutdown (Ctrl+C)
        print("\nProgram interrupted, summarizing conversation...")
        summarize_and_save(conversation, memory_manager)
        save_conversation_to_file(conversation, conversation_file)
        print("Conversation summary saved. Exiting...")

if __name__ == "__main__":
    main()

