import ast
import os
from glob import glob
import pathlib

from utils import write_jsonfile, SUMMARIES_PATH
from summary_non_py import get_summary_non_py

def parse_python_file(file_full_path):
    file_content = pathlib.Path(file_full_path).read_text()
    try:
        tree = ast.parse(file_content)
    except Exception as e:
        return file_full_path
    classes = []
    class_to_funcs = {}
    top_level_funcs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            start_lineno = node.lineno
            end_lineno = node.end_lineno
            classes.append((class_name, start_lineno, end_lineno))
            # class_funcs = [
            #     (n.name, n.lineno, n.end_lineno)
            #     for n in ast.walk(node)
            #     if isinstance(n, ast.FunctionDef)
            # ]
            class_funcs=[]
            for no in ast.walk(node):
                if isinstance(no, ast.FunctionDef):
                    function_calls = []
                    for n in ast.walk(no):
                        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                            function_calls.append(n.func.id)
                    class_funcs.append((no.name, no.lineno, no.end_lineno,function_calls))
            class_to_funcs[class_name] = class_funcs

        elif isinstance(node, ast.FunctionDef):
            if len(node.args.args)>0:
                if node.args.args[0].arg=="self":
                    continue
            function_name = node.name
            start_lineno = node.lineno
            end_lineno = node.end_lineno
            function_calls = []
            for n in ast.walk(node):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                    function_calls.append(n.func.id)
            top_level_funcs.append((function_name, start_lineno, end_lineno,function_calls))
        
    return classes, class_to_funcs, top_level_funcs

def find_python_files(dir_path):
    py_files = glob(os.path.join(dir_path, "**/*.py"), recursive=True)
    forbidden_paths=[]
    res = []
    for file in py_files:
        rel_path = file[len(dir_path) + 1 :]
        for p in forbidden_paths:
            if rel_path.startswith(p):
                continue
        res.append(file)
    return res

def find_non_python_files(dir_path):
    code_files = [
        ".md", ".js", ".py", ".c", ".sh", ".ts", ".java", ".cpp", ".hpp", ".cs", 
        ".html", ".htm", ".css", ".rb", ".php", ".pl", ".swift", ".go", ".r", 
        ".m", ".kt", ".scala", ".dart", ".hs", ".lua", ".mm", ".rs", ".yaml", 
        ".yml", ".json", ".xml", ".toml", ".bash"
    ]
    non_code_files = [
        ".img", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".tiff", ".ico", 
        ".webp", ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mp3", 
        ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".pdf", ".doc", ".docx", 
        ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".log", ".task", ".pth", ".npy", 
        ".npz", ".zip", ".tar", ".gz", ".rar", ".7z", ".db", ".sql", ".sqlite", 
        ".mdb", ".exe", ".bat", ".bin", ".com",
        ".py"
    ]
    all_files = glob(os.path.join(dir_path, "**/*"), recursive=True)
    non_python_files = [f for f in all_files if os.path.isfile(f) and not f.endswith(tuple(non_code_files))]
    return non_python_files

def get_code(path,start_line,end_line):
    file_content = pathlib.Path(path).read_text()
    return ''.join(file_content.splitlines(keepends=True)[start_line-1:end_line])

def list_to_json_class(classes, class_funcs,path):
    cls_list=[]
    for cls in classes:
        cls_struct={
            "name":cls[0],
            "summary":"",
            "path":path,
            "type":"class",
            "code":get_code(path,cls[1],cls[2]),
            "class_funcs":{}
        }
        for func in class_funcs[cls[0]]:
            cls_struct["class_funcs"][func[0]]={
                "function_name":func[0],
                "summary":"",
                "code":get_code(path,func[1],func[2]),
                "dependent_functions":func[3]
            }
        cls_list.append(cls_struct)
    return cls_list

def list_to_json_functions(functions,path):
    functions_list=[]
    for func in functions:
        func_struct={
            "name":func[0],
            "summary":"",
            "type":"function",
            "code":get_code(path,func[1],func[2]),
            "path":path,
            "dependent_functions":func[3]
        }
        functions_list.append(func_struct)
    return functions_list

def replace_functions_classes_with_placeholders(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
    tree = ast.parse(file_content)
    functions_and_classes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            functions_and_classes.append(node)
    
    functions_and_classes.sort(key=lambda node: node.lineno)
    lines = file_content.splitlines(keepends=True)
    modified_lines = lines.copy()
    modified_content=""
    for node in functions_and_classes:
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
        
        if isinstance(node, ast.FunctionDef):
            placeholder = f"# Function '{node.name}' defined here\n"
        elif isinstance(node, ast.ClassDef):
            placeholder = f"# Class '{node.name}' defined here\n"
        
        for line in range(start_line, end_line):
            if line == start_line:
                modified_lines[line] = placeholder
            else:
                modified_lines[line] = ''
        modified_content = ''.join(modified_lines)
    return modified_content

def file_json(path):
    file_struct={
        "name":path.split('/')[-1],
        "summary":"",
        "type":"file",
        "code":pathlib.Path(path).read_text(encoding='utf-8', errors='replace'),
        "path":path
    }
    return file_struct

def file_partial_json(path):
    code=replace_functions_classes_with_placeholders(path)
    file_struct={
        "name":path.split('/')[-1],
        "summary":"",
        "type":"file",
        "code":code,
        "path":path
    }
    return file_struct

def json_non_parsable_files(file_paths):
    f_list=[]
    for file_path in file_paths:
        response=get_summary_non_py(file_path)
        # response should we be in list of file_struct format
        # func_struct={
        #     "name":response['name'],
        #     "summary":response['summary'],
        #     "type":response['type'],
        #     "code":response['code'],
        #     "path":file_path,
        #     "dependent_functions":response['dependent_functions']
        # }
        # f_list.append(func_struct)
        f_list+=response
    return f_list

def create_json_files(dir_path):
    py_files=find_python_files(dir_path)
    # print('_'*100)
    # print("Python files in the repo are:")
    # print(py_files)
    # print('_'*100)
    non_py_files=find_non_python_files(dir_path)
    group_list=[]
    for file_path in py_files:
        file_struct=file_json(file_path)
        # file_struct=file_partial_json(file_path)
        try:
            cls, class_funcs, top_level_funcs=parse_python_file(file_path)
        except Exception as e:
            non_py_files.append(file_path)
        classes_list=list_to_json_class(cls, class_funcs,file_path)
        functions_list=list_to_json_functions(top_level_funcs,file_path)
        group_list.append(file_struct)
        group_list+=classes_list
        group_list+=functions_list

    other_list=json_non_parsable_files(non_py_files)
    group_list+=other_list

    print('_'*100)
    print("py-files")
    for file in py_files:
        print(file)
    print('.'*100)
    print("non py-files")
    for file in non_py_files:
        print(file)
    print('_'*100)
    
    write_jsonfile(SUMMARIES_PATH,group_list)