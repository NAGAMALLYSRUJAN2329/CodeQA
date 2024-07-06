from functions_json import create_json_files
from create_summary import generate_summaries, get_token_length, repo_summary
from retrieve_and_predict import prediction, create_retriever
from config import dir_path

def initialize_dir(dir_path):
    ans=input("Enter 'yes' to create the fresh json files otherwise just press enter: ")
    if ans.lower()=='yes':
        print('Generating json files...')
        create_json_files(dir_path)
        print('Completed')
    tokens=get_token_length()
    print(f"Number of tokens needed to generate the summary are:")
    print(f"input_tokens:{tokens[0]}")
    print(f"output_tokens:{tokens[1]}")
    ans=input("Enter 'yes' to generate summaries otherwise just press enter: ")
    if ans.lower()=='yes':
        print('Generating summaries...')
        generate_summaries()
        print('Completed')
    ans=input("Enter 'yes' to generate summary of the whole repo otherwise just press enter: ")
    if ans.lower()=='yes':
        print('Generating summary of the repo...')
        repo_summary()
        print('Completed! Summary generated in the specified path (summary.txt)')

def predict(query):
    response=prediction(query,retriever)
    return response

if __name__ =="__main__":
    initialize_dir(dir_path)
    retriever=create_retriever()
    while True:
        print("\n")
        print('_'*100)
        query=input('Enter your query:')
        if query!='q':
            answer=predict(query)
            print(answer)
        else:
            print('Exiting...')
            break

# some user queries for sos
# which .py file should i check to see where do I remove the check whether server is registered on db or not
# which file can allocate a model to a GPU based on the availability
# where do I remove the check whether server is registered on db or not while registering the model mappings
# where do i see if a given server is down

# some user queries for heimdall
# where do i change my prepaid rate limits
# increase the free credits rate limiter to 50
# find prepaid_limiter function