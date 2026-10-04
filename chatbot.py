import json
import os
import requests
from datetime import datetime


OLLAMA_URL = "http://localhost:11434/api/chat"  # main link of Ai model
DEFAULT_MODEL = "qwen2.5:1.5b"                   # name of the model
HISTORY_DIR = "chat_sessions"
MAX_CONTEXT_MESSAGES = 20                        # max no. of messages to be stored at a time

DEFAULT_PERSONA = (
    "You are a sharp, no-nonsense assistant. "
    "Be direct, concise, and useful. "
    "Don't pad answers with fluff. "
    "If you don't know something, say so."
)  # Personality of AI


class ChatBot:

    def __init__(self, model=DEFAULT_MODEL, persona=DEFAULT_PERSONA):
        self.model = model
        self.persona = persona
        self.history = [{"role": "system", "content": persona}]
        os.makedirs(HISTORY_DIR, exist_ok=True)

    def _trim_context(self):
        system_msg = self.history[0]
        convo = self.history[1:]
        if len(convo) > MAX_CONTEXT_MESSAGES:
            convo = convo[-MAX_CONTEXT_MESSAGES:]
        self.history = [system_msg] + convo

    def set_persona(self, persona):
        self.persona = persona
        self.history[0] = {"role": "system", "content": persona}

    def reset(self):
        self.history = [{"role": "system", "content": self.persona}]

    def send(self, user_input):
        """Send a message to the local Ollama model."""
        self.history.append({"role": "user", "content": user_input})
        self._trim_context()

        payload = {
            "model": self.model,
            "messages": self.history,
            "stream": True,
        }

        full_reply = ""

        try:
            with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=60) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    full_reply += token
                    if chunk.get("done"):
                        break

        except requests.exceptions.ConnectionError:
            self.history.pop()
            return "⚠️ Can't connect to Ollama. Please make sure Ollama is running."

        except requests.exceptions.HTTPError:
            self.history.pop()
            return f"⚠️ Could not use model '{self.model}'. Make sure it has been downloaded."

        self.history.append({"role": "assistant", "content": full_reply})
        return full_reply

    def save(self, name=None):
        name = name or datetime.now().strftime("session_%Y%m%d_%H%M%S")
        path = os.path.join(HISTORY_DIR, f"{name}.json")
        with open(path, "w") as f:
            json.dump(self.history, f, indent=2)
        return path

    def load(self, name):
        path = os.path.join(HISTORY_DIR, f"{name}.json")
        with open(path) as f:
            self.history = json.load(f)
        self.persona = self.history[0]["content"]