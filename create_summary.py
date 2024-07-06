from tqdm import tqdm

from utils import llm, file_read, write_jsonfile, SUMMARIES_PATH, REPO_SUMMARY_PATH

def generate_summary(code,len=50):
    system_prompt=f"""
    You are a good code summarizer. Given a code, your task is to summarize what the code do in less than {len} words so that this summary can be used to refer to for code suggesstions and doubt solving.The summary you create should be such that it contains every detail from a coding point of view as this will be refered later for code suggestions.
    Generate your summary between <summary>...</summary> tags.
    """
    prompt = f"The code you need to summarise is: \n{code}"
    response=llm(prompt,system_prompt)
    response=response.split('<summary>')[-1].split('</summary>')[0]
    return response

def _get_token_length(input_text):
    import tiktoken
    tokenizer = tiktoken.get_encoding('cl100k_base')
    tokens = tokenizer.encode(input_text,disallowed_special=())
    num_tokens = len(tokens)
    return num_tokens

def get_token_length():
    f_list=file_read(SUMMARIES_PATH)
    text=""
    for func in f_list:
        if func['summary']=="":
            system_prompt=f"""
            You are a good code summarizer. Given a code, your task is to summarize what the code do in less than 50 words so that this summary can be used to refer to for code suggesstions and doubt solving.The summary you create should be such that it contains every detail from a coding point of view as this will be refered later for code suggestions.
            Generate your summary between <summary>...</summary> tags.
            """
            text+=system_prompt+"The code you need to summarise is: \n"+ func['code']
    num_tokens=_get_token_length(text)
    return (num_tokens,len(f_list)*52)

def generate_summaries():
    f_list=file_read(SUMMARIES_PATH)
    for func in tqdm(f_list):
        # print(f"Generating summary for {func['name']}")
        if func['type']=="file":
            func['summary']=generate_summary(func['code'],len=200)
        else:
            func['summary']=generate_summary(func['code'])
    write_jsonfile(SUMMARIES_PATH,f_list)

def repo_summary():
    f_list=file_read(SUMMARIES_PATH)
    summary = ""
    for element in f_list:
        name = element['name']
        summary = element['summary']
        type = element['type']
        try :
            dependent_functions = element['dependent_functions']
        except Exception as e :
            dependent_functions = "null"
        path = element['path']
        summary += f"The name of the file is {name}. Its type is {type}. Its path is {path}. Its dependant functions are {dependent_functions}. Its summary is {summary}. "
    
    prompt=f"The summaries of all the files are : {summary}"
    system_prompt="""You are a good code summarizer. Given summaries of all file in a repository , your task is to create an overall summary using all these summaries. This summary will be used for question answering about the code and code improvements , so build the summary accordingly.
    Generate your summary between <summary>...</summary> tag."""
    summary=llm(prompt,system_prompt)
    summary=summary.split('<summary>')[-1].split('</summary>')[0]
    with open(REPO_SUMMARY_PATH,'w') as f:
        f.write(summary)