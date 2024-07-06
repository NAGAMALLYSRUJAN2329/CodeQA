# from create_summary import generate_summary
from utils import llm
import pathlib
# def get_summary_non_py(file_path):
#     response={
#         "name":file_path.split('/')[-1],
#         "summary":"",
#         "code":pathlib.Path(file_path).read_text(encoding='utf-8', errors='replace'),
#         "type":"file",
#         "dependent_functions":[]
#     }
#     # system="""
#     # You are the best code summarizer present here. You are given a code of a file and your task is to summarize the file in the json format given below.

#     # """
#     # prompt=f"The code is:\n {code}"
#     # ans=llm(prompt,system)
#     response["summary"]=generate_summary(response['code'],len=200)
#     return [response]

def get_summary_non_py(file_path):
    # system = """
    # You are the best code summarizer present here. You are given a file and your task is to summarize the whole file given as well as the functions/classess/modules present in it separately as well.The output should be in the following format:
    # the summarries of each kind must be inside the summary tag <summary></summary>. Inside the summary tag you should give the name of the class/function/module inside the <name></name> tag , the type that is class/function/module you are generating  
    # """
    system = """
    You are a good code summarizer. Given an input file which has code your task is to summarize what each function/class is resposible for separately as well as generate the summary of the whole file so that this summary can be used to refer to for code suggesstions and doubt solving.The summary you create should be such that it contains every detail from a coding point of view as this will be refered later for code suggestions.
    For each function/class/file you should output its metadata inside the <element>/element> tag. Inside the element tag you should write the name of the class/function inside the <name></name> tag , its type (function/class/file) inside the <type></type> tag , its summary inside the <summary></summary> tag, the code of the function/class inside the <code></code> tag , and the functions/classes the function is dependent on which is not defined in it inside the <dependent></dependent> tag (if it is not dependent , the dependent tag should contain the word null).
    There must be compulsorily a file summary for every file.For the file summary , make its type file inside the <type> tag and its code tag should just contain the letter code.

    For example of the variable summary refer this:

    The code is :
    def add_two_number(first_number , second_number):
        return first_number + second_number
    def display_client_name (client_name):
        print("Good Morning " , client name)

    the output should be :
    <element> <name>add_two_numbers</name> <type>function</type> <summary>This function takes in two numbers first_number and second_number as input and the returns their sum</summary>  <code> def add_two_number(first_number , second_number):    return first_number + second_number </code> <dependent>null</dependent></element>

    <element> <name>display_client_name</name> <type>function</type> <summary>This function takes in client_name as input and then greets the the client by saying good morning and then client_name</summary>  <code> def display_client_name (client_name):    print("Good Morning " , client name) </code> <dependent>null</dependent>  </element>

    <element> <name>example.py</name> <type>file</type> <summary> summary of the file </summary> <code> code </code> <dependent>null</dependent> </element>
    """
    code = pathlib.Path(file_path).read_text(encoding='utf-8', errors='replace')
    prompt = f"The code is {code}"
    # elements = []
    elements = llm ( prompt , system)
    # return code , elements
    elements = elements.split("<element>")
    elements = elements[1:]
        
    response=[]
    for element in elements:
            if element.strip(): 
                    name = element.split("<name>")[1].split("</name>")[0].strip()
                    elem_type = element.split("<type>")[1].split("</type>")[0].strip()
                    description = element.split("<summary>")[1].split("</summary>")[0].strip()
                    code_func = element.split("<code>")[1].split("</code>")[0].strip()
                    dependent = element.split("<dependent>")[1].split("</dependent>")[0].strip()
                    
                    if dependent == "null" :
                        dependent = ""

                    if (elem_type == "file"):
                        response.append({
                        "name": name,
                        "type": elem_type,
                        "summary": description,
                        "path": file_path,
                        "code" : code,
                        "dependent_functions" : dependent.split(',')
                    })
                    
                    else:
                        response.append({
                        "name": name,
                        "type": elem_type,
                        "summary": description,
                        "path": file_path , 
                        "code" : code_func,
                        "dependent_functions" : dependent.split(',')
                    })

    # response should we be in list of file_struct format
    # func_struct={
    #     "name":"",
    #     "summary":"",
    #     "type":"",
    #     "code":"}",
    #     "path":file_path,
    #     "dependent_functions":[]
    # }
    # response.append(file_struct)

    return response