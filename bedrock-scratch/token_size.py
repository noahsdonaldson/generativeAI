import matplotlib.pyplot as plt
import tiktoken
from bs4 import BeautifulSoup as Soup
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


# LCEL docs
url = "https://python.langchain.com/docs/expression_language/"
loader = RecursiveUrlLoader(
    url=url, max_depth=20, extractor=lambda x: Soup(x, "html.parser").text
)
docs = loader.load()

# Doc texts
# docs.extend([*docs_pydantic, *docs_sq])
docs_texts = [d.page_content for d in docs]

# Calculate the number of tokens for each document
counts = [num_tokens_from_string(d, "cl100k_base") for d in docs_texts]

# # Plotting the histogram of token counts
# plt.figure(figsize=(10, 6))
# plt.hist(counts, bins=30, color="blue", edgecolor="black", alpha=0.7)
# plt.title("Histogram of Token Counts")
# plt.xlabel("Token Count")
# plt.ylabel("Frequency")
# plt.grid(axis="y", alpha=0.75)

# # Display the histogram
# plt.show()

print(type(docs))