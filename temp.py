# from functions_json import find_python_files
# from create_summary import _get_token_length
# from config import dir_path

# py_files=find_python_files(dir_path)
# for file in py_files:
#     start=input('press ENTER:')
#     with open(file,'r') as f:
#         code=f.read()
#     print('_'*100)
#     print(code)
#     print(file)
#     print(_get_token_length(str(code)))
#     print('_'*100)

# from tqdm import tqdm
# from time import sleep

# for i in tqdm(range(10)):
#     sleep(1)
#     print(i)

from create_summary import _get_token_length
import json
path='sos/summaries.json'
# path='test_repo_summ/summaries.json'
with open(path,'r') as f:
    text=json.load(f)
summ=""
for summary in text:
    summ+=summary['summary']
tokens=_get_token_length(summ)
print(tokens)