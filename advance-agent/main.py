import os  # For accessing environment variables
import chainlit as cl  # Web UI framework for chat applications
# import google.generativeai as genai  # Google's Generative AI library
from dotenv import load_dotenv  # For loading environment variables
from typing import Optional, Dict  # Type hints for better code clarity
from agents import Agent,Runner,AsyncOpenAI,OpenAIChatCompletionsModel
from agents.tool import function_tool
import requests
# Load environment variables from .env file
load_dotenv()

# Get Gemini API key from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")
# Initialize OpenAI provider with Gemini API settings
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
)

# Configure the language model
model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=provider)
@function_tool("greet_weather")
def greet_weather(location: str) -> str:
    """ 
    Function to greet the user with a friendly message and provide weather information.
    """
    return f"Hello! The weather in {location} is sunny and warm today.",

agent = Agent(
    name= "Greeting Agent",
    instructions="You are a  Greeting Agent. Your task is to greet the user with a friently " \
    "message.interactions and information about Sarwat afreen",
    model=model,
    tools=[greet_weather],
)
agent = Agent(
    name="Greeting Agent",
    instructions="""You are a Greeting Agent designed to provide friendly interactions and information about Asharib Ali.

Your responsibilities:
1. Greet users warmly when they say hello (respond with 'Salam from sarwat afreen')
2. Say goodbye appropriately when users leave (respond with 'Allah Hafiz from sarwat afreen')
3. When users request information about sarwat afreen, use the get_asharib_data tool to retrieve and share his profile information
4. For any questions not related to greetings or sarwat afreen, politely explain: 'I'm only able to provide greetings and information about Asharib Ali. I can't answer other questions at this time.'

Always maintain a friendly, professional tone and ensure responses are helpful within your defined scope.""",
    model=model,
    tools=[get_sarwat_data],
)
@cl.on_message
async def on_message(message: cl.Message):
    # Run the agent with user message
    response = await agent.run(message.content)

    # Send agent's reply to the user
    await cl.Message(content=response).send()
# Configure Gemini with API key
# genai.configure(api_key=gemini_api_key)

# # Initialize Gemini model
# model = genai.GenerativeModel(
#     model_name="gemini-2.0-flash"  # Using Gemini's flash model for faster responses
# )
//////////////////////////////////////////////////////////

# Decorator to handle OAuth callback from GitHub
@cl.oauth_callback
def oauth_callback(
    provider_id: str,  # ID of the OAuth provider (GitHub)
    token: str,  # OAuth access token
    raw_user_data: Dict[str, str],  # User data from GitHub
    default_user: cl.User,  # Default user object from Chainlit
) -> Optional[cl.User]:  # Return User object or None
    """
    Handle the OAuth callback from GitHub
    Return the user object if authentication is successful, None otherwise
    """

    print(f"Provider: {provider_id}")  # Print provider ID for debugging
    print(f"User data: {raw_user_data}")  # Print user data for debugging

    return default_user  # Return the default user object


# Handler for when a new chat session starts
@cl.on_chat_start
async def handle_chat_start():

    cl.user_session.set("history", [])  # Initialize empty chat history

    await cl.Message(
        content="Hello! How can I help you today?"
    ).send()  # Send welcome message


# Handler for incoming chat messages
@cl.on_message
async def handle_message(message: cl.Message):

    history = cl.user_session.get("history")  # Get chat history from session

    history.append(
        {"role": "user", "content": message.content}
    )  # Add user message to history
    result = await cl.make_async(Runner.run_sync)(agent, input=history )
    response_text = result.final_output
    await cl.Message(content=response_text).sent()

    history.append({"role": "assistant", "content": response_text})
    cl.user_session.set("history",history)
    //////////////////////////////////////////////////
    # Format chat history for Gemini model
    # formatted_history = []
    # for msg in history:
    #     role = "user" if msg["role"] == "user" else "model"  # Determine message role
    #     formatted_history.append(
    #         {"role": role, "parts": [{"text": msg["content"]}]}
    #     )  # Format message

    # response = model.generate_content(formatted_history)  # Get response from Gemini

    # response_text = (
    #     response.text if hasattr(response, "text") else ""
    # )  # Extract response text safely

    # history.append(
    #     {"role": "assistant", "content": response_text}
    # )  # Add assistant response to history
    # cl.user_session.set("history", history)  # Update session history

    # await cl.Message(content=response_text).send()  # Send response to user





# def main():
#     print("Hello from advance-agent!")


# if __name__ == "__main__":
#     main()
