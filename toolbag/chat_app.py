import tkinter as tk
from tkinter import scrolledtext
import os
import json
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

CONFIG_FILE = "config.json"


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat with Websites")

        self.chat_history = [
            AIMessage(content="Hello, I am a bot. How can I help you?"),
        ]
        self.vector_store = None

        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        self.url_label = tk.Label(self.root, text="Website URL:")
        self.url_label.pack(pady=5)

        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)
        self.url_entry.insert(0, "https://centralfloridaattorney.net")

        self.load_button = tk.Button(self.root, text="Load Website", command=self.load_website)
        self.load_button.pack(pady=5)

        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=60, height=15)
        self.chat_display.pack(pady=10)

        self.console_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=60, height=10)
        self.console_display.pack(pady=10)

        self.user_input = tk.Entry(self.root, width=50)
        self.user_input.insert(0, "Reasons to love John Iriye, let me count the ways.")
        self.user_input.pack(pady=5)
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        self.update_chat_display()

    def log_message(self, message):
        self.console_display.config(state=tk.NORMAL)
        self.console_display.insert(tk.END, message + "\n")
        self.console_display.config(state=tk.DISABLED)

    def load_website(self):
        url = self.url_entry.get()
        if url:
            self.vector_store = self.get_vectorstore_from_url(url)
            self.log_message("Website loaded successfully!")
            self.save_config()
        else:
            self.log_message("Please enter a website URL.")

    def send_message(self, event=None):
        user_query = self.user_input.get()
        if user_query and self.vector_store:
            response = self.get_response(user_query)
            self.chat_history.append(HumanMessage(content=user_query))
            self.chat_history.append(AIMessage(content=response))
            self.update_chat_display()
            self.user_input.delete(0, tk.END)

    def update_chat_display(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        for message in self.chat_history:
            if isinstance(message, AIMessage):
                self.chat_display.insert(tk.END, "AI: " + message.content + "\n\n")
            elif isinstance(message, HumanMessage):
                self.chat_display.insert(tk.END, "Human: " + message.content + "\n\n")
        self.chat_display.config(state=tk.DISABLED)

    def get_vectorstore_from_url(self, url):
        loader = WebBaseLoader(url)
        document = loader.load()

        text_splitter = RecursiveCharacterTextSplitter()
        document_chunks = text_splitter.split_documents(document)

        vector_store = Chroma.from_documents(document_chunks, OpenAIEmbeddings())
        return vector_store

    def get_context_retriever_chain(self, vector_store):
        llm = ChatOpenAI()

        retriever = vector_store.as_retriever()

        prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
        ])

        retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
        return retriever_chain

    def get_conversational_rag_chain(self, retriever_chain):
        llm = ChatOpenAI()

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer the user's questions based on the below context:\n\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        stuff_documents_chain = create_stuff_documents_chain(llm, prompt)
        return create_retrieval_chain(retriever_chain, stuff_documents_chain)

    def get_response(self, user_input):
        retriever_chain = self.get_context_retriever_chain(self.vector_store)
        conversation_rag_chain = self.get_conversational_rag_chain(retriever_chain)

        response = conversation_rag_chain.invoke({
            "chat_history": self.chat_history,
            "input": user_input
        })

        return response['answer']

    def save_config(self):
        config_data = {
            "website_url": self.url_entry.get(),
            "chat_history": [{"type": "AI" if isinstance(msg, AIMessage) else "Human", "content": msg.content} for msg in self.chat_history]
        }
        with open(CONFIG_FILE, "w") as config_file:
            json.dump(config_data, config_file)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as config_file:
                config_data = json.load(config_file)
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, config_data.get("website_url", ""))
                self.chat_history = [
                    AIMessage(content=msg["content"]) if msg["type"] == "AI" else HumanMessage(content=msg["content"])
                    for msg in config_data.get("chat_history", [])
                ]
                self.update_chat_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
