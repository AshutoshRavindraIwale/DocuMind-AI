#!/usr/bin/env python3

import os
import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.spinner import spinner
from rich.live import live
from agents.research_agent import ResearchAgent

#Load environment variables

load_dotenv()

console = Console()

class DocuMindAI:
    def __init__(self):
        """Initialize the DocuMindAI instance."""
        self.agent = ResearchAgent()
        self.session_active = True

    def display_welcome(self):
        """Display the welcome message."""
        welcome_text = """
        🧠 DocuMindAI - Document Intelligence Platform

        Features:
        - Web search with real-time information
        - Document analysis (PDF, TXT)
        - Conversation memory
        - Multi-tool agent decision making
        - Streaming responses

        Commands:
        - 'upload <filename>' - Analyze a document
        - 'search <query>' - Web search
        - 'ask <question>' - General questions
        - 'history' - Show conversation history
        - 'clear' - Clear memory
        - 'quit' - Exit
        """
        console.print(Panel.fit(welcome_text, title="Welcome", border_style="blue"))

    def process_command(self, user_input: str):
        "Process user command"""
        if user_input.lower() in ['quit', 'exist']:
            self.session_active = False
            console.print("\n👋 Thank you for using DocuMindAI!")

        if user_input.lower() == 'history':
            history = self.agent.get_conversation_history()
            console.print("\n📜 Conversation History:")
            for i, msg in enumerate(history[-10:],1):
                console.print(f"{i}. {msg}")
            return

        if user_input.lower() == 'clear':
            self.agent.clear_memory()
            console.print("\n🧹 Memory cleared!")
            return

        #Process with agent
        with console.status("[bold green]Processing...", spinner="dots"):
            try:
                response = self.agent.process_query(user_input)
                console.print(f"\n🤖 Assistant: {response}")
            except Exception as e:
                console.print(f"\n❌ Error: {str(e)}")

        def run(self):
            """Main Application loop"""
            self.display_welcome()

            while self.session_active:
                try:
                    user_input = console.input("\n💬 You: ")
                    if user_input.strip():
                        self.process_command(user_input)
                except KeyboardInterrupt:
                    console.print("\n\n👋 Goodbye!")
                    break
                except Exception as e:
                    console.print(f"\n❌ Error: {str(e)}")

        @click.command()
        @click.option('--mode', default='cli', help='Run mode: cli or web')
        def main(mode):
            """DocuMindAI - Document Intelligence Platform"""
            if mode == 'web':
                #Run Streamlit version
                os.system("streamlit run web_app.py")
            else:
                #Run CLI version
                app = DocuMindAI()
                app.run()

        if __name__ == "__main__":
            main()
