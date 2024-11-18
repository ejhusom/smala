<div align="center">
<img alt="smala" height="200px" src="assets/smala-logo.png">
</div>

# smala

A simple memory-aided language assistant.

Chat with any local language model of your choice, and let smala help you with storing essential information across conversations.

smala works with any language model used through [Ollama](https://ollama.com/), and lets you build (automatically or manually) your own archive of memories that you want the language model to use while chatting with it.

The smala tool is designed aroudn the following principles:

- **Privacy**: Designed to work with local models, enabling you to freely use personal and sensitive information without worrying about data collection.
- **Flexibility**: Use any open-weights language model that is available through Ollama, and swap between them without losing any information.
- **Control**: Customize the instructions given to the model on how to extract and use memories.

## Quickstart

You need to have [Ollama](https://ollama.com/) installed, with the language models you want to use.

Clone repository:

```
git clone https://github.com/ejhusom/smala
```

Create and activate a virtual environment (optional):

```
mkdir venv
python3 -m venv venv
source venv/bin/activate
```

Install requirements:

```
pip3 install -r requirements.txt
```

Update `config/settings.yaml` with your desired setup, most importantly which language model you want to use (make sure you have it installed through Ollama).

Run smala:

```
python3 src/smala.py
```


## About

The inspiration for smala came from the [Memory](https://openai.com/index/memory-and-new-controls-for-chatgpt/) feature of ChatGPT, where the chatbot will remember important pieces of information across your conversations.
I wanted to make something with similar functionality that is independent of what service or language model you use.
This flexibility, together with control and transparency, are the founding principles of smala.
You control your own data, using any language model you like.
smala is designed to be transparent by making it easy to control all instructions given to the language model with respect to how it extracts and uses memories.


<!-- ## Tests -->

<!-- ``` -->
<!-- pytest tests/ -->
<!-- ``` -->

