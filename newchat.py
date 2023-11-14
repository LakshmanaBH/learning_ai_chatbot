import openai
import streamlit as st
from streamlit_chat import message
import os

# Set org ID and API key
os.environ["OPENAI_API_KEY"] = "sk-6sjOPZjhKNPKA9OGr2qBT3BlbkFxxxxxxxxxxxxxxxxxxxx"
openai.api_key = "sk-6sjOPZjhKNPKA9OGr2qBT3BlbkFxxxxxxxxxxxxxxxx"

# Setting page title and header
st.set_page_config(page_title="Lachi", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>HR Book</h1>", unsafe_allow_html=True)

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0
if "current_intent" not in st.session_state:
        st.session_state.current_intent = ''
if 'flow_count' not in st.session_state:
    st.session_state['flow_count'] = 0
if 'current_flow' not in st.session_state:
    st.session_state['current_flow'] = False
if 'flow_answers' not in st.session_state:
    st.session_state['flow_answers'] = []
if 'flow_question' not in st.session_state:
    st.session_state['flow_question'] = ''
if 'prev_question' not in st.session_state:
    st.session_state['prev_question'] = ''

# Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
st.sidebar.title("Sidebar")
model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
counter_placeholder = st.sidebar.empty()
counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button("Clear Conversation", key="clear")

# Map model names to OpenAI model IDs
if model_name == "GPT-3.5":
    model = "gpt-3.5-turbo"
else:
    model = "gpt-4"

def resetSessionState():    
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    st.session_state['flow_count'] = 0
    st.session_state['flow_answers'] = []
    st.session_state['current_flow'] = False
    st.session_state['flow_question'] = ''
    st.session_state['prev_question'] = ''

# reset everything
if clear_button:
    resetSessionState()
    st.session_state['generated'] = []
    st.session_state['past'] = []
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

def Intent_Classification(user_input):
    st.session_state['messages'].append({"role": "user", "content": user_input})
    completion = openai.ChatCompletion.create(
    model="ft:gpt-3.5-turbo-0613:nuvento::86kobmRR",
    messages=[
      {
        "role": "system",
        "content":"Classify the user input into one of the cateogries. The categories are 'LeaveApplication' or 'GetLeaves' or 'Other'.",
      },
      {
          "role": "user",
          "content": user_input,
      }
    ],)    
    response = completion.choices[0].message['content']
    st.session_state['messages'].append({"role": "assistant", "content": response})
    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens

# generate a response
def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    completion = openai.ChatCompletion.create(
        model=model,
        messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content
    st.session_state['messages'].append({"role": "assistant", "content": response})
    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens

def getLeaves():
    MyLeaves = "These are the available leaves Casual Leaves - 5, Sick Leaves 3"
    return MyLeaves

def userQuestion():
    Q1 = "What is your name?"
    Q2 = "What is your employer ID"
    Q3 = "Please provide the leave dates"
    if st.session_state["flow_count"]==1:
        st.session_state['current_flow'] = True
        st.session_state['flow_question'] = Q1
    elif st.session_state["flow_count"]==2:
        st.session_state['flow_question'] = Q2
    elif st.session_state["flow_count"]==3:
        st.session_state['flow_question'] = Q3
    else:
        st.session_state['current_flow'] = False
        st.session_state['flow_question'] = "Leave application sent successfully"
        #resetSessionState()
    return st.session_state['flow_question']

# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        response, total_tokens, prompt_tokens, completion_tokens = Intent_Classification(user_input)
        st.session_state.current_intent = response
        if(st.session_state.current_intent == 'Greetings'):
            output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        elif(st.session_state.current_intent == 'GetLeaves'):
            output = getLeaves() 
            if st.session_state['current_flow']==True:
                output = 'Please prepare the statement for "'+ output +' and '+st.session_state['prev_question'] + '" and give only the context'
            else:
                output = 'Please prepare the statement for "'+ output + '" and give only the context'
            output, total_tokens, prompt_tokens, completion_tokens = generate_response(output) 
        else:
            #output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
            output,total_tokens, prompt_tokens, completion_tokens = 0,0,0,0
            print('output: ',output, 'total_tokens: ',total_tokens, 'prompt_tokens: ',prompt_tokens, 'completion_tokens: ',completion_tokens)            
        #if(st.session_state.current_intent == 'LeaveApplication'):            
            if st.session_state["flow_count"]>0:
                st.session_state['flow_answers'].append(user_input)
            st.session_state["flow_count"] +=1             
            output = userQuestion()
           # output = 'Please prepare the statement for "'+ output + '" and give only the context'
            st.session_state['prev_question'] = st.session_state['flow_question']
            
        
        if st.session_state['current_flow']==False:
            resetSessionState()

        print("Intent Name: ",st.session_state.current_intent)
        print("user_input: ",user_input)
        print("flow_question: ", output)
        print("prev_question",st.session_state['prev_question'])
        print("flow_answers: ", st.session_state['flow_answers'])
        print("flow_count: ",st.session_state["flow_count"])
        
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)

        # from https://openai.com/pricing#language-models
        if model_name == "GPT-3.5":
            cost = total_tokens * 0.002 / 1000
        else:
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000

        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
            #st.write(
                #f"Model used: {st.session_state['model_name'][i]}; Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")
            counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
else:
    st.session_state['generated'] = ['Hi! How can I assist you today? I can help you with applying for leave and viewing your existing leaves.']
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["generated"][i], key=str(i))
            counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
    st.session_state['generated'] = []