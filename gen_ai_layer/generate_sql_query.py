from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain.callbacks.base import BaseCallbackHandler

# Define a callback handler to stream tokens
class StreamHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token, end='', flush=True)


# Read schema from dataset.txt
with open('schema.txt', 'r') as f:
    schema_text = f.read()


template = """You are a SQL expert.

Here is the database schema:

{schema}

Here is the question:

{question}

Give me an optimized SQL query to answer the question based on the provided schema."""


# Create the prompt
prompt = ChatPromptTemplate.from_template(template)

# Load the model with streaming
model = OllamaLLM(model="sqapp", streaming=True, callbacks=[StreamHandler()])

# Create chain
chain = prompt | model


q1 = "Give me a query that displays all film titles from the release year 2006"


# Invoke the chain with both schema and procedure
response = chain.invoke({
    "schema": schema_text,
    "question": q1
})