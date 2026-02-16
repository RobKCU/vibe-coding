from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-5.2",
    input="Give me a one-sentence noir detective greeting.",
)

print(resp.output_text)
