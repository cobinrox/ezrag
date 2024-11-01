import os
import subprocess
import sys
import time
import threading
import inspect
import pprint
from types import ModuleType
import csv

# re-usable global for setting a start time, useful
# for debugging
g_start_time = 0

def remove_cr_lf(text: str) -> str:
  return text.replace('\r', '').replace('\n', '')

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

def to_absolute_path(path_str):
    # Convert the input string to an absolute path
    return os.path.abspath(path_str)

def dec_pts(val, n):
  """
  Truncates a number to a specified number of decimal points.

  Args:
    val: The number to truncate.
    n: The number of decimal points to retain.

  Returns:
    The truncated number as a string.
  """
  return f"{val:.{n}f}"


def print_start_msg(msg) :
  global g_start_time
  g_start_time = time.perf_counter()
  printf(msg)

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

    caller_filename = get_true_caller()
    if caller_filename == None:
        abbreviated_filename = ""
    else:
        abbreviated_filename = abbreviate_path(caller_filename)

    print("[" + str((int)(time.time() * 1000)) + "] [" + current_thread_name + "] [" + abbreviated_filename + "]" + str(msg),flush=True)

def abbreviate_path(filepath):
    # Split the path into components
    components = filepath.split(os.sep)
    
    # Abbreviate all components except the last one (the script name)
    abbreviated_components = [comp[0] if i < len(components) - 1 else comp for i, comp in enumerate(components)]
    
    # Join the components back into a single path
    abbreviated_path = os.sep.join(abbreviated_components)
    
    return abbreviated_path

def get_true_caller():
    # Traverse the stack to find the first caller that's not from utilities.py
    for frame_info in inspect.stack():
        filename = frame_info.filename
        # Skip any frames that are inside this utilities module
        if "utils.py" not in filename:
            return filename
    return None  # In case no external caller is found


# print whether we are running in a virtual environment, this is helpful when
# debugging issues and just nice-to-know, if we are not in an env, then
# warn the user and allow them to continue anyway or quit, this is also useful,
# by the way when running inside of VSCode which has a habbit of not telling you
# if you are within an env or not
# @param nag if True, then will print out the message and wait for you to confirm
#                     you want to continue
def check_venv(nag=False):
    in_venv = False
    if "VIRTUAL_ENV" in os.environ:
        venv_path = os.environ["VIRTUAL_ENV"]
        venv_name = os.path.basename(venv_path)
        printf(f"Running inside a python virtual environment: [{venv_name}].")
        in_venv = True
    else:
        printf("*****************************************")
        printf("          W A R N I N G  !")
        printf("Not running inside a virtual environment.")
        if(nag):
            response = input("Do you want to continue anyway? (y/n): [y]").strip().lower()
            
            if response == 'n':
                print("Good choice, it is safer to run in a venv.")
                print("You can use the scripts create_venv.bat and then activate_venv.bat to create a venv")
                print("and then restart this program.")
                print("Exiting the program.")
                sys.exit(0)
            else:
                print("Continuing without a virtual environment...")
    return in_venv 


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



# Method to run the pip install package_name command in an operating system command
# 
def install_package(package_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])


def check_and_install_packages(required_libraries):
    # Try to import each module, install it if not found, and then import again
    set_g_start_time()
    printf("Checking/Loading modules...")
    for module_name, package_names in required_libraries.items():

        try:
            printf("Attempting to import module ["+module_name + "]/from pkg(s) : [" + package_names[0] + "]")
            globals()[module_name] = __import__(module_name)
        except Exception as ex:
          for package_name in package_names:

            printf("************")
            printf(f"********** Warning: Unable to import module [{module_name}].")
            printf(f"           PIP-Installing required package [{package_name}]...")
            printf(f" {ex}")
            printf("************")
            try:
                install_package(package_name)
            except Exception as ex:
                printf("**************************************************\n")
                printf("  UNABLE TO INSTALL PACKAGE [" + package_name + "] FOR MODULE [" + module_name + "] VIA OPERATING SYSTEM")

                printf( f"{ex}")
                printf("**************************************************\n")
                sys.exit(1)
                try:
                    utils.printf("Re-attempting to import module ["+module_name + "]/from pkg : [" + package_name + "]")
                    globals()[module_name] = __import__(module_name)
                except Exception as ex:
                    utils.printf("**************************************************\n")
                    utils.printf("  UNABLE TO IMPORT [" + module_name + "]")

                    utils.printf( f"{ex}")
                    utils.printf("**************************************************\n")
                    sys.exit(1)
    printf("IMPORT CHECK COMPLETE")
    printExecutionTime("... checking/Loading modules")