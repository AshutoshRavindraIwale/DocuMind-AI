"""
Document Processing Tool with RAG capabilities
"""

from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from typing import Optional, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DocumentProcessor(BaseTool):
    name: str = "document_analysis"
    description: str = "Analyze and answer questions about uploaded documents (PDF, TXT)"
    embeddings: Optional[Any] = None
    documents_dir: Optional[str] = None
    documents_path: Optional[str] = None
    vectorstore: Optional[Any] = None
    qa_chain: Optional[Any] = None
    llm: Optional[Any] = None
    
    def __init__(self):
        super().__init__()
        self.embeddings = OpenAIEmbeddings()
        self.documents_path = "data/documents"
        self.documents_dir = self.documents_path  # For compatibility
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.vectorstore = None
        self.qa_chain = None
        
        # Create documents directory if it doesn't exist
        os.makedirs(self.documents_path, exist_ok=True)
        
        # Process any existing documents on initialization
        self._process_existing_documents()
    
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Run the document processor"""
        print(f"DocumentProcessor received query: '{query}'")
        
        # Check if vectorstore exists first
        if self.vectorstore is None:
            print("Vectorstore is None, attempting to process existing documents")
            # Try to process any existing documents if not already done
            self._process_existing_documents()
        
        # Process all documents in directory
        if "process all documents" in query.lower():
            print("Processing all documents in directory")
            if not os.path.exists(self.documents_path):
                return "No documents directory found."
            
            files = os.listdir(self.documents_path)
            if not files:
                return "No documents found in the documents directory."
            
            processed = []
            for file in files:
                file_path = os.path.join(self.documents_path, file)
                if file.lower().endswith('.pdf') or file.lower().endswith('.txt'):
                    try:
                        self._process_document(file_path)
                        processed.append(file)
                    except Exception as e:
                        print(f"Error processing {file}: {str(e)}")
                        continue
            
            if processed:
                return f"Successfully processed {len(processed)} documents: {', '.join(processed)}"
            else:
                return "No documents were processed successfully."
        
        # Process single document (only if it contains a file path)
        elif ("upload" in query.lower() or "process" in query.lower()) and ":" in query:
            print("Processing single document")
            # Extract file path from query
            file_path = query.split(":")[-1].strip()
            if not file_path:
                return "Please provide a file path."
            
            try:
                return self._process_document(file_path)
            except Exception as e:
                return f"Error processing document: {str(e)}"
        else:
            # Handle QA
            print("Handling QA query")
            if not self.vectorstore:
                print("No vectorstore available for QA")
                return "No documents have been processed yet. Please upload a document first."
            
            try:
                print(f"Querying vectorstore with: {query}")
                result = self.qa_chain.invoke({"query": query})["result"]
                print(f"Got result: {result[:100]}...")
                return result
            except Exception as e:
                print(f"Error in QA: {str(e)}")
                import traceback
                print(traceback.format_exc())
                return f"Error answering question: {str(e)}"
    
    def _handle_upload_request(self, query: str) -> str:
        """Handle document upload requests"""
        # In a real implementation, this would handle file uploads
        # For demo purposes, we'll look for files in the documents directory
        try:
            files = os.listdir(self.documents_path)
            if not files:
                return "No documents found in the documents directory. Please add some files to data/documents/"
            
            # Process all documents in the directory
            all_documents = []
            for file in files:
                file_path = os.path.join(self.documents_path, file)
                if file.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                elif file.endswith('.txt'):
                    loader = TextLoader(file_path)
                else:
                    continue
                
                documents = loader.load()
                all_documents.extend(documents)
            
            if not all_documents:
                return "No valid documents found (PDF or TXT files only)."
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(all_documents)
            
            # Create vectorstore
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            
            return f"Successfully processed {len(all_documents)} documents with {len(splits)} text chunks. You can now ask questions about the content."
            
        except Exception as e:
            return f"Error uploading documents: {str(e)}"
    
    def process_all_documents(self):
        """Process all documents in the documents directory"""
        if not os.path.exists(self.documents_path):
            return "No documents directory found."
        
        files = os.listdir(self.documents_path)
        if not files:
            return "No documents found in the documents directory."
        
        processed = []
        for file in files:
            file_path = os.path.join(self.documents_path, file)
            if file.lower().endswith('.pdf') or file.lower().endswith('.txt'):
                try:
                    self._process_document(file_path)
                    processed.append(file)
                except Exception as e:
                    continue
        
        if processed:
            return f"Successfully processed {len(processed)} documents: {', '.join(processed)}"
        else:
            return "No documents were processed successfully."
    
    def _process_document(self, file_path):
        """Process a single document file"""
        try:
            print(f"Starting to process document: {file_path}")
            
            # Load document based on file type
            if file_path.lower().endswith('.pdf'):
                print(f"Loading PDF file: {file_path}")
                loader = PyPDFLoader(file_path)
            elif file_path.lower().endswith('.txt'):
                print(f"Loading text file: {file_path}")
                loader = TextLoader(file_path)
            else:
                print(f"Unsupported file type: {file_path}")
                return f"Unsupported file type: {file_path}"
            
            # Load the document
            print("Loading document content...")
            documents = loader.load()
            print(f"Loaded {len(documents)} document(s)")
            if not documents:
                print("No content found in document")
                return f"No content found in {file_path}"
            
            # Split text into chunks
            print("Splitting text into chunks...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            print(f"Created {len(splits)} text chunks")
            
            # Create or update vectorstore
            print("Creating/updating vectorstore...")
            if self.vectorstore:
                print("Adding documents to existing vectorstore")
                self.vectorstore.add_documents(splits)
            else:
                print("Creating new vectorstore with embeddings")
                self.embeddings = OpenAIEmbeddings()
                self.vectorstore = Chroma.from_documents(
                    documents=splits,
                    embedding=self.embeddings
                )
            print("Vectorstore updated successfully")
            
            # Create QA chain if it doesn't exist
            if not self.qa_chain:
                print("Creating QA chain...")
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                    return_source_documents=True
                )
                print("QA chain created successfully")
            
            print(f"Document processing complete: {os.path.basename(file_path)}")
            return f"Successfully processed {os.path.basename(file_path)} with {len(splits)} text chunks."
            
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return f"Error processing document {os.path.basename(file_path)}: {str(e)}"
    
    def _process_existing_documents(self):
        """Process any existing documents in the documents directory on initialization"""
        print(f"Checking for documents in {self.documents_path}")
        if not os.path.exists(self.documents_path):
            print(f"Directory {self.documents_path} does not exist")
            return
        
        files = os.listdir(self.documents_path)
        print(f"Found {len(files)} files in directory: {files}")
        if not files:
            print("No files found in directory")
            return
        
        for file in files:
            file_path = os.path.join(self.documents_path, file)
            print(f"Checking file: {file_path}")
            if file.lower().endswith('.pdf') or file.lower().endswith('.txt'):
                try:
                    print(f"Processing document: {file}")
                    result = self._process_document(file_path)
                    print(f"Result: {result}")
                except Exception as e:
                    print(f"Error processing document {file}: {str(e)}")
            else:
                print(f"Skipping file with unsupported extension: {file}")
    
    def get_tool(self):
        """Get the tool for agent use"""
        return self