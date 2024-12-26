from openai import OpenAI
import os
import re
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

instruction = """You are a helpful assistant. You will be provided with JSON data delimited 
by triple quotes and a few questions. Your task is to answer the questions using only the provided 
JSON data. The JSON data will include information related to various python functions and 
classes used in the .py files contained within a codebase. If the JSON data does not contain the information needed to answer the question 
then simply write: "Insufficient information".

Two functions are called 'related' if one of the functions is called inside the other function. The 
number of related functions for each function corresponds to the number of functions present in the 
"related_functions" list of the given function.

The format of the JSON data is similar to a python dictionary and is described below. 
Here, each string value corresponding to a key denotes the key's description.

{
    "python_file_name.py": {
        "imports": [
            "import statements"
        ]
        "classes": [
            {
                "class_name": "Name of the class",
                "methods": [
                    {
                        "name": "Name of first method",
                        "parent": "Name of class",
                        "parameters": "Parameters of the first method as tuple",
                        "summary": "short description of the first method",
                        "children": "children of first method as list"
                    },
                    {
                        "name": "Name of second method",
                        "parent": "Name of class",
                        "parameters": "Parameters of the second method as tuple",
                        "summary": "short description of the second method",
                        "children": "children of second method as list"
                    }
                ],
                "children": "list of derived class names"
            }
        ],
        "functions": [
            {
                "name": "Name of the function",
                "parent": "name of the parent of the function",
                "parameters": "parameters of the functions as tuple",
                "summary": "short description of the function",
                "children": "list of children of the function",
                "related_functions": "list of related functions of the function"
            }
        ]
    }
}

"""

f = open('AST.json')
data = json.load(f)
f.close()

context = f"""
The JSON data to be used for answering the questions is as follows:

{json.dumps(data, indent=4)}

Based on the JSON data, answer the below question(s).

1. What functions does api.py have?
2. What are different classes present in api.py?
3. How many imports are present in app.py?
4. How many function are related in each of app.py and api.py?

"""

completion = client.chat.completions.create(
    model="gpt-4",
    seed=0,
    temperature=0,
    messages=[
        {"role": "system", "content": instruction},
        {
            "role": "user",
            "content": context
        }
    ]
)

response = completion.choices[0].message.content

questions = [
    "What functions does api.py have?",
    "What are different classes present in api.py?",
    "How many imports are present in app.py?",
    "How many function are related in each of app.py and api.py?",
]

answers = re.split(r'\d+\.\s+', response.strip())[1:]

for i in range(len(questions)):

    data = {"question": questions[i], "answer": answers[i]}
    # print(questions[i] + '\n')
    # print(answers[i] + '\n\n')

    filename = f"question_{i+1}.json"

    file_path = os.path.join("output", filename)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Saved: {file_path}")

