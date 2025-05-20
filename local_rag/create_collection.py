import weaviate
from weaviate.classes.config import Configure



client = weaviate.connect_to_local()

# First delete the collection if it already exists to avoid issues
try:
    client.collections.delete("Question")
    print("Deleted existing Question collection")
except:
    print("No existing Question collection found")

questions = client.collections.create(
    name="Question",
    vectorizer_config=Configure.Vectorizer.text2vec_ollama(
        # For macOS/Windows with Weaviate in Docker and Ollama on host:
        api_endpoint="http://host.docker.internal:11434",
        # For Linux with Weaviate in Docker and Ollama on host:
        # api_endpoint="http://<your-host-ip>:11434",
        model="nomic-embed-text",
    ),
    generative_config=Configure.Generative.ollama(
        # Same as above
        api_endpoint="http://host.docker.internal:11434",
        # For Linux with Weaviate in Docker and Ollama on host:
        # api_endpoint="http://<your-host-ip>:11434",
        model="llama3.2",
    )
)

# Print confirmation
print(f"Created collection: {questions.name}")

client.close()