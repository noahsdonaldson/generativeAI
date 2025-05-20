To get this to work you need to do the following

Run Ollama in a docker container
1. Create the docker container docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
2. Download the Llama model docker compose exec -ti ollama ollama pull llama3.2
3. Download the embeddings model docker exec -it ollama ollama pull nomic-embed-text
4. Test that its working

curl http://localhost:11434/api/generate -d '{                             
  "model": "llama3.2",
  "prompt":"Why is the sky blue?"
}'

and 

curl http://localhost:11434/api/embed -d '{                                
  "model": "nomic-embed-text",
  "prompt":"Why is the sky blue?"
}'


Now proceed to the instructiosn https://weaviate.io/developers/weaviate/quickstart/local