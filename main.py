from openai import OpenAI
client = OpenAI()

# message history, starts w/ system prompt
messages=[
    {"role": "developer", "content": "You are a commute planner for the Chicago Transit Authority. Provide optimal routes based on user queries. Be concise and informative. Do not use bus routes, only use 'L' train lines."}
  ]

# user query
print("Hello, I am your CTA assistant. How can I help you today?")

while True:
    # user query
    user_input = input("\n")

    if user_input.lower() in ['exit', 'quit']:
        break
    
    # append user message to history
    messages.append({"role": "user", "content": user_input})

    # get response from model
    completion = client.chat.completions.create(
      model="gpt-5-mini",
      messages=messages
    )

    # append model response to history
    messages.append({"role": "assistant", "content": completion.choices[0].message.content})

    # print model response
    print(completion.choices[0].message.content)