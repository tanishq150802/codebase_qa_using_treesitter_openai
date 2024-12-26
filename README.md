# codebase_qa_using_treesitter_openai

### Query your codebase using tree-sitter and GPT-4

By: [Tanishq Selot](https://github.com/tanishq150802)  

Refer to ```setup.py``` for querying your codebase and saving the responses in the ```output``` folder. 
Edit the ```context``` variable and the list ```questions``` for putting your own questions.

Refer to ```tree_sitter_setup.py``` for the logic used to convert the tree-sitter tree information into
JSON format as stored in ```AST.json```. ```.env``` should contain the OPENAI_API_KEY for accessing gpt models.

## Approach
* Tree sitter is used to parse the code files present in the ```codebase``` directory and create a tree.
* For extracting classes, functions and imports, we traverse through the tree by using ['tree-sitter' queries](https://tree-sitter.github.io/tree-sitter/using-parsers#pattern-matching-with-queries) which identifiers for each component, starting with root node. 
* The extracted classes, functions and imports are stored in JSON file.
* This JSON file is given as context to gpt-4 with instructions about how to interpret JSON data and answer the questions.
* The answers to all the questions are stored as a single string which is then processed to create different JSON files containing question-answer pairs.

## Steps
Create a virtual environment and install the below requirements. Run ```tree_sitter_setup.py``` to create the tree as JSON like ```AST.json``` after changing the codebase directory path. 

Then run ```setup.py``` to answer your queries and saving the responses in ```output``` folder.

## Requirements
* python==3.12
* openai==1.54.4
* tree-sitter==0.23.2
* tree-sitter-python==0.23.4
* python-dotenv==1.0.1
