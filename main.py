from src.voice.voice import listen, speak
from src.orchestrator.orchestrator import Orchestrator


def main():
    orch = Orchestrator()

    # 👤 greeting
    profile = orch.memory.get_profile()
    name = profile.get("name")

    if name:
        speak(f"Welcome back {name}.")
    else:
        speak("Hello, I am Sam.")

    while True:
        user_input = listen()

        if not user_input:
            continue

        if "exit" in user_input:
            speak("Goodbye")
            break

        # 🧠 process
        response, action = orch.handle(user_input)

        # 🔊 speak
        speak(response)


if __name__ == "__main__":
    main()
