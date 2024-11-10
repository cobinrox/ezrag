import sys
import argparse
from . import utils

'''
     Dump config items to menu, allow user to modify them.
     @param old_args not used
     @param oldparser parser previously set up for the program
     @return array of new args that can be applied to another run of the program
'''
def run_menu(old_args, oldparser):
    new_args = oldparser.parse_args()
    new_args_dict = vars(new_args)
    question = new_args.question

    # Define available options for each variable and initialize current_index based on args
    variables = {
        '1': {'name': 'retriever_name',     'options': ['Naive_ST_FAISS_Retriever', 'SimpleRetriever'], 'current_index': 0},
        '2': {'name': 'generator_name',     'options': ['T5SmallGenerator', 'T5BaseGenerator', 'TinyLLmGenerator'], 'current_index': 0},
        '3': {'name': 'chunker_name',       'options': ['Simple_Chunker'], 'current_index': 0},
        '4': {'name': 'chunk_max_num',      'options': [1, 5, 6, 7, 10], 'current_index': 0},
        '5': {'name': 'chunk_size',         'options': [50, 256, 512, 768, 1024], 'current_index': 0},
        '6': {'name': 'chunk_dist_scoring', 'options': ['EUCLIDIAN', 'DOT_PRODUCT', 'COSINE'], 'current_index': 0},
        '7': {'name': 'tempAsStr',          'options': ['NONE', '0.1', '0.2', '0.5', '0.7'], 'current_index': 0},
        '8': {'name': 'docs_dir',           'options': ['docs/security', 'docs/airrag_docs', 'docs/email', 'docs/geography', 'docs/reports', 'docs/wrk', 'NONE'], 'current_index': 0},
        '9': {'name': 'quantize',           'options': ['True', 'False'], 'current_index': 0},
        '10':{'name': 'debug',              'options': ['True', 'False'], 'current_index': 0},
    }

    # Set current_index to match the value in args for each variable
    for key, variable in variables.items():
        arg_value = new_args_dict.get(variable['name'])
        # utils.printf(f"DEBUG checking key [{key}] variable [{variable}] against arg_value [{arg_value}]")
        if arg_value in variable['options']:
            # utils.printf(f"DEBUG match")
            variable['current_index'] = variable['options'].index(arg_value)

    # Menu logic
    while True:
        print("\nCurrent session settings:")
        for key, variable in variables.items():
            current_value = variable['options'][variable['current_index']]
            options_str = ', '.join(map(str, variable['options']))
            print(f"{key} {variable['name']:<15} {current_value:<20} [{options_str}]")
        print("Q " + question)            
        print("D Set docs_dir")
        print("\nR RUN!")
        print("X EXIT")
        print('Select an option by number to rotate its values, "R" to run, "Q" to change the question, "D" to set docs_dir, or "X" to exit.')
        user_input = input("Your choice: ").strip().lower()

        if user_input == 'x':
            # print("Exiting the variable editor. Goodbye!")
            return ["x"]
        elif user_input == 'q':
            question = input("New question: ").strip()
            # print(f"\nUpdated question to: {question}")
            continue  # Rerun the menu with the new question
        elif user_input == 'd':
            new_docs_dir = input("Enter the new docs_dir path: ").strip()
            if new_docs_dir:
                if new_docs_dir in variables['8']['options']:
                    variables['8']['current_index'] = variables['8']['options'].index(new_docs_dir)
                else:
                    variables['8']['options'].append(new_docs_dir)
                    variables['8']['current_index'] = len(variables['8']['options']) - 1
                print(f"docs_dir has been set to: {new_docs_dir}")
            else:
                print(f"No input provided. docs_dir remains as: {variables['8']['options'][variables['8']['current_index']]}")
            continue  # Return to menu after setting docs_dir
        elif user_input == 'r':
            # Build the command-line argument list from the final selected values
            new_args = [f"--{var['name']}={var['options'][var['current_index']]}" for var in variables.values()]
            new_args.append(f"--question={question}")
            return new_args
            break

        if user_input in variables:
            variable = variables[user_input]
            variable['current_index'] = (variable['current_index'] + 1) % len(variable['options'])
            print(f"\nUpdated {variable['name']} to: {variable['options'][variable['current_index']]}")
        else:
            print("Invalid choice. Please enter a valid variable key (e.g., '1', '2', '3'), 'r', 'q', 'd', or 'x'.")

    return question

# example usage
if __name__ == "__main__":
    # Create the parser
    myparser = argparse.ArgumentParser(description="Example parser")
    myparser.add_argument("--retriever_name",     type=str, choices=['Naive_ST_FAISS_Retriever','giraffe','ostritch'], help="Set the retriever type")
    myparser.add_argument("--generator_name",     type=str, choices=['T5SmallGenerator', 'T5BaseGenerator', 'TinyLLmGenerator'], help="Set the generator type")
    myparser.add_argument("--chunker_name",       type=str, default='simle')
    myparser.add_argument("--chunk_size",         type=str, default='512')
    myparser.add_argument("--chunk_dist_scoring", type=str, choices=['EUCLIDIAN', 'DOT_PRODUCT', 'COSINE'], help="Set dbvector search similarity type")
    myparser.add_argument("--tempAsStr",          type=str, choices=['NONE','0.1','0.2','0.5','0.7'], help="Set temperature")
    myparser.add_argument("--docs_dir",           type=str, choices=['docs/security', 'docs/airrag_docs', 'docs/email', 'docs/geography', 'docs/reports', 'docs/wrk', 'NONE'], help="Set docs directory")
    myparser.add_argument("--quantize",           type=str, help="Enable quantization")
    myparser.add_argument("--debug",              type=str, help="Enable debug mode")
    myparser.add_argument("--question",           default="what did the fox say?", help="Set the question")

    old_parsed_args = myparser.parse_args()
    print("\nOld Parsed arguments:")
    print(old_parsed_args)

    # Call the menu function with the parser
    new_args = run_menu(old_parsed_args, myparser)
    if new_args[0].lower() == "x":
        print("Goodbye!")
        sys.exit(0)
    sys.argv = [sys.argv[0]] + new_args  # Replace command-line arguments
    new_parsed_args = myparser.parse_args()
    print("\nNew Parsed arguments:")
    print(new_parsed_args) 
