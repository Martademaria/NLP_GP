import streamlit as st
from openai import AzureOpenAI
import os
import random  # Import random for selecting images
from datetime import datetime
import re

from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Recuperar las claves desde las variables de entorno
ENDPOINT = os.getenv("AZURE_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
SUBSCRIPTION_KEY = os.getenv("SUBSCRIPTION_KEY")


# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=SUBSCRIPTION_KEY,
    api_version="2024-05-01-preview",
)

# Show restaurant information
def show_restaurant_info():
    st.image("labellavita2.png", use_container_width=True)
    st.image("aboutus3.png", use_container_width=True)
    st.image("aaa.png", use_container_width=True)  # This image should be displayed normally

def show_chatbot():
    # Replace the title with an image
    st.image("va.png", use_container_width=True)
    
    # Modify the description with relevant emojis
    st.markdown("""
    Our assistant is here to help you with:
    - **Menu questions** ️
    - **Popular dishes** ️
    - **Allergies** ️
    - **Vegan options & Daily specials** 
    
    Just type your question, and our chatbot will assist you!
    """)
    
    # Initialize conversation history in session_state
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = [
            {"role": "system", "content": "You are a restaurant assistant."}
        ]

    user_query = st.text_input("How can I assist you today?")

    if user_query:
        # Add user query to history
        st.session_state.conversation_history.append({"role": "user", "content": user_query})

        # Generate assistant's response
        assistant_response = generate_response(st.session_state.conversation_history)

        # Add assistant's response to history
        st.session_state.conversation_history.append({"role": "assistant", "content": assistant_response})

        # Display only the most recent user and assistant message
        user_message = st.session_state.conversation_history[-2]
        assistant_message = st.session_state.conversation_history[-1]

        # Display user message with red background in chat box
        st.chat_message("user").markdown(f"**You:** {user_message['content']}", unsafe_allow_html=True)

        # Display assistant message with yellow background in chat box
        st.chat_message("assistant").markdown(f"**Assistant:** {assistant_message['content']}", unsafe_allow_html=True)


import re  # Asegúrate de importar 're' al inicio del script

# Function to generate the chatbot response
def generate_response(conversation_history):
    # Generate response using Azure OpenAI
    completion = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=conversation_history,
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        extra_body={
            "data_sources": [{
                "type": "azure_search",
                "parameters": {
                    "endpoint": SEARCH_ENDPOINT,
                    "index_name": "try1ragnlp",  # Make sure this index exists in Azure
                    "semantic_configuration": "azureml-default",
                    "authentication": {
                        "type": "api_key",
                        "key": SEARCH_KEY
                    },
                    "embedding_dependency": {
                        "type": "endpoint",
                        "endpoint": f"{ENDPOINT}/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-07-01-preview",
                        "authentication": {
                            "type": "api_key",
                            "key": SUBSCRIPTION_KEY
                        }
                    },
                    "query_type": "vector_simple_hybrid",
                    "top_n_documents": 5
                }
            }]
        }
    )

    response_content = completion.choices[0].message.content.strip()

    # Remove any document references like [doc1], [doc2], [doc3], etc.
    response_content = re.sub(r'\[doc\d+\]', '', response_content)

    return response_content

    
# Function to display the menu image
def show_random_menu_image():
    st.image("themenu.png", use_container_width=True)  # Use the correct width for the menu image

# Main function to display content and chatbot
def main():
    show_restaurant_info()

    # Use st.markdown to add extra space before the button
    st.markdown("<br><br><br>", unsafe_allow_html=True)  # Adds space before button
    
    # Center the button using st.button
    if st.button("See Menu", key="random_menu_button", use_container_width=True):
        show_random_menu_image()

    # Show 'loc.png' image below the button and menu
    st.image("loc.png", use_container_width=True)  # Show this image after the button

    show_chatbot()

if __name__ == "__main__":
    main()
