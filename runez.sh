#!/bin/bash
#
#  This is just an easy-to-use cmd window menu that is useful to get started
#  using the ezrag project.  It just prints out some options that are available and
#  allows the user to pick which option they want to use and then pass those values
#  of to the main_ai.py.
#

# Enable case-insensitive matching
shopt -s nocasematch

# Initialize default values for each option
retriever_name="Naive_ST_FAISS_Retriever"
generator_name="T5SmallGenerator"
chunker_name="Simple_Chunker"
chunk_max_num=5
chunk_size=512
chunk_dist_scoring="EUCLIDIAN"
temperature="NONE"
quantize="True"
debug="True"
docs_dir="docs/security"

# Define possible values for each option as arrays
retriever_name_choices=("Naive_ST_FAISS_Retriever" "SimpleRetriever")
generator_name_choices=("T5SmallGenerator" "T5BaseGenerator" "TinyLLmGenerator")
chunker_name_choices=("Simple_Chunker")
chunk_max_num_choices=(1 5 6 7 10)
chunk_size_choices=(50 256 512 768 1024)
chunk_dist_scoring_choices=("EUCLIDIAN" "DOT_PRODUCT" "COSINE")
temperature_choices=("NONE" 0.1 0.2 0.5 0.7)
docs_dir_choices=("docs/security" "docs/airrag_docs" "docs/email" "docs/geography" "docs/reports" "docs/wrk" "NONE")
quantize_choices=("True" "False")
debug_choices=("True" "False")

# Initialize question
question="What is original classification?"

# Function to display an option
display_option() {
    local option_number=$1
    local option_name=$2
    local option_value=$3
    local option_choices=$4

    printf "%2s %-25s: <%s> %s\n" "$option_number" "$option_name" "$option_value" "$option_choices"
}

# Function to rotate to the next value in the choices array
rotate_option() {
    local option_name=$1
    local -n choices_ref=$2
    local current_value=${!option_name}
    local next_value=""
    local found=0

    for choice in "${choices_ref[@]}"; do
        if [[ "$found" -eq 1 ]]; then
            next_value="$choice"
            break
        fi
        if [[ "$choice" == "$current_value" ]]; then
            found=1
        fi
    done

    # If current value is the last in the array, loop back to the first
    if [[ -z "$next_value" ]]; then
        next_value="${choices_ref[0]}"
    fi

    # Update the option with the next value
    declare -g "$option_name"="$next_value"
}

# Function to get a new question from the user
get_question() {
    read -rp "Enter your question: " new_question
    if [[ -n "$new_question" ]]; then
        question="$new_question"
    fi
}

# Function to run the Python script with selected options
run_script() {
    echo "Running Python script with the selected options:"
    
    args=(
        "--retriever_name=$retriever_name"
        "--generator_name=$generator_name"
        "--chunker_name=$chunker_name"
        "--chunk_max_num=$chunk_max_num"
        "--chunk_size=$chunk_size"
        "--chunk_dist_scoring=$chunk_dist_scoring"
        "--tempAsStr=$temperature"
        "--quantize=$quantize"
        "--debug=$debug"
        "--docs_dir=$docs_dir"
        "--question=\"$question\""
    )
    
    # Display the command that will be executed
    echo "python main_ai.py ${args[*]}"
    
    # Execute the Python script with arguments
    python main_ai.py "${args[@]}"
    
    # Wait for user to press Enter before returning to menu
    read -rp "Press Enter to return to the menu..."
}

# Function to display the menu
show_menu() {
    clear
    echo
    echo "Select an option to rotate its values, 'R' to run, 'Q' to change the question, or 'X' to exit."
    echo

    # Display all options with their current values and possible choices
    display_option "1" "retriever_name" "$retriever_name" "[${retriever_name_choices[*]}]"
    display_option "2" "generator_name" "$generator_name" "[${generator_name_choices[*]}]"
    display_option "3" "chunker_name" "$chunker_name" "[${chunker_name_choices[*]}]"
    display_option "4" "chunk_max_num" "$chunk_max_num" "[${chunk_max_num_choices[*]}]"
    display_option "5" "chunk_size" "$chunk_size" "[${chunk_size_choices[*]}]"
    display_option "6" "chunk_dist_scoring" "$chunk_dist_scoring" "[${chunk_dist_scoring_choices[*]}]"
    display_option "7" "temperature" "$temperature" "[${temperature_choices[*]}]"
    display_option "8" "docs_dir" "$docs_dir" "[${docs_dir_choices[*]}]"
    display_option "9" "quantize" "$quantize" "[${quantize_choices[*]}]"
    display_option "10" "debug" "$debug" "[${debug_choices[*]}]"
    
    echo "Q  Set Question: \"$question\""
    echo
    echo "R  RUN!"
    echo "X  EXIT"
    echo
}

# Main loop
while true; do
    show_menu

    # Prompt user for input
    read -rp "Choose option, R to run, Q to set question, or X to exit: " choice

    case "$choice" in
        [xX])
            echo "Exiting..."
            exit 0
            ;;
        [rR])
            run_script
            ;;
        [qQ])
            get_question
            ;;
        1)
            rotate_option "retriever_name" retriever_name_choices
            ;;
        2)
            rotate_option "generator_name" generator_name_choices
            ;;
        3)
            rotate_option "chunker_name" chunker_name_choices
            ;;
        4)
            rotate_option "chunk_max_num" chunk_max_num_choices
            ;;
        5)
            rotate_option "chunk_size" chunk_size_choices
            ;;
        6)
            rotate_option "chunk_dist_scoring" chunk_dist_scoring_choices
            ;;
        7)
            rotate_option "temperature" temperature_choices
            ;;
        8)
            rotate_option "docs_dir" docs_dir_choices
            ;;
        9)
            rotate_option "quantize" quantize_choices
            ;;
        10)
            rotate_option "debug" debug_choices
            ;;
        *)
            echo "Invalid choice. Please try again."
            # Wait for user to press Enter before re-displaying the menu
            read -rp "Press Enter to continue..."
            ;;
    esac
done
