from src.voice.voice import listen, speak
from src.orchestrator.orchestrator import Orchestrator
from src.observability.setup import setup_observability
from src.observability.bus import event_bus

def main():
    setup_observability()

    event_bus.emit(
        "system_started",
        {
            "component": "sam"
        }
    )

    orch = Orchestrator()

    try:
        profile = orch.memory.get_profile()

        name = profile.get("name")

        if name:
            greeting = f"Welcome back {name}"
        else:
            greeting = "Hello I am Sam"

        event_bus.emit(
            "assistant_greeting",
            {
                "message": greeting
            }
        )

        speak(greeting)
        
        ## main loop
        while True:
            event_bus.emit(
                "voice_listening_start",
                {}
            )

            user_input = listen()

            event_bus.emit(
                "voice_listening_completed",
                {
                    "text": user_input
                }
            )

            if not user_input:
                event_bus.emit(
                    "empty_input",
                    {}
                )

            if "exit" in user_input:
                event_bus.emit(
                    "system_shutdown",
                    {}
                )
                speak("Goodbye")

                break
            
            response, action = orch.handle(
                user_input
            )

            event_bus.emit(
                "assistant_response",
                {
                    "response": response,
                    "action": action
                }
            )

            speak(response)

    except Exception as e:
        event_bus.emit(
            "system_error",
            {
                "error": str(e)
            }
        )

        raise

if __name__ == "__main__":
    main()
