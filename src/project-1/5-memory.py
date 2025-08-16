from openai import OpenAI

client = OpenAI()


def run_chat(user_inputs, preserve_memory=True):
    print(f"\n=== Chat Simulation (memory = {preserve_memory}) ===\n")
    messages = []

    for user_input in user_inputs:
        # Build user message
        user_msg = {"role": "user", "content": user_input}
        if preserve_memory:
            messages.append(user_msg)

        # Ask the model
        resp = client.responses.create(
            model="gpt-5", input=[user_msg] if not preserve_memory else messages
        )
        reply = resp.output_text

        # Print turn
        print("You:", user_input)
        print("Assistant:", reply, "\n")

        if preserve_memory:
            messages.append({"role": "assistant", "content": reply})


# Demo conversation
user_inputs = ["My name is Alice.", "What is my name?"]

# run_chat(user_inputs, preserve_memory=False)  # no memory
# run_chat(user_inputs, preserve_memory=True)  # with memory
