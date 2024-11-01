import sys
from types import ModuleType, FunctionType, MethodType
import numpy as np

def printObj(obj, max_depth=3, max_length=50, current_depth=0):
    """
    Print a representation of an object, handling circular references and complex structures.
    
    :param obj: The object to print
    :param max_depth: Maximum depth to recurse into nested structures
    :param max_length: Maximum number of items to show for sequences and mappings
    :param current_depth: Current recursion depth (used internally)
    """
    # Check recursion depth
    if current_depth > max_depth:
        return "..."

    # Handle basic types
    if isinstance(obj, (int, float, str, bool, type(None))):
        return repr(obj)

    elif isinstance(obj, np.ndarray):
         formatted_array = np.array2string(obj, precision=2, separator=', ', suppress_small=True)
         return f"np.ndarray {formatted_array}"


    # Handle sequences (list, tuple, etc.)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        type_name = type(obj).__name__
        items = [printObj(x, max_depth, max_length, current_depth + 1) for x in list(obj)[:max_length]]
        if len(obj) > max_length:
            items.append("...")
        return f"{type_name}([{', '.join(items)}])"

    # Handle dictionaries
    elif isinstance(obj, dict):
        items = [f"{printObj(k, max_depth, max_length, current_depth + 1)}: {printObj(v, max_depth, max_length, current_depth + 1)}" 
                 for k, v in list(obj.items())[:max_length]]
        if len(obj) > max_length:
            items.append("...")
        return f"dict({{{', '.join(items)}}})"

    # Handle modules
    elif isinstance(obj, ModuleType):
        return f"<module '{obj.__name__}'>"

    # Handle functions and methods
    elif isinstance(obj, (FunctionType, MethodType)):
        return f"<function '{obj.__name__}'>"

    # Handle other objects
    else:
        class_name = obj.__class__.__name__
        try:
            attrs = vars(obj)
        except:
            return f"<{class_name} object>"
        
        items = [f"{k}={printObj(v, max_depth, max_length, current_depth + 1)}" 
                 for k, v in list(attrs.items())[:max_length]]
        if len(attrs) > max_length:
            items.append("...")
        return f"<{class_name}({', '.join(items)})>"

def safe_print_obj(obj, obj_name):
        max_depth=3 
        max_length=50
        if obj_name == None: obj_name = "some object"
        print(f"DEBUG OBJECT [{obj_name}] of type ({type(obj)}):")
        try:
           result = printObj(obj, max_depth, max_length)
           print(result)
        except Exception as e:
           print(f"horked trying to print out large object")
           print(f"Error while printing object: {e}")
           print(f"Object type: {type(obj)}")
           print(f"Object string representation: {str(obj)}")           
        print(f"=== DEBUG END OBJECT [{obj_name}] ===")

# Usage
# safe_print_obj(your_object)