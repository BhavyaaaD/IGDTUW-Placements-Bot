# from langchain.llms import HuggingFaceHub
# from langchain import PromptTemplate
# from prompt import rag_template as template
# from langchain.schema.runnable import RunnablePassthrough
# from langchain.schema.output_parser import StrOutputParser
# from config import config

# from langchain.text_splitter import CharacterTextSplitter
# from langchain.document_loaders import TextLoader
# from langchain.embeddings import HuggingFaceEmbeddings
# from pinecone import ServerlessSpec, Pinecone

# loader = TextLoader('C:/Users/bhavy/Langchain/Langchain_basics/Data/text_output.txt', encoding = 'UTF-8')
# documents = loader.load()
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=4)
# docs = text_splitter.split_documents(documents)

# embeddings = HuggingFaceEmbeddings()

# # Initialize Pinecone client
# pc = Pinecone( api_key= config['pinecone_api_key'] ) 

# # Define Index Name
# index_name = "placement-info-2023"
# docsearch = None

# # Checking Index
# if index_name not in pc.list_indexes():
#   # Create new Index
#   pc.create_index(name=index_name, metric="cosine", dimension=768)
#   docsearch = Pinecone.from_documents(docs, embeddings, index_name=index_name)
# else:
#   # Link to the existing index
#   docsearch = Pinecone.from_existing_index(index_name, embeddings)

# # Define the repo ID and connect to Mixtral model on Huggingface
# repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
# llm = HuggingFaceHub(
#   repo_id=repo_id, 
#   model_kwargs={"temperature": 0.8, "top_k": 50}, 
#   huggingfacehub_api_token=config['HF_TOKEN']
# )

# prompt = PromptTemplate(
#   template=template, 
#   input_variables=["context", "question"]
# )

# rag_chain = (
#   {"context": docsearch.as_retriever(),  "question": RunnablePassthrough()} 
#   | prompt 
#   | llm
#   | StrOutputParser() 
# )

from rag.data_indexing import PDFProcessor,TextChunker,Embedder,VectorStore, LLMAnswerGenerator

class PlacementQA:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf_processor = PDFProcessor(self.pdf_path)
        self.chunker = TextChunker()
        self.embedder = Embedder()
        self.vector_store = VectorStore(self.embedder)
        self.llm_generator = LLMAnswerGenerator()


    def run(self):
        print("Extracting text from PDF...")
        text = self.pdf_processor.extract_text()
        print("Chunking text...")
        chunks = self.chunker.chunk(text)
        print(f"Total chunks: {len(chunks)}")
        print("Building FAISS index...")
        self.vector_store.build_index(chunks)
        print("Retrieving relevant chunks...")
        relevant_chunks = self.vector_store.retrieve(self.query)
        context = "\n\n".join(relevant_chunks)
        print("Generating answer...")
        answer = self.llm_generator.generate(context, self.query)
        return answer
    
    def generate_response(self, query):
        self.query = query

        response = self.run()
        return response

