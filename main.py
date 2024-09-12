import streamlit as st
import yfinance as yf
import pandas as pd
# from langchain.agents import create_pandas_dataframe_agent
# from langchain.chat_models import ChatOpenAI
import re
from dotenv import load_dotenv
import sqlite3
from htmlTemplates import css, user_template, bot_template

import autogen
import json

import asyncio
from autogen import AssistantAgent, UserProxyAgent

config_list_gpt4 = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    file_location="./AppV6",
    filter_dict={
        "model": ["gpt-3.5-turbo", "gpt-35-turbo", "gpt-35-turbo-0613", "gpt-4", "gpt4", "gpt-4-32k", "gpt432k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    },
)

def create_users_db():
    conn = sqlite3.connect('MASTER.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_user_to_db(email, password):
    conn = sqlite3.connect('MASTER.db')
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO Users (email, password)
        VALUES (?, ?)
    """
    cursor.execute(insert_query, (email, password))
    conn.commit()
    conn.close()


def authenticate_user(email, password):
    conn = sqlite3.connect('MASTER.db')
    cursor = conn.cursor()
    select_query = """
        SELECT * FROM Users WHERE email = ? AND password = ?
    """
    cursor.execute(select_query, (email, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return True
    else:
        return False


def init_ses_states():
    st.session_state.setdefault('chat_history', [])
    st.session_state.setdefault('user_authenticated', False)


def relative_returns(df):
    rel = df.pct_change()
    cumret = ((1 + rel).cumprod() - 1).fillna(0)
    return cumret


def approve_password(password):
    if len(password) >= 8 and re.search(r"(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[_@$#!?&*%])", password):
        return True
    return False
    

def approve_email(email):
    email_regex = '^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(email_regex, email):
        return True
    else:
        return False
    

def user_authentication_tab():
    with st.expander("User Authentication", expanded=True):
        login_tab, create_account_tab = st.tabs(["Login", "Create Account"])

        with login_tab:
            email = st.text_input("Email:") 
            password = st.text_input("Password:", type='password')
            if st.button("Login"):
                if authenticate_user(email=email,password=password):
                    st.session_state.user_authenticated = True
                else:
                    st.caption('Incorrect Username or Password.')

            if st.session_state.user_authenticated:
                st.caption("User Authenticated")

        with create_account_tab:
            new_email = st.text_input("New Email:")
            new_password = st.text_input("New Password:", type='password')
            confirm_password = st.text_input("Confirm Password:", type='password')
            if st.button("Create Account"):
                if not approve_email(new_email):
                    st.caption("Invalid Email")
                    return
                if not approve_password(new_password):
                    st.caption("Invalid Password")
                    return
                if new_password != confirm_password:
                    st.caption("Passwords do not match")
                    return
                add_user_to_db(email=new_email, password=new_password)
                st.caption(f"{new_email} Successfully Added")


class TrackableAssistantAgent(AssistantAgent):
    """
    A custom AssistantAgent that tracks the messages it receives.

    This is done by overriding the `_process_received_message` method.
    """

    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)


class TrackableUserProxyAgent(UserProxyAgent):
    """
    A custom UserProxyAgent that tracks the messages it receives.

    This is done by overriding the `_process_received_message` method.
    """
 
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)


def main():
    # setup page title and description
    st.set_page_config(page_title="AutoGen Chat App", page_icon="🤖", layout="wide")
    # st.set_page_config(page_title="Stock Price AI Bot", page_icon=":chart:")
    st.markdown(
    "This is a demo of AutoGen chat agents. You can use it to chat with OpenAI's GPT-3 and GPT-4 models. They are able to execute commands, answer questions, and even write code."
    )
    st.markdown("An example a question you can ask is: 'How is the S&P 500 doing today? Summarize the news for me.'")
    st.markdown("Start by getting an API key from OpenAI. You can get one [here](https://openai.com/pricing).")
    
    # add placeholders for selected model and key
    selected_model = None
    selected_key = None

    st.write(css, unsafe_allow_html=True)
    create_users_db()
    init_ses_states()
    st.title("Stock Price AI Bot")
    st.caption("Visualizations and OpenAI Chatbot for Multiple Stocks Over A Specified Period")

    with st.sidebar:
        user_authentication_tab()
    
    if st.session_state.user_authenticated:
        with st.sidebar:
            st.header("OpenAI Configuration")
            # selected_model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4-1106-preview"], index=1)
            selected_model = st.selectbox("Model", ["gpt-4", "gpt-3.5-turbo", "gpt-4-1106-preview"], index=0)
            st.markdown("Press enter to save key")
            st.markdown(
                "For more information about the models, see [here](https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo)."
            )
            selected_key = st.text_input("API_Key", type="password")            

        with st.expander("Settings",expanded=True):
            asset_tickers = sorted(['DOW','NVDA','TSL','GOOGL','AMZN','AI','NIO','LCID','F','LYFY','AAPL', 'MSFT', 'BTC-USD', 'ETH-USD'])
            asset_dropdown = st.multiselect('Pick Assets:', asset_tickers)

            metric_tickers = ['Adj. Close', 'Relative Returns']
            metric_dropdown = st.selectbox("Metric", metric_tickers)

            viz_tickers = ['Line Chart', 'Area Chart']
            viz_dropdown = st.multiselect("Pick Charts:", viz_tickers)

            start = st.date_input('Start', value=pd.to_datetime('2023-01-01'))
            end = st.date_input('End', value=pd.to_datetime('today'))

            chatbot_temp = st.slider("Chat Bot Temperature",0.0,1.0,0.5)

        # Only when a stock is selected
        if len(asset_dropdown) > 0:
            df = yf.download(asset_dropdown,start,end)['Adj Close']
            if metric_dropdown == 'Relative Returns':
                df = relative_returns(df)
            if len(viz_dropdown) > 0:
                with st.expander("Data Visualizations for {} of {}".format(metric_dropdown,asset_dropdown), expanded=True):
                    if "Line Chart" in viz_dropdown:
                        st.subheader("Line Chart")
                        st.line_chart(df)
                    if "Area Chart" in viz_dropdown:
                        st.subheader("Area Chart")
                        st.area_chart(df)
            st.header("Chat with your Data") 

            user_input = st.text_input("User Input")
            # only run if user input is not empty and model and key are selected
            if user_input:
                if not selected_key or not selected_model:
                    st.warning("You must provide valid OpenAI API key and choose preferred model", icon="⚠️")
                    st.stop()
                
                try:
                    # setup request timeout and config list
                    llm_config = {
                        # "request_timeout": 600,
                        "config_list": [
                            {"model": selected_model, "api_key": config_list_gpt4[0]['api_key']},
                        ],
                        "seed": 42,  # seed for reproducibility
                        "temperature": 0,  # temperature of 0 means deterministic output
                    }
                    # create an AssistantAgent instance named "assistant"
                    assistant = TrackableAssistantAgent(name="assistant", llm_config=llm_config)

                    # create a UserProxyAgent instance named "user"
                    # human_input_mode is set to "NEVER" to prevent the agent from asking for user input
                    user_proxy = TrackableUserProxyAgent(
                        name="user",
                        human_input_mode="NEVER",
                        llm_config=llm_config,
                        is_termination_msg=lambda x: x.get("content", "").strip().endswith("TERMINATE"),
                    )
                    
                    # # Create an event loop: this is needed to run asynchronous functions
                    # loop = asyncio.new_event_loop()
                    # asyncio.set_event_loop(loop)
                    
                    # Replace the event loop creation and setting part with this
                    # loop = asyncio.get_event_loop()
                    loop = asyncio.new_event_loop()
                    if not loop.is_running():
                        asyncio.set_event_loop(loop)

                    # Define an asynchronous function: this is needed to use await
                    if "chat_initiated" not in st.session_state:
                        st.session_state.chat_initiated = False  # Initialize the session state

                except Exception as ex:
                    print(f"Exception : {str(ex)}")
                    # print(f"exit()")
                    # exit()            
                        
            else:
                print(f"Warning !")
                print(f"Please type any your question !")

            
            # if st.button("Execute") and query:
            if st.button("Execute") and user_input:
                with st.spinner('Generating response...'):
        
                    if not st.session_state.chat_initiated:                        
                        async def initiate_chat():
                            await user_proxy.a_initiate_chat(
                                assistant,
                                message=f"{user_input} with the relative returns data : {df}",
                                max_consecutive_auto_reply=20,
                                is_termination_msg=lambda x: x.get("content", "").strip().endswith("TERMINATE"),
                            )
                            st.stop()  # Stop code execution after termination command
                        # Run the asynchronous function within the event loop
                        loop.run_until_complete(initiate_chat())
                        # Close the event loop
                        loop.close()
                        st.session_state.chat_initiated = True  # Set the state to True after running the chat

    # stop app after termination command
    st.stop()



if __name__ == '__main__':
    load_dotenv()
    main()





# which stock performed best in terms of relative returns ? 

# which stock performed best in terms of relative returns? Prints that result to the screen.

# Find scientific articles about tensor networks for deep learning or LLM . Create a markdown table of different domains.


