import streamlit as st
import openai,json
import re, warnings
import requests
from bs4 import BeautifulSoup as bs

warnings.filterwarnings("ignore")

try:

    # Read the configuration from config.json
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    # Fetch the OpenAI API key from the configuration
    #openai.api_key = config.get('openai_api_key')
    openai.api_key = st.secrets['API_KEY']
except Exception as e:
        pass 



def get_chunks(url):
    try:
        print('---Getting Chunks---')

        chunk_size = 500
        r = requests.get(url)
        soup = bs(r.text, 'html.parser')
        text = soup.find_all(['h1','p'])
        text = [t.text for t in text]
        blog = ' '.join(text)
        blog = blog.replace('\n', ' ')
        blog = blog.replace('\r', ' ')
        blog = blog.replace('\t', ' ')
        blog = blog.replace('.','.<eos>')
        blog = blog.replace('?','?<eos>')
        blog = blog.replace('!','!<eos>')
        lines = blog.split('<eos>')
        chunks ,cc = [], 0
        for line in lines:
            if len(chunks) == cc+1:
                if len(chunks[cc]) + len(line.split(' ')) <= chunk_size:
                    chunks[cc].extend(line.split(' '))
                else:
                    cc += 1
                    chunks.append(line.split(' '))
            else:
                chunks.append(line.split(' '))
        for i in range(len(chunks)):
            chunks[i] = ' '.join(chunks[i])
        return chunks
    except Exception as e:
        pass 

def get_ncs(chunk):
    try:
        print('---Getting Response---')

        if len(chunk) != 0 or chunk is not None:
            prompt = f"Act as a Legal Compliance Policy Advisor, Check the content in Data against the compliance policy and report the findings. if yes, give me the content regarding that only. Otherwise, don't provide any other info. Don't provide any irrelevant content. \n Data =  {chunk}"
            messages = [{'role':'user','content':prompt}]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = messages,
                temperature = 0.7
            )
            # Extract and display non-compliant results
            non_compliant_results = response.choices
            for response in non_compliant_results:
                content = response['message']['content']
                print(content)

        return content
    except Exception as e:
        print(e)

def get_result(url='https://stripe.com/docs/treasury/marketing-treasury'):
    try:
        print('---Getting Result---')
        chunks = get_chunks(url)
        results = []
        for chunk in chunks:
            res = get_ncs(chunk)
            results.append(res)
        return results
    except Exception as e:
        pass 

st.title("Webpage Compliance Checker")
url = st.text_input("Enter the URL of the webpage")

if url:
    if st.button("Check Compliance"):
        results = get_result(url)
        st.subheader("Non-Compliant Results:")
        st.write(*results)



