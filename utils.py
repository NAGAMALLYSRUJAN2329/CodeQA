import json
from openai import OpenAI
import os

from config import DIR_NAME
from apikey import API_KEY

# CLASS_PATH=os.path.join(DIR_NAME,'summaries/new_classes.json')
# FUNCTIONS_PATH=os.path.join(DIR_NAME,'summaries/new_functions.json')
# FILES_PATH=os.path.join(DIR_NAME,'summaries/new_files.json')
SUMMARIES_PATH=os.path.join(DIR_NAME,'summaries.json')
REPO_SUMMARY_PATH=os.path.join(DIR_NAME,'summary.txt')
EMBEDDINGS_PATH=os.path.join(DIR_NAME,'embeddings.npy')

# os.makedirs(os.path.dirname(CLASS_PATH), exist_ok=True)
# os.makedirs(os.path.dirname(FUNCTIONS_PATH), exist_ok=True)
# os.makedirs(os.path.dirname(FILES_PATH), exist_ok=True)
os.makedirs(os.path.dirname(SUMMARIES_PATH), exist_ok=True)
os.makedirs(os.path.dirname(REPO_SUMMARY_PATH), exist_ok=True)
os.makedirs(os.path.dirname(EMBEDDINGS_PATH), exist_ok=True)

def write_jsonfile(path,content):
    with open(path,'w') as f:
        json.dump(content,f)

def file_read(path):
    with open(path,'r') as f:
        content=json.load(f)
    return content

client = OpenAI(api_key = API_KEY)  
def llm(prompt,system="you are a helpful assistant"):
    completion = client.chat.completions.create(
        # model="gpt-4-turbo",
        model = "gpt-4o",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )
    return(completion.choices[0].message.content)