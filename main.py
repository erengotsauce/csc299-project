from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-5-mini",
  messages=[
    {"role": "developer", "content": "You are a commute planner for the Chicago Transit Authority. Provide optimal routes based on user queries. Be concise and informative. Do not use bus routes, only use 'L' train lines."},
    {"role": "user", "content": "How do I get from Millennium Station to O'Hare Airport using the 'L' train lines?"}
  ]
)

print(completion.choices[0].message)