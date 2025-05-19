import os
import chainlit as cl
from dotenv import load_dotenv
from typing import Optional, Dict
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.tool import function_tool

load_dotenv()

# Initialize with native Gemini client instead of OpenAI wrapper
gemini_api_key = os.getenv("GEMINI_API_KEY")

# More reliable configuration
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",  # Updated endpoint
)

# Configure the language model for the first agent
model_greeting = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=provider)
agent_greeting = Agent(
    name="Greeting Agent",
    instructions="""You are a Greeting Agent designed to provide friendly interactions and information about sarwat afreen.

Your responsibilities:
1. Greet users warmly when they say hello (respond with 'Salam from sarwat afreen ')
2. Say goodbye appropriately when users leave (respond with 'Allah Hafiz from sarwat afreen')
3. When users request information about sarwat afreen, use the get_sarwat_info tool to retrieve and share his profile information
4. For any questions not related to greetings or sarwat afreen, politely explain: 'I'm only able to provide greetings and information about sarwat afreen. I can't answer other questions at this time.'

Always maintain a friendly, professional tone and ensure responses are helpful within your defined scope.""",
    model=model_greeting,
    tools=[get_sarwat_info], # type: ignore
)


# Configure the language model for the second agent
model_info = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider,
    temperature=0.7  # Added for more varied responses
)

@function_tool("get_sarwat_info")
def get_sarwat_info() -> str:
    """Returns detailed information about Sarwat Afreen"""
    return f"""Sarwat Afreen is a notable personality. Here are some details:
    - Profession: [Add actual details]
    - Achievements: [Add actual details]
    - Background: [Add actual details]"""

agent_info = Agent(
    name="SarwatInfoBot",
    instructions="""You are a specialized assistant for providing information about Sarwat Afreen. Follow these rules STRICTLY:

1. Greetings:
    - When greeted first: "Salam! I'm here to share information about Sarwat Afreen."
    - When said goodbye: "Allah Hafiz! Feel free to ask about Sarwat Afreen anytime."

2. Information Provision:
    - ONLY discuss topics related to Sarwat Afreen
    - For Sarwat-related queries, ALWAYS use get_sarwat_info tool
    - NEVER make up information - only use what the tool provides

3. Off-topic Handling:
    - For non-Sarwat topics: "I specialize only in information about Sarwat Afreen."
    - Politely decline any other requests

4. Response Style:
    - Always be professional and factual
    - Keep responses concise (1-2 sentences)
    - Never repeat user's words back to them""",
    model=model_info,
    tools=[get_sarwat_info],
)

@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    """
    Handle the OAuth callback from GitHub
    Return the user object if authentication is successful, None otherwise
    """

    print(f"Provider: {provider_id}")  # Print provider ID for debugging
    print(f"User data: {raw_user_data}")  # Print user data for debugging
    return default_user  # Return the default user object


@cl.on_chat_start
async def start_chat():
    cl.user_session.set("history", [])
    await cl.Message(
        content="Hello! How can I help you today?"
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):

    history = cl.user_session.get("history")  # Get chat history from session

    history.append(
        {"role": "user", "content": message.content}
    )  # Add user message to history

    # Decide which agent to use based on the user's message
    if "sarwat afreen" in message.content.lower():
        result = await cl.make_async(Runner.run_sync)(agent_info, input=history)
    else:
        result = await cl.make_async(Runner.run_sync)(agent_greeting, input=history)

    response_text = result.final_output
    await cl.Message(content=response_text).send()

    history.append({"role": "assistant", "content": response_text})
    cl.user_session.set("history", history)













# import os  # For accessing environment variables
# import chainlit as cl  # Web UI framework for chat applications
# # import google.generativeai as genai  # Google's Generative AI library
# from dotenv import load_dotenv  # For loading environment variables
# from typing import Optional, Dict  # Type hints for better code clarity
# from agents import Agent,Runner,AsyncOpenAI,OpenAIChatCompletionsModel
# from agents.tool import function_tool
# import requests
# # Load environment variables from .env file
# load_dotenv()

# # Get Gemini API key from environment variables
# gemini_api_key = os.getenv("GEMINI_API_KEY")
# # Initialize OpenAI provider with Gemini API settings
# provider = AsyncOpenAI(
#     api_key=gemini_api_key,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai",
# )

# # Configure the language model
# model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=provider)
# @function_tool("greet_weather")
# def greet_weather(location: str) -> str:
#     """ 
#     Function to greet the user with a friendly message and provide weather information.
#     """
#     return f"Hello! The weather in {location} is sunny and warm today.",

# agent = Agent(
#     name= "Greeting Agent",
#     instructions="You are a  Greeting Agent. Your task is to greet the user with a friently " \
#     "message.interactions and information about Sarwat afreen",
#     model=model,
#     tools=[greet_weather],
# )
# agent = Agent(
#     name="Greeting Agent",
#     instructions="""You are a Greeting Agent designed to provide friendly interactions and information about Asharib Ali.

# Your responsibilities:
# 1. Greet users warmly when they say hello (respond with 'Salam from sarwat afreen')
# 2. Say goodbye appropriately when users leave (respond with 'Allah Hafiz from sarwat afreen')
# 3. When users request information about sarwat afreen, use the get_asharib_data tool to retrieve and share his profile information
# 4. For any questions not related to greetings or sarwat afreen, politely explain: 'I'm only able to provide greetings and information about Asharib Ali. I can't answer other questions at this time.'

# Always maintain a friendly, professional tone and ensure responses are helpful within your defined scope.""",
#     model=model,
#     tools=[get_sarwat_data],
# )
# @cl.on_message
# async def on_message(message: cl.Message):
#     # Run the agent with user message
#     response = await agent.run(message.content)

#     # Send agent's reply to the user
#     await cl.Message(content=response).send()
# # Configure Gemini with API key
# # genai.configure(api_key=gemini_api_key)

# # # Initialize Gemini model
# # model = genai.GenerativeModel(
# #     model_name="gemini-2.0-flash"  # Using Gemini's flash model for faster responses
# # )
# //////////////////////////////////////////////////////////

# # Decorator to handle OAuth callback from GitHub
# @cl.oauth_callback
# def oauth_callback(
#     provider_id: str,  # ID of the OAuth provider (GitHub)
#     token: str,  # OAuth access token
#     raw_user_data: Dict[str, str],  # User data from GitHub
#     default_user: cl.User,  # Default user object from Chainlit
# ) -> Optional[cl.User]:  # Return User object or None
#     """
#     Handle the OAuth callback from GitHub
#     Return the user object if authentication is successful, None otherwise
#     """

#     print(f"Provider: {provider_id}")  # Print provider ID for debugging
#     print(f"User data: {raw_user_data}")  # Print user data for debugging

#     return default_user  # Return the default user object


# # Handler for when a new chat session starts
# @cl.on_chat_start
# async def handle_chat_start():

#     cl.user_session.set("history", [])  # Initialize empty chat history

#     await cl.Message(
#         content="Hello! How can I help you today?"
#     ).send()  # Send welcome message


# # Handler for incoming chat messages
# @cl.on_message
# async def handle_message(message: cl.Message):

#     history = cl.user_session.get("history")  # Get chat history from session

#     history.append(
#         {"role": "user", "content": message.content}
#     )  # Add user message to history
#     result = await cl.make_async(Runner.run_sync)(agent, input=history )
#     response_text = result.final_output
#     await cl.Message(content=response_text).sent()

#     history.append({"role": "assistant", "content": response_text})
#     cl.user_session.set("history",history)
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






# def main():
#     print("Hello from build-advance-agent-openal!")


# if __name__ == "__main__":
#     main()
