import sys
import argparse
from . import utils

'''
     Dump config items to menu, allow user to modify them.
     @param old_args not used
     @param oldparser parser previously set up for the program
     @return array of new args that can be applied to another run of the program
'''
def run_menu(old_args,oldparser ):
    # get oldparser args
    #old_args = oldparser.parse_args(['--foo', 'value1', '--bar', 'value2'])
    #old_args_dict = {f'--{arg}': str(value) for arg, value in vars(old_args).items() if value is not None}

    new_args = oldparser.parse_args()
    new_args_dict = vars(new_args)
    question = new_args.question
    # Define available options for each variable and initialize current_index based on args
    variables = {

        '1': {'name': 'retriever_name',     'options': ['Naive_ST_FAISS_Retriever','SimpleRetriever'], 'current_index': 0},
        '2': {'name': 'generator_name',     'options': ['T5SmallGenerator', 'TinyLLmGenerator'],       'current_index': 0},
        '3': {'name': 'chunker_name',       'options': ['Simple_Chunker'],                             'current_index': 0},
        '4': {'name': 'chunk_max_num',      'options': [1,5,6,7,10],                                   'current_index': 0},
        '5': {'name': 'chunk_size',         'options': [50, 256, 512, 768, 1024],                      'current_index': 0},

        '6': {'name': 'chunk_dist_scoring', 'options': ['EUCLIDIAN', 'DOT_PRODUCT', 'COSINE'],         'current_index': 0},
        '7': {'name': 'tempAsStr',          'options': ['NONE','0.1','0.2','0.5','0.7'],               'current_index': 0},

        '8': {'name': 'docs_dir',           'options': ['docs/security','docs/airrag_docs','docs/email','docs/geography','docs/reports','docs/wrk','NONE'], 'current_index': 0},
        '9': {'name': 'quantize',           'options': ['True','False'],                               'current_index': 0},
        '10':{'name': 'debug',             'options': ['True','False'],                               'current_index': 0},



    }

    # Set current_index to match the value in args for each variable
    for key, variable in variables.items():
        arg_value = new_args_dict.get(variable['name'])
        #utils.printf(f"DEBUG checking key [{key}] variable [{variable}] against arg_value [{arg_value}]")
        if arg_value in variable['options']:
            #utils.printf(f"DEBUG match")
            variable['current_index'] = variable['options'].index(arg_value)

    # Menu logic
    while True:
        print("\nCurrent session settings:")
        for key, variable in variables.items():
            current_value = variable['options'][variable['current_index']]
            options_str = ', '.join(map(str, variable['options']))
            print(f"{key} {variable['name']:<15} {current_value:<20} [{options_str}]")
        print("Q " + question)            
        print("\nR RUN!")
        print("X EXIT")
        #print("\nChoose a variable to change (e.g., '1' for temperature), type 'r' to run, or 'q' to exit:")
        print('Select an option by number to rotate its values, "R" to run, or "X" to exit.')
        user_input = input("Your choice: ").strip().lower()

        if user_input == 'x':
            #print("Exiting the variable editor. Goodbye!")
            return ["x"]
        elif user_input == 'q':
            question = input("New question: ").strip()
            #print(f"\nUpdated question to: {question}")
            continue  # Rerun the menu with the new question
            
        elif user_input == 'r':
            # Build the command-line argument list from the final selected values
            new_args = [f"--{var['name']}={var['options'][var['current_index']]}" for var in variables.values()]
            new_args.append(f"--question={question}")

            #merged_args_dict = {**old_args_dict, **new_args_dict}

            # Convert merged dictionary back to a list of arguments
            #mergedArgs = [item for pair in merged_args_dict.items() for item in pair]

            return new_args
            #return mergedArgs #new_args
            #sys.argv = [sys.argv[0]] + args  # Replace command-line arguments

            # print("\nModified command-line arguments:")
            # print(' '.join(sys.argv))

            # # Parse the new command-line arguments and show them
            # parsed_args = myparser.parse_args()
            # print("\nParsed arguments:")
            # print(parsed_args)

            break

        if user_input in variables:
            variable = variables[user_input]
            variable['current_index'] = (variable['current_index'] + 1) % len(variable['options'])
            print(f"\nUpdated {variable['name']} to: {variable['options'][variable['current_index']]}")
        else:
            print("Invalid choice. Please enter a valid variable key (e.g., '1', '2', '3'), 'r', or 'x'.")
    return question

# example usage
if __name__ == "__main__":
    # Create the parser
    myparser = argparse.ArgumentParser(description="Example parser")
    myparser.add_argument("--retriever_name",     type=str, choices=['Naive_ST_FAISS_Retriever','giraffe','ostritch'], help="Set the retriver type")
    myparser.add_argument("--generator_name",     type=str, choices=['T5SmallGenerator', 'TinyLLmGenerator']         , help="Set the generator type")
    myparser.add_argument("--chunker_name",       type=str, default='simle')
    myparser.add_argument("--chunk_size",       type=str, default='512')


    myparser.add_argument("--chunk_dist_scoring", type=str, choices=['EUCLIDIAN', 'DOT_PRODUCT', 'COSINE']           , help="Set dbvector search similarty type")
    myparser.add_argument("--tempAsStr",        type=str, choices=['NONE','0.1','0.2','0.5','0.7']                 , help="Set temp")
    myparser.add_argument("--docs_dir",           type=str, choices=['docs/security', 'docs/email', 'docs/geography', 'docs/reports', 'docs/wrk', 'NONE']           , help="Set dbvector search similarty type")
    myparser.add_argument("--quantize",           type=str,  help="Set dbvector search similarty type")
    myparser.add_argument("--debug",           type=str, help="Set dbvector search similarty type")

    myparser.add_argument("--question", default="what did the fox say?")    
    old_parsed_args = myparser.parse_args()
    print("\nOld Parsed arguments:")
    print(old_parsed_args)


    # Call the menu function with the parser
    new_args = run_menu(old_parsed_args,myparser)
    if( new_args[0] == "x"):
        print("bubbye")
        sys.exit(0)
    sys.argv = [sys.argv[0]] + new_args  # Replace command-line arguments
    new_parsed_args = myparser.parse_args()
    print("\nNew Parsed arguments:")
    print(new_parsed_args)