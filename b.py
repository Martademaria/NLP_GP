import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Retrieve keys from environment variables
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

# Function to show restaurant information
def show_restaurant_info():
    st.image("labellavita2.png", use_container_width=True)
    st.image("aboutus3.png", use_container_width=True)
    st.image("aaa.png", use_container_width=True)

# Function to handle chatbot interactions
def show_chatbot():
    # Replace the title with an image
    st.image("va.png", use_container_width=True)

    # Add chatbot description with emojis
    st.markdown("""
    Our assistant is here to help you with:
    - **Menu questions** ️
    - **Popular dishes** ️
    - **Allergies** ️
    - **Vegan options & Daily specials**

    Just type your question, and our chatbot will assist you!
    """)

    # Initialize conversation history in session state
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = [
            {
                "role": "system", 
                "content": (
                    "You are a multilingual expert waiter assisting customers with menu inquiries. "
                    "Answer questions about the menu in an energetic and respectful tone. "
                    "Provide information only from the data. If you cannot answer, respond with: "
                    "'Sorry, I cannot answer that question. Please ask the waiter or call 9001-0304.'\n\n"
                    "Example:\n\n"
                    "Question: What are the best gluten-free spicy options?\n"
                    "Answer:\n"
                    "The best gluten-free and spicy dishes are Cacio and Tartufo ($10) and Duomo di Parma ($15).\n"
                    "The first is served directly on top of a Pecorino cheese round, and the second features Jamón de Parma, "
                    "San Marzano tomatoes, stracciatella, fresh basil, olives, and a touch of paprika.\n"
                    "If unable to answer, use the fallback message."
                )
            }
        ]

    user_query = st.text_input("How can I assist you today?")

    if user_query:
        # Add user query to conversation history
        st.session_state.conversation_history.append({"role": "user", "content": user_query})

        # Try generating assistant response, handle rate limit error
        try:
            assistant_response = generate_response(st.session_state.conversation_history)
            # Add assistant response to conversation history
            st.session_state.conversation_history.append({"role": "assistant", "content": assistant_response})

            # Display user and assistant messages
            user_message = st.session_state.conversation_history[-2]
            assistant_message = st.session_state.conversation_history[-1]

            st.chat_message("user").markdown(f"**You:** {user_message['content']}", unsafe_allow_html=True)
            st.chat_message("assistant").markdown(f"**Assistant:** {assistant_message['content']}", unsafe_allow_html=True)
        except Exception as e:
            # Handle rate limit error specifically
            if "429" in str(e):
                st.warning("The assistant is currently busy. Please try again in 60 seconds.", icon="⏳")
            else:
                st.error("An error occurred while processing your request. Please try again later.", icon="⚠️")

# Function to generate chatbot responses
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
                    "index_name": "try1ragnlp",  # Ensure this index exists in Azure
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

    # Remove document references like [doc1], [doc2], etc.
    response_content = re.sub(r'\[doc\d+\]', '', response_content)

    return response_content

# Function to display the menu image
def show_random_menu_image():
    st.image("themenu.png", use_container_width=True)

# Main function to display content and chatbot
def main():
    show_restaurant_info()

    # Add space before the button
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # Show menu button
    if st.button("See Menu", key="random_menu_button", use_container_width=True):
        show_random_menu_image()

    # Show location image below the button
    st.image("loc.png", use_container_width=True)

    # Show chatbot
    show_chatbot()

if __name__ == "__main__":
    main()








