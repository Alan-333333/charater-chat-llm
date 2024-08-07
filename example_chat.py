import argparse
from chat import chat
from backend_localai import backend_localai

def setup_backend(url, model):
    backend = backend_localai(url, model)
    backend.max_length = 1000
    return backend

def setup_chat(backend):
    return chat(backend)

def download_character(chat_instance, char_url):
    if 'Miku' not in chat_instance.char.list():
        chat_instance.char.download(char_url)
    chat_instance.char.load('Miku')

def on_stream(text, final, offset):
    print(text[offset:], end='\n' if final else '', flush=True)

def main():
    parser = argparse.ArgumentParser(description="Chat with Miku AI")
    parser.add_argument("--url", default="http://localhost:8080", help="Backend URL")
    parser.add_argument("--model", default="l3-8b-stheno-v3.2-iq-imatrix", help="Model name")
    parser.add_argument("--stream", action="store_true", help="Enable streaming output")
    args = parser.parse_args()

    backend = setup_backend(args.url, args.model)
    chat_instance = setup_chat(backend)
    download_character(chat_instance, 'https://chub.ai/characters/pitanon/miku-d1b931c6')

    greeting = chat_instance.start()
    if greeting:
        print(f"{chat_instance.char.name}: {greeting}")

    while True:
        prompt = input(f"{chat_instance.user.name}: ")
        if args.stream:
            print(f"{chat_instance.char.name}: ", end='')
            chat_instance.say(prompt, on_stream)
        else:
            print(f"{chat_instance.char.name}: {chat_instance.say(prompt)}")

if __name__ == "__main__":
    main()