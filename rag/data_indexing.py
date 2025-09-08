# from langchain.text_splitter import CharacterTextSplitter
# from langchain.document_loaders import TextLoader
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import Pinecone
# import pinecone
# from config import config

# loader = TextLoader('C:/Users/bhavy/Langchain/Langchain_basics/Data/text_output.txt')
# documents = loader.load()
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=4)
# docs = text_splitter.split_documents(documents)

# embeddings = HuggingFaceEmbeddings()

# # Initialize Pinecone client
# pinecone.init(
#     api_key= config['PINECONE_API_KEY'],
# )

# # Define Index Name
# index_name = "placement-info-2023"
# docsearch = None

# # Checking Index
# if index_name not in pinecone.list_indexes():
#   # Create new Index
#   pinecone.create_index(name=index_name, metric="cosine", dimension=768)
#   docsearch = Pinecone.from_documents(docs, embeddings, index_name=index_name)
# else:
#   # Link to the existing index
#   docsearch = Pinecone.from_existing_index(index_name, embeddings)

import fitz  # PyMuPDF
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_text(self):
        doc = fitz.open(self.pdf_path)
        return "\n".join(page.get_text() for page in doc)
    
class TextChunker:
    def __init__(self, chunk_size=500, chunk_overlap=100):
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def chunk(self, text):
        return self.splitter.split_text(text)


class Embedder:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts):
        return self.model.encode(texts, convert_to_tensor=False)

    def embed_query(self, query):
        return self.model.encode([query])
    
class VectorStore:
    def __init__(self, embedder):
        self.embedder = embedder
        self.index = None
        self.chunks = []

    def build_index(self, chunks):
        self.chunks = chunks
        embeddings = self.embedder.embed(chunks)
        dim = embeddings[0].shape[0]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(embeddings))

    def retrieve(self, query, top_k=5):
        query_embedding = self.embedder.embed_query(query)
        D, I = self.index.search(np.array(query_embedding), k=top_k)
        return [self.chunks[i] for i in I[0]]
    
from transformers import AutoModelForSeq2SeqLM

class LLMAnswerGenerator:
    def __init__(self, model_name="google/flan-t5-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.pipeline = pipeline("text2text-generation", model=self.model, tokenizer=self.tokenizer, max_new_tokens=512)

    def generate(self, context, query):
        prompt = f"""
Answer the following question using the context provided.Rephrase this to understandable answer for user. Make your response user friendly.

Context:
{context}

Question:
{query}
"""
        result = self.pipeline(prompt)[0]["generated_text"]
        return result.strip()
