import threading
import torch
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone
from django.urls import reverse
from langchain_core.prompts import PromptTemplate  # Updated import
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import
from langchain_community.vectorstores import FAISS  # Updated import
from langchain_community.llms import CTransformers  # Updated import
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader  # Updated import
import logging
import aiml
from pyswip import Prolog, Functor, Variable, Query  # Add Prolog import
from neo4j import GraphDatabase  # Add Neo4j import

# Initialize Prolog
prolog = Prolog()
prolog.consult("knowledgebase.pl")

# Initialize Neo4j
uri = "bolt://localhost:7687"  # Update with your Neo4j instance URI
username = "neo4j"             # Update with your Neo4j username
password = "password"          # Update with your Neo4j password
driver = GraphDatabase.driver(uri, auth=(username, password))

# Function to create nodes and relationships
def create_nodes_and_relationships(tx):
    # Gender facts
    tx.run("MERGE (a:Person {name: 'ali', gender: 'male'})")
    tx.run("MERGE (b:Person {name: 'bob', gender: 'male'})")
    tx.run("MERGE (j:Person {name: 'jack', gender: 'male'})")
    tx.run("MERGE (al:Person {name: 'alia', gender: 'female'})")
    tx.run("MERGE (t:Person {name: 'tahira', gender: 'female'})")
    tx.run("MERGE (s:Person {name: 'sara', gender: 'female'})")
    tx.run("MERGE (m:Person {name: 'mary', gender: 'female'})")
    
    # Marriage facts
    tx.run("MATCH (a:Person {name: 'ali'}), (t:Person {name: 'tahira'}) MERGE (a)-[:MARRIED]->(t)")
    tx.run("MATCH (j:Person {name: 'jack'}), (s:Person {name: 'sara'}) MERGE (j)-[:MARRIED]->(s)")
    tx.run("MATCH (b:Person {name: 'bob'}), (m:Person {name: 'mary'}) MERGE (b)-[:MARRIED]->(m)")

    # Age facts
    tx.run("MATCH (a:Person {name: 'ali'}) SET a.age = 60")
    tx.run("MATCH (t:Person {name: 'tahira'}) SET t.age = 58")
    tx.run("MATCH (j:Person {name: 'jack'}) SET j.age = 40")
    tx.run("MATCH (s:Person {name: 'sara'}) SET s.age = 38")
    tx.run("MATCH (b:Person {name: 'bob'}) SET b.age = 45")
    tx.run("MATCH (m:Person {name: 'mary'}) SET m.age = 43")

    # Family relationships
    tx.run("MATCH (a:Person {name: 'ali'}), (b:Person {name: 'bob'}) MERGE (a)-[:PARENT]->(b)")
    tx.run("MATCH (t:Person {name: 'tahira'}), (b:Person {name: 'bob'}) MERGE (t)-[:PARENT]->(b)")
    tx.run("MATCH (j:Person {name: 'jack'}), (al:Person {name: 'alia'}) MERGE (j)-[:PARENT]->(al)")
    tx.run("MATCH (s:Person {name: 'sara'}), (al:Person {name: 'alia'}) MERGE (s)-[:PARENT]->(al)")

    # Death facts
    tx.run("MATCH (j:Person {name: 'jack'}) SET j:Deceased")

    # Foster relationships
    tx.run("MATCH (a:Person {name: 'ali'}), (m:Person {name: 'mary'}) MERGE (a)-[:FOSTER_PARENT]->(m)")
    tx.run("MATCH (t:Person {name: 'tahira'}), (m:Person {name: 'mary'}) MERGE (t)-[:FOSTER_PARENT]->(m)")

def create_derived_relationships(tx):
    # Aunt relationships
    tx.run("""
        MATCH (a:Person)-[:PARENT]->(p:Person)-[:PARENT]->(c:Person)
        WHERE a.gender = 'female' AND a <> p
        MERGE (a)-[:AUNT]->(c)
    """)

    # Uncle relationships
    tx.run("""
        MATCH (u:Person)-[:PARENT]->(p:Person)-[:PARENT]->(c:Person)
        WHERE u.gender = 'male' AND u <> p
        MERGE (u)-[:UNCLE]->(c)
    """)

    # Widow relationships
    tx.run("""
        MATCH (w:Person)-[:MARRIED]->(h:Person)
        WHERE w.gender = 'female' AND h:Deceased
        SET w:Widow
    """)

    # Foster child relationships
    tx.run("""
        MATCH (p:Person)-[:FOSTER_PARENT]->(c:Person)
        MERGE (c)-[:FOSTER_CHILD]->(p)
    """)

    # Mother-in-law relationships
    tx.run("""
        MATCH (mil:Person)-[:PARENT]->(s:Person)<-[:MARRIED]-(p:Person)
        WHERE mil.gender = 'female'
        MERGE (mil)-[:MOTHER_IN_LAW]->(p)
    """)

# Create nodes and relationships in the database
with driver.session() as session:
    session.write_transaction(create_nodes_and_relationships)
    session.write_transaction(create_derived_relationships)

# Close the driver
driver.close()

# Learning aiml
k = aiml.Kernel()
k.learn("aiml/*.aiml")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

DATA_PATH = "data/"
DB_FAISS_PATH = "vectorstores/db_faiss"

custom_prompt_template = """ Use the following pieces of information to answer the user's questions.
If you don't know the answer, please just say that you don't know the answer, don't try to make up an answer.

Context: {context}
Question: {question}

Only return the helpful answer below and nothing else.

Helpful Answer:
"""

def set_custom_prompt():
    prompt = PromptTemplate(template=custom_prompt_template, input_variables=['context', 'question'])
    return prompt

def load_llm():
    llm = CTransformers(
        model="llama-2-7b-chat.ggmlv3.q5_K_S.bin",
        model_type="llama",
        max_new_tokens=512,
        temperature=0.5,
    )
    return llm

def retrieval_qa_chain(llm, prompt, db):
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={'k': 2}),
        return_source_documents=True,
        chain_type_kwargs={'prompt': prompt}
    )
    return qa_chain

def prolog_query(query):
    result = list(prolog.query(query))
    return result

def chatbot(request):
    if request.user.is_authenticated:
        chats = Chat.objects.filter(user=request.user)

        if request.method == 'POST':
            message = request.POST.get('message')
            logging.debug(f"Received message: {message}")

            if any(salutation in message.lower() for salutation in ["hi", "hello", "hey"]):
                response = "Hi! I am A.T.O.M. Nice to meet you. How can I assist you today?"
            elif any(salutation in message.lower() for salutation in ["salam", "assalam o alikum", "aoa"]) or any(
                    salutation in message.upper() for salutation in ["SALAM", "ASSALAM O ALIKUM", "AOA"]):
                response = "Walikum Salam! I am A.T.O.M. Nice to meet you. How can I assist you today?"
            elif any(keyword in message.lower() for keyword in ["creator", "made", "who created you", "who made you", "who created you?", "who made u?"]):
                response = "I was created by Usman Ghani. He is a really talented developer."
            else:
                prolog_queries = {
                    "who is married": "married(X, Y)",
                    "who is the wife of": "married(Y, X)",
                    "who is the husband of": "married(X, Y)",
                    "who are the parents of": "parent(X, Y)",
                    "who are the children of": "parent(Y, X)",
                    "who is the aunt of": "aunt(X, Y)",
                    "who is the uncle of": "uncle(X, Y)",
                    "who is the widow of": "widow(X)",
                    "who is the foster child of": "foster_child(X, Y)",
                    "who is the mother-in-law of": "mother_in_law(X, Y)",
                }

                query = None
                for key in prolog_queries:
                    if key in message.lower():
                        if key in ["who is the wife of", "who is the husband of"]:
                            name = message.lower().split(" of ")[-1].strip()
                            query = f"{prolog_queries[key]}('{name}', Y)"
                        else:
                            query = prolog_queries[key]
                        break

                if query:
                    results = prolog_query(query)
                    response = ", ".join(f"{result['X']} is {result['Y']}" for result in results) if results else "I don't know the answer to that."
                else:
                    response = k.respond(message)

            chat = Chat(user=request.user, message=message, response=response, timestamp=timezone.now())
            chat.save()

        return render(request, 'chatbot.html', {'chats': chats})
    else:
        return redirect(reverse('login'))
