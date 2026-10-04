from flask import Flask, render_template, request, jsonify
from chatbot import ChatBot

app = Flask(__name__)

# Create one chatbot instance
bot = ChatBot()

# '/' means starting page /home page / main page
@app.route("/")
def home():
    return render_template("index.html") # runs html file


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    reply = bot.send(user_message)

    if reply is None:
        reply = "Error: Could not connect to Ollama."

    return jsonify({"reply": reply})


@app.route("/reset", methods=["POST"])
def reset():
    bot.reset()
    return jsonify({"message": "Conversation memory cleared."})


@app.route("/model", methods=["POST"])
def change_model():
    data = request.get_json()
    model = data.get("model", "").strip()

    if model:
        bot.model = model
        return jsonify({
            "message": f"Model changed to {model}",
            "model": model
        })

    return jsonify({"message": "Please provide a model name."})


if __name__ == "__main__":
    app.run(debug=True)