import argparse
import os
import signal
import sys
import json
from llm_interface import LLMInterface
from memory_manager import MemoryManager
from utils import save_conversation_to_file, load_conversation_from_file, get_multiline_input
from datetime import datetime


def handle_exit(conversation, memory_manager, conversation_file, signal, frame):
    """Graceful exit handler to summarize and save the conversation """
    print("\nGracefully shutting down.")
    print("Summarizing conversation...")
    memory_manager.summarize_and_save(conversation, conversation_file)
    print("Conversation summary saved. Exiting...")
    sys.exit(0)


def initialize_conversation(args):
    """Initialize conversation from file or create a new conversation file path."""
    if args.conversation_file:
        conversation = load_conversation_from_file(args.conversation_file)
        conversation_file = args.conversation_file
    else:
        conversation = []
        conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        conversation_file = f"conversations/{conversation_id}.json"
        os.makedirs(os.path.dirname(conversation_file), exist_ok=True)
    return conversation, conversation_file


def process_conversation(prompt, llm, conversation, memory_manager, conversation_file):
    """Process a single conversation turn, including memory and assistant response handling."""
    # Include user input in the conversation
    conversation.append({"role": "user", "content": prompt})

    messages = [
        {"role": "system", "content": llm.system_message},
        {"role": "user", "content": memory_manager.build_memory_context()},
        {"role": "assistant", "content": "I'm aware of these memories, and will use relevant information from them when needed to assist you in the best possible way."}
    ]
    # Append conversation history
    messages.extend(conversation)

    # Send the message history to the API
    print("--------------------")
    if llm.settings.get("stream"):
        response = llm.generate_streaming_response(messages)
    else:
        response = llm.generate_response(messages)
        print(f"Assistant: {response}")

    # Append response and save conversation
    if response:
        conversation.append({"role": "assistant", "content": response})
        save_conversation_to_file(conversation, conversation_file)
    else:
        print("Assistant: Sorry, I couldn’t process that request.")
    print("====================")


def main():
    # Parse arguments and initialize conversation, LLM interface, and memory manager
    parser = argparse.ArgumentParser(description="Start a conversation with the LLM assistant.")
    parser.add_argument(
        "--conversation-file", "-f",
        type=str,
        help="Path to a previous conversation file to continue.",
        default=None
    )
    args = parser.parse_args()

    # Initialize components
    llm = LLMInterface()
    memory_manager = MemoryManager(llm=llm)
    conversation, conversation_file = initialize_conversation(args)

    # Register signal handler for graceful shutdown (Ctrl+C)
    signal.signal(signal.SIGINT, lambda signal, frame: handle_exit(conversation, memory_manager, conversation_file, signal, frame))

    print("Welcome to the Local LLM Assistant!")
    print("Type '\"\"\"' to start multi-line input mode.")
    print("Type '/remember' as part of a prompt to store a summary of it, or type only '/remember' to save a summary of the last prompt.")
    print("Type '/exit' to quit. On exit, you will be asked whether a summary of the conversation should be saved as a 'memory'.")


    while True:
        try:
            prompt = input(">>> ")

            # Multi-line mode check
            if prompt.strip().startswith('"""'):
                prompt = get_multiline_input(prompt.replace("\"\"\"", "")) 

            if prompt.lower() == "/exit":
                # Exit handling
                summary_response = input("Would you like to summarize the conversation? (y/n): ")
                if summary_response.lower() == "y":
                    print("Summarizing conversation...")
                    memory_manager.summarize_and_save(conversation, conversation_file)
                    print("Conversation summary saved. Exiting...")
                else:
                    print("Conversation not summarized. Exiting...")
                sys.exit(0)

            # Handle the /remember command
            if "/remember" in prompt:
                if prompt.strip() == "/remember":
                    # Remember the previous prompt if available
                    last_user_message = conversation[-1]["content"] if conversation else ""
                    if last_user_message:
                        memory_manager.remember(
                                    last_user_message, 
                                    category="imperative_memory",
                                    priority=llm.settings.get("priority_imperative_memories")
                        )
                else:
                    # Remember the current prompt, minus the /remember part
                    memory_content = prompt.replace("/remember", "").strip()
                    memory_manager.remember(
                                memory_content, 
                                category="imperative_memory",
                                priority=llm.settings.get("priority_imperative_memories")
                    )


            # Process the conversation turn
            process_conversation(prompt, llm, conversation, memory_manager, conversation_file)

        except EOFError:
            print("\nReceived EOF signal (Ctrl+D).")
            handle_exit(conversation, memory_manager, conversation_file, None, None)


if __name__ == "__main__":
    main()

