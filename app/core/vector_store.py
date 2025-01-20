from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.models.schemas import DocumentType
from typing import List, Optional

class VectorService:
    def __init__(self, supabase_client):
        self.client = supabase_client
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
    
    async def process_document(self, content: str, doc_type: DocumentType, metadata: dict):
        try:
            # Split content into chunks
            chunks = self.text_splitter.split_text(content)
            
            # Add document type to metadata
            enhanced_metadata = {
                **metadata,
                "doc_type": doc_type,
                "chunk_count": len(chunks)
            }
            
            processed_chunks = []
            # Generate embeddings for each chunk
            for chunk in chunks:
                embedding = await self.embeddings.aembed_query(chunk)
                
                # Prepare data for insertion
                data = {
                    "content": chunk,
                    "metadata": enhanced_metadata,
                    "embedding": embedding
                }
                
                # Insert into Supabase
                result = self.client.table('documents').insert(data).execute()
                processed_chunks.append(result)
            
            return {"document_id": f"{len(processed_chunks)} chunks processed"}
            
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            raise e

    async def get_relevant_context(self, query: str, doc_type: Optional[DocumentType] = None, limit: int = 5):
        try:
            # Generate embedding for the query
            query_embedding = await self.embeddings.aembed_query(query)
            # Call the match_documents function
            result = self.client.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_count': limit
                }
            ).execute()
            
            # Format results to match expected structure
            documents = []
            for doc in result.data:
                documents.append((
                    {"page_content": doc['content'], "metadata": doc['metadata']},
                    doc['similarity']
                ))
            
            return documents
        except Exception as e:
            print(f"Error getting relevant context: {str(e)}")
            raise e