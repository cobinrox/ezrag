import os
import subprocess
import sys
import time
import threading
import inspect
import pprint
from types import ModuleType
import numpy as np
import psutil

# re-usable global for setting a start time, useful
# for debugging
g_start_time = 0

'''
     Prompt for and get a 'rating', a number between 1 and 5
'''
def get_rating():
    while True:
        try:
            # Prompt the user with a default value of 3
            rating = input("Rate this answer from 1 (bad) to 5 (good): ") or "3"
            
            # Convert the rating to an integer and validate the range
            rating = int(rating)
            if 1 <= rating <= 5:
                return rating
            else:
                print("Please enter a whole number between 1 and 5.")
        except ValueError:
            #print("Invalid input. Please enter a whole number between 1 and 5.")
            pass

# strip of cr/lf chars from a string
def remove_cr_lf(text: str) -> str:
  return text.replace('\r', '').replace('\n', '')

# save a string, assumed to be a csvstring, to a file, if the file already
# exists, then the header is NOT printed to the file first
# @param header csv string header to print to the top of the file
# @param csvStr the string to print
# @param filename the file name to write the string to
# 
def save_csv(header, csvStr, fileName):
    directory = os.path.dirname(fileName)
    abs_dir_name = os.path.abspath(directory)
    if not os.path.exists(abs_dir_name):
        print(f"Created dir [{abs_dir_name}]")
        os.makedirs(abs_dir_name)

    with open(fileName, 'a+') as f:
        # Check if the file is empty (i.e., no header)
        f.seek(0, 2)  # Move the file pointer to the end
        if f.tell() == 0:
            # Prepend "TIME_MS" to the header
            f.write(f"TIME_MS,{header}\n")

        current_time_ms = int(round(time.time() * 1000))
        row_data = f"{current_time_ms},{csvStr}\n"  # Prepend timestamp to row data
        f.write(row_data)

# convert a path to absolute path
def to_absolute_path(path_str):
    # Convert the input string to an absolute path
    return os.path.abspath(path_str)

'''
    Returns a string with the first x characters, an ellipsis,
    the last x characters, and the total length of the string in parentheses.
    @param str: The input string.
    @param x: The number of characters to display from the beginning and end.
    @return string in the specified format.
'''
def first_x_last_x_chars(str, x):
  if len(str) <= 2 * x:
    return str
  else:
    return f"{str[:x]}...{str[-x:]}({len(str)})"
'''
   Truncate a number to specified num of decimal pts
   @param val number to truncate
   @param n number of max decimal places for output
   @return truncated number, as a string
'''
def dec_pts(val, n):
  return f"{val:.{n}f}"

def get_current_time_ms():
    return int(round(time.time() * 1000))

# save off the current time in a global and
# print out a message
def print_start_msg(msg) :
  global g_start_time
  g_start_time = time.perf_counter()
  printf(msg)

# print out a message and include the current time
# minus the global start time that was saved when
# using the print_start_msg
def print_stop_msg(msg) :
  printExecutionTime(msg)

# method to set g_start_time to now
def set_g_start_time() :
  global g_start_time
  g_start_time = time.perf_counter()


# method to print out length of time it took to peform an operaion
# @param msg string specifying the operation whose time is to be printed out
# Uses g_start_time as assumed starting time
# example usage:
# g_start_time = time.perf_counter()
# do_some_long_running_operation()
# printTime("ate a sammich")
# the print out will look similar to:
# "     ate a sammich took [xxxxy] secs"
# @returns returns num seconds an operation took, to 3 decimal places
def printExecutionTime(msg):
    global g_start_time

    # Calculate the time difference
    time_elapsed = round(time.perf_counter() - g_start_time, 3)

    # Print the message using the time_elapsed variable
    printf(f"     {msg} took [{time_elapsed:.3f}] secs")

    # Return the time_elapsed value
    return time_elapsed

# method to print a string, flushing the output
# @param msg string to print out
def printf(msg):
    current_thread_name = threading.current_thread().name
    memUsage = f"{psutil.Process().memory_info().rss / (1024*1024):.2f} MB"
    caller_filename = get_true_caller()
    if caller_filename == None:
        abbreviated_filename = ""
    else:
        abbreviated_filename = abbreviate_path(caller_filename)

    print("[" + str((int)(time.time() * 1000)) + "] [" + current_thread_name + "] ["+memUsage+"] [" + abbreviated_filename + "]" + str(msg),flush=True)

'''
    Take a filepath and shorten it, useful for printing out a file path to
    log messages without cluttering up the screen.
'''
def abbreviate_path(filepath):
    # Split the path into components
    components = filepath.split(os.sep)
    
    # Abbreviate all components except the last one (the script name)
    abbreviated_components = [comp[0] if i < len(components) - 1 else comp for i, comp in enumerate(components)]
    
    # Join the components back into a single path
    abbreviated_path = os.sep.join(abbreviated_components)
    
    return abbreviated_path

# used internally to get caller of method, use for printing
# info to logs
def get_true_caller():
    # Traverse the stack to find the first caller that's not from utilities.py
    for frame_info in inspect.stack():
        filename = frame_info.filename
        # Skip any frames that are inside this utilities module
        if "utils.py" not in filename:
            return filename
    return None  # In case no external caller is found


# dump basic info about object
def printObj(val, maxlines=100, max_depth=5):
    class LineCounterWriter:
        def __init__(self, maxlines):
            self.maxlines = maxlines
            self.line_count = 0
            self.truncated = False

        def write(self, s):
            lines = s.split('\n')
            for line in lines:
                if self.line_count < self.maxlines:
                    print(line)
                    self.line_count += 1
                else:
                    self.truncated = True
                    return

        def flush(self):
            pass

    def safe_repr(obj, depth=0):
        if depth > max_depth:
            return "..."
        if isinstance(obj, ModuleType):
            return f"<module '{obj.__name__}'>"
        if isinstance(obj, (list, tuple, set, frozenset)):
            type_name = type(obj).__name__
            return f"{type_name}([{', '.join(safe_repr(x, depth+1) for x in list(obj)[:10])}{'...' if len(obj) > 10 else ''}])"
        if isinstance(obj, dict):
            items = list(obj.items())[:10]
            return f"dict({{{'...' if len(obj) > 10 else ''}{', '.join(f'{safe_repr(k, depth+1)}: {safe_repr(v, depth+1)}' for k, v in items)}}}"
        return repr(obj)

    line_counter = LineCounterWriter(maxlines)
    original_stdout = sys.stdout
    sys.stdout = line_counter

    try:
        pprint.pprint(val, stream=line_counter, depth=max_depth, compact=False, width=80, sort_dicts=False, underscore_numbers=True)
    except RecursionError:
        print("RecursionError: Object is too deeply nested. Using custom repr.")
        print(safe_repr(val))
    except Exception as e:
        print(f"Error while printing: {e}")

    sys.stdout = original_stdout

    if line_counter.truncated:
        print("... and there's more!")

# check that a directory does indeed exist
def ensure_directory_exists(an_abs_file_or_dir):
    # Check if the given path is a directory or a file
    if os.path.isdir(an_abs_file_or_dir):
        # If it's a directory, ensure it exists
        directory_path = an_abs_file_or_dir
    else:
        # If it's a file, get the directory part of the path
        directory_path = os.path.dirname(an_abs_file_or_dir)

    # Create the directory if it does not exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory created: {directory_path}")
    else:
        print(f"Directory already exists: {directory_path}")


'''
    Convert an array of cosine similarity scores to a percentage.
    @param scores (list or np.ndarray): Array of cosine similarity scores.
    @return list: Array of percentage scores.
'''
def convert_cosine_similarity_to_percentage(scores):

    # Ensure input is a numpy array for easier operations
    scores = np.array(scores)
    
    # Normalize the scores to range from 0 to 100
    # Map the range of -1 to 1 to 0 to 100
    normalized_scores = (scores + 1) / 2  # Shift range from [-1, 1] to [0, 1]
    percentage_scores = normalized_scores * 100  # Scale to [0, 100]
    
    return percentage_scores.tolist()

'''
    Convert an array of dot product similarity scores to a percentage.
    @param scores (list or np.ndarray): Array of dot product similarity scores.
    @return list: Array of percentage scores.
'''
def convert_dot_product_to_percentage(scores):
    # Ensure input is a numpy array for easier operations
    scores = np.array(scores)
    
    # Normalize the scores to range from 0 to 100
    min_score = scores.min()
    max_score = scores.max()
    
    if max_score - min_score == 0:
        return [100] * len(scores)  # All scores are the same
    
    normalized_scores = (scores - min_score) / (max_score - min_score)
    percentage_scores = normalized_scores * 100
    
    return percentage_scores.tolist()   

'''
    Convert an array of Euclidean similarity scores to a percentage.
    @param scores (list or np.ndarray): Array of Euclidean similarity scores.
    @return list: Array of percentage scores.
'''
def convert_euclidean_to_percentage(scores):
    # Ensure input is a numpy array for easier operations
    scores = np.array(scores)
    
    # Invert scores because lower Euclidean distances indicate better matches
    inverted_scores = 1 / (1 + scores)
    
    # Normalize the inverted scores to range from 0 to 100
    min_score = inverted_scores.min()
    max_score = inverted_scores.max()
    
    if max_score - min_score == 0:
        return [100] * len(inverted_scores)  # All scores are the same
    
    normalized_scores = (inverted_scores - min_score) / (max_score - min_score)
    percentage_scores = normalized_scores * 100
    
    return percentage_scores.tolist()  

# Example usages
if __name__ == "__main__":
    euclidean_scores = [0.93, 1.24, 1.30, 1.52, 1.76]
    percentage_scores = convert_euclidean_to_percentage(euclidean_scores)
    print(percentage_scores)

    cosine_scores = [0.5339851 , 0.37814558 ,0.35027722, 0.24068423, 0.11972722]
    percentage_scores = convert_cosine_similarity_to_percentage(cosine_scores)
    print(percentage_scores)    

    dot_product_scores = [0.53, 0.38, 0.35, 0.24, 0.12]
    percentage_scores = convert_dot_product_to_percentage(dot_product_scores)
    print(percentage_scores)