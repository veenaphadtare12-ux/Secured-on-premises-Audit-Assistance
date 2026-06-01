from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
import time


print("Initializing connection to local Llama 3...")
llm = ChatOllama(model="llama3", temperature=0)


messages = [
    HumanMessage(content="write a code for trie in c"),
]

print("Thinking...\n")
print("-" * 40)


start_time = time.time()

for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)

end_time = time.time()

print("\n" + "-" * 40)
print(f"Inference Complete! Time taken: {end_time - start_time:.2f} seconds.")