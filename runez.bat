@echo off
setlocal EnableDelayedExpansion

REM Define default values for each option
set retriever_name=Naive_ST_FAISS_Retriever
set generator_name=T5SmallGenerator
set chunker_name=Simple_Chunker
set chunk_max_num=5
set chunk_size=512
set chunk_dist_scoring=EUCLIDIAN
set temperature=NONE
set quantize=True
set debug=True
set docs_dir=docs/security

REM Define possible values for each option
set retriever_name_choices=Naive_ST_FAISS_Retriever SimpleRetriever
set generator_name_choices=T5SmallGenerator TinyLLmGenerator
set chunker_name_choices=Simple_Chunker
set chunk_max_num_choices=1 5 6 7 10
set chunker_size_choices=50 256 512 768 1024
set chunk_dist_scoring_choices=EUCLIDIAN DOT_PRODUCT COSINE
set temperature_choices=NONE 0.1 0.2 0.5 0.7
set docs_dir_choices=docs/security docs/airrag_docs docs/email docs/geography docs/reports docs/wrk NONE
set quantize_choices=True False
set debug_choices=True False
set 

@REM set question=What is PJ's wife's name?
set question=What is original classification?

:menu
cls
echo.
echo Select an option to rotate its values, "R" to run, or "X" to exit.
echo.

REM Display options with alignment
call :display_option 1  retriever_name "     " !retriever_name! "  "  "[Naive_ST_FAISS_Retriever SimpleRetriever]"
call :display_option 2  generator_name "     " !generator_name! "  " "[T5SmallGenerator TinyLLmGenerator]"
call :display_option 3  chunker_name "       " !chunker_name! "  " "[Simple_Chunker]"
call :display_option 4  chunk_max_num "      " !chunk_max_num! "  " "[1 5 6 7 10]"
call :display_option 5  chunk_size "         " !chunk_size! "  " "[50 256 512 768 1024]"
call :display_option 6  chunk_dist_scoring " " !chunk_dist_scoring! "  " "[EUCLIDIAN, DOT_PRODUCT,COSINE]"
call :display_option 7  temperature "        " !temperature! " "      "[NONE, 0.1, 0.2, 0.5, 0.7]"
call :display_option 8  docs_dir "           " !docs_dir! "  "       "[C:/projects/docs/security, docs/airrag_docs, docs/email, docs/geography, docs/reports, docs/wrk, NONE]"
call :display_option 9  quantize "           " !quantize! "  "       "[True, False]"
call :display_option 10 debug "              " !debug! "  "          "[True, False]"
echo Q %question%
echo.
echo R RUN!
echo X EXIT

REM Get user input
set /p choice=Choose option, R to run, or X to exit:

REM Rotate option, run script, or quit based on input
if /i "%choice%"=="x" goto end
if /i "%choice%"=="r" goto run_script
if /i "%choice%"=="q" call :get_question
if "%choice%"=="1"  call :rotate_option retriever_name retriever_name_choices
if "%choice%"=="2"  call :rotate_option generator_name generator_name_choices
if "%choice%"=="3"  call :rotate_option chunker_name chunker_name_choices
if "%choice%"=="4"  call :rotate_option chunk_max_num chunk_max_num_choices
if "%choice%"=="5"  call :rotate_option chunk_size chunk_size_choices

if "%choice%"=="6"  call :rotate_option chunk_dist_scoring chunk_dist_scoring_choices
if "%choice%"=="7"  call :rotate_option temperature temperature_choices
if "%choice%"=="8"  call :rotate_option docs_dir docs_dir_choices
if "%choice%"=="9"  call :rotate_option quantize quantize_choices
if "%choice%"=="10" call :rotate_option debug debug_choices

REM Return to menu after each selection
goto menu

:get_question
set /p new_question=Enter your question:
set question=%new_question%
goto menu

:display_option
REM REM Display formatted option line with aligned values
set option_number=%1
set option_name=%2

REM interword spacer
set iwd1=%3
REM remove wrapper quotes
set iwd1=%iwd1:"=%

set option_value=%4

REM interword spacer
set iwd2=%5
REM remove wrapper quotes
set iwd2=%iwd2:"=%

set option_choices=%6
set option_choices=%option_choices:"=%

REM print line, should look something like this:
REM 1 retriever_name:    <giraffe> ... [Naive_ST_FAISS_Retriever,giraffe,ostritch]
REM call echo %option_number% %option_name%: %iwd1% [%option_value%] %iwd2% %option_choices%
set "display_line=%option_number% %option_name%: %iwd1% ^<%option_value%^> %iwd2% %option_choices%"
echo %display_line%
goto :eof


:rotate_option
REM Rotate to the next value in the list for the given option
set option_name=%1
set choices_name=%2
set current_value=!%option_name%!
set choices=!%choices_name%!

REM Initialize to the first value if the current one is at the end of the list
set next_value=
set found_next=
for %%v in (%choices%) do (
    if defined found_next (
        set next_value=%%v
        goto :end_rotate
    )
    if "!current_value!"=="%%v" (
        set found_next=1
    )
)

:end_rotate
REM Loop back to the first value if no next value was found
if not defined next_value (
    for %%v in (%choices%) do (
        set next_value=%%v
        goto :set_value
    )
)

:set_value
set %option_name%=%next_value%
goto :eof

:run_script
REM Run Python script with selected options as arguments
echo Running Python script with the selected options:
set args=--retriever_name=%retriever_name% --generator_name=%generator_name% --chunker_name=%chunker_name% --chunk_max_num=%chunk_max_num%  --chunk_size=%chunk_size% --chunk_dist_scoring=%chunk_dist_scoring% --tempAsStr=%temperature% --quantize=%quantize% --debug=%debug% --docs_dir=%docs_dir% --question="%question%"
echo python main_ai.py %args%
python main_ai.py %args%
goto end

:end
REM Exit the batch file and return to the command prompt
echo Exiting...
exit /b
