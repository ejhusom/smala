import argparse
import os
import signal
import sys
import json
from llm_interface import LLMInterface
from memory_manager import MemoryManager
from datetime import datetime


def load_conversation_from_file(file_path):
    """ Load a conversation from a JSON file """
    if not os.path.exists(file_path):
        print(f"Warning: No existing conversation found at {file_path}. Starting a new conversation.")
        return []

    with open(file_path, "r") as file:
        conversation = json.load(file)
    return conversation


def save_conversation_to_file(conversation, file_path):
    """ Save the conversation to a JSON file """
    with open(file_path, "w") as file:
        json.dump(conversation, file, indent=2)


def summarize_and_save(conversation, memory_manager, conversation_file):
    """ Summarize the conversation and save it to memories """
    llm = LLMInterface()
    conversation_text = "\n".join([entry["content"] for entry in conversation])
    summary = llm.generate_response([prompt2json(f"Summarize the following conversation:\n{conversation_text}")])

    if summary:
        memory_manager.add_memory(content=summary, category="conversation_summary", priority=5)
        print("Assistant: The conversation has been summarized and saved.")

        # Add summary to conversation as well
        conversation.append(prompt2json(summary, role="assistant"))

        save_conversation_to_file(conversation, conversation_file)

    return summary


def handle_exit(conversation, memory_manager, conversation_file, signal, frame):
    """ Graceful exit handler to summarize and save the conversation """
    print("\nGracefully shutting down.")
    print("Summarizing conversation...")
    summarize_and_save(conversation, memory_manager, conversation_file)
    print("Conversation summary saved. Exiting...")
    sys.exit(0)


def prompt2json(prompt, role="user"):
    """Convert a prompt string to a JSON object"""
    return {"role": role, "content": prompt}


def get_multiline_input(line=""):
    """Allow multi-line input using triple quotes to start and end."""
    lines = [line]
    while True:
        line = input(">>> ")
        if line.strip() == '"""':  # End multi-line input if '"""' is typed
            break
        lines.append(line)
    return "\n".join(lines)  # Combine all lines into a single string


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
        conversation_file = f"conversations/{conversation_id}.json"
        os.makedirs(os.path.dirname(conversation_file), exist_ok=True)

    # Register signal handler for graceful shutdown (Ctrl+C or exit command)
    signal.signal(signal.SIGINT, lambda signal, frame: handle_exit(conversation, memory_manager, conversation_file, signal, frame))

    print("Welcome to the Local LLM Assistant!")
    print("Type '\"\"\"' to start multi-line input mode. Type '/exit' to exit.")

    try:
        while True:
            prompt = input(">>> ")

            # Check if the user wants to start multi-line mode
            if prompt.strip().startswith('"""'):
                prompt = get_multiline_input(prompt.replace("\"\"\"", ""))  # Switch to multi-line input mode

            if prompt.lower() == "/exit":
                # Ask the user if they want to summarize the conversation
                summary_response = input("Would you like to summarize the conversation? (y/n): ")
                if summary_response.lower() == "y":
                    print("Summarizing conversation...")
                    summarize_and_save(conversation, memory_manager, conversation_file)
                    print("Conversation summary saved. Exiting...")
                else:
                    print("Conversation not summarized. Exiting...")
                sys.exit(0)

            # Include user input in the conversation
            conversation.append({"role": "user", "content": prompt})

            messages = [{"role": "system", "content": llm.system_message}]

            # Include active memories in the prompt context
            active_memories = memory_manager.get_active_memories()
            memory_context = "Here are some memories from previous conversations (use these to be as helpful as possible when relevant):\n"
            memory_context += "\n".join([m["content"] for m in active_memories])
            messages.append({"role": "system", "content": memory_context})

            # Append the entire conversation history (including user's and assistant's messages)
            messages.extend(conversation)

            # Send the entire message history (system + conversation) to the API
            response = llm.generate_response(messages)

            # Get the response based on the full message history
            if response:
                print("----------")
                print(f"Assistant: {response}")
                print("==========")
                conversation.append({"role": "assistant", "content": response})

                # Optionally store the conversation in the file as we go
                save_conversation_to_file(conversation, conversation_file)
            else:
                print("Assistant: Sorry, I couldn’t process that request.")

    except KeyboardInterrupt:
        # Handle unexpected shutdown (Ctrl+C)
        print("\nProgram interrupted.")
        handle_exit(conversation, memory_manager, conversation_file, None, None)

if __name__ == "__main__":
    main()

