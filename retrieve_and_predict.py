from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import json
import openai
import annoy
import os
import tiktoken

from utils import file_read, llm, API_KEY, SUMMARIES_PATH, EMBEDDINGS_PATH

class Sentence_Embedding:
    def __init__(self,model_name):
        self.model=SentenceTransformer(model_name)
    def encode(self,query):
       return self.model.encode(query)

class Openai_Embedding:
    def __init__(self):
        self.client=openai.OpenAI(api_key=API_KEY)
    def encode(self,query):
        response=self.client.embeddings.create(
            input=query,
            model="text-embedding-3-large"
        )
        embeddings=[]
        for emb in response.data:
            embeddings.append(emb.embedding)
        return np.array(embeddings)

class Faiss_Retriever:
    def __init__(self,data,embedding_model,k):
        self.k=k
        self.embedding_model=embedding_model
        self.doc_emb=embedding_model.encode(data)
        self.index = faiss.IndexFlatL2(self.doc_emb.shape[1])
        self.index.add(self.doc_emb)
    def retrieve(self,query):
        if type(query)==str:
            query=[query]
        query_vec=self.embedding_model.encode(query)
        D, I = self.index.search(query_vec, self.k)
        return I[0]
class ANN:
    def __init__(self,data,embedding_model,k,method='angular',ann_depth=10):
        self.k=k
        self.embedding_model=embedding_model
        if os.path.exists(EMBEDDINGS_PATH):
            print('Using previously generating embeddings')
            self.doc_emb=np.load(EMBEDDINGS_PATH)
        else:
            print('Generating fresh embeddings')
            self.doc_emb=embedding_model.encode(data)
            np.save(EMBEDDINGS_PATH,self.doc_emb)
        self.index = annoy.AnnoyIndex(self.doc_emb[0].shape[0], method)
        for i, vector in enumerate(self.doc_emb):
            self.index.add_item(i, vector)
        self.index.build(ann_depth)
    def retrieve(self,query):
        if type(query)==str:
            query=[query]
        query_vec=self.embedding_model.encode(query)
        nearest_neighbors_idx = self.index.get_nns_by_vector(query_vec[0], self.k)
        return nearest_neighbors_idx


def predict(query,functions):
    system=f"""
    You are an agent who has an good ability to understand the code and you task is to solve the user query about his doubt in the code base and given the code and summary of some of the relevant functions which you can refer to for answering the given query, be precise and concise while answering and don't generate answer too long.
    ```functions
    {json.dumps(functions)}
    ```
    """
    prompt=f"""The query is {query}"""
    llm_response=llm(prompt,system)
    return llm_response

def prediction(query,args):
    (retriever,f_list,file_names)=args
    idxs=retriever.retrieve(query)
    functions=[]
    print('_'*100)
    print("RETRIEVED THINGS")
    for idx in idxs:
        functions.append(f_list[idx])
        print(file_names[idx])
    print('_'*100)
    llm_response=predict(query,functions)
    return llm_response

def truncate_data(data,max_tokens=8000):
    new_data=[]
    for d in data:
        tokenizer = tiktoken.get_encoding('cl100k_base')
        tokens = tokenizer.encode(d,disallowed_special=())
        if(len(tokens)>max_tokens):
            tokens=tokens[:max_tokens]
        new_data.append(tokenizer.decode(tokens))
    return new_data

def create_retriever():
    f_list=file_read(SUMMARIES_PATH)
    descriptions=[]
    for func in f_list:
        if func['type']=='class':
            # descriptions.append(f"name:{func['name']} summary:{func['summary']} code:{func['code']} class_functions:{json.dumps(func['class_funcs'])}")
            descriptions.append(f"name:{func['name']} summary:{func['summary']} code:{func['code']}")
        elif func['type']=='function':
            # descriptions.append(f"name:{['name']} summary:{func['summary']} code:{func['code']} dependent_functions:{str(func['dependent_functions'])}")
            descriptions.append(f"name:{func['name']} summary:{func['summary']} code:{func['code']}")
        else:
            descriptions.append(f"name:{func['name']} summary:{func['summary']} code:{func['code']}")
        file_names=[f"{f['path']}, {f['name']}, {f['type']}"for f in f_list]
    
    embedding_model=Openai_Embedding()
    # embedding_model=Sentence_Embedding("BAAI/bge-large-en-v1.5")
    descriptions=truncate_data(descriptions)
    retriever=ANN(descriptions,embedding_model,k=5)
    return (retriever,f_list,file_names)