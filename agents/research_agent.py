"""
Research Agent - Core agent with multiple tools
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import SystemMessage, HumanMessage
from tools.web_search import WebSearchTool
from tools.document_processor import DocumentProcessor
from utils.memory_manager import MemoryManager

class ResearchAgent:
    def __init__(self):
        """Initialize the research agent with tools and memory"""
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            streaming=True
        )

        # Initialize tools
        self.web_search = WebSearchTool()
        self.doc_processor = DocumentProcessor()
        self.memory_manager = MemoryManager()

        # Create tools list
        self.tools = [
            self.web_search.get_tool(),
            self.doc_processor.get_tool()
        ]        

        # Create agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI Research Assistant. You have access to:
            1. Web search tool for real-time information
            2. Document analysis tool for PDF/text files
            
            Always:
            - Use appropriate tools based on the query
            - Provide detailed, well-structured responses
            - Cite sources when using web search
            - Maintain conversation context
            - Be helpful and professional
            
            Current conversation context: {chat_history}
            """),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        # Create agent
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )

        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=10,
            return_messages=True,
            memory_key="chat_history"
        )

    def process_query(self, query: str) -> str:
        """Process user query with the agent"""
        try:
            # Get conversation history
            history = self.memory.chat_memory.messages
            
            # Execute agent
            response = self.agent_executor.invoke({
                "input": query,
                "chat_history": history
            })
            
            # Save to memory
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(response["output"])
            
            return response["output"]
            
        except Exception as e:
            return f"Error processing query: {str(e)}"

    def get_conversation_history(self) -> list:
        """Get conversation history"""
        history = []
        for message in self.memory.chat_memory.messages:
            if hasattr(message, 'content'):
                role = "User" if message.type == "human" else "Assistant"
                history.append(f"{role}: {message.content}")
        return history
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()