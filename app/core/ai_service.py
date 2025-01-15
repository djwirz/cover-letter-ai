import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain

load_dotenv()

class AIService:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found. Please set it in your environment variables.")
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=openai_api_key)
        
    async def generate_cover_letter(self, job_description: str, resume: str):
        # Create system and user prompts
        system_prompt = SystemMessagePromptTemplate.from_template("You are an expert cover letter writer.")
        user_prompt = HumanMessagePromptTemplate.from_template("""
            Job Description: {job_description}
            Resume: {resume}
            Create a professional cover letter.
        """)
        
        # Combine system and user messages into a chat prompt
        prompt = ChatPromptTemplate.from_messages([system_prompt, user_prompt])
        
        # Create a chain that links the prompt to the LLM
        chain = LLMChain(prompt=prompt, llm=self.llm)
        
        # Call the chain asynchronously with variables
        return await chain.arun({"job_description": job_description, "resume": resume})
