@echo off
setlocal EnableDelayedExpansion

REM Define default values for each option
set retreiver_name=Naive_ST_FAISS_Retriever
set generator_name=TinyLLmGenerator
set chunk_dist_scoring=EUCLIDIAN
set quantize=True
set debug=True
set docs_dir=docs/geography

REM Define possible values for each option
set retreiver_name_choices=Naive_ST_FAISS_Retriever giraffe ostritch
set generator_name_choices=TinyLLmGenerator TinyLLmGenerator beer wine
set chunk_dist_scoring_choices=EUCLIDIAN DOT_PRODUCT COSINE
set docs_dir_choices=docs/airrag_docs docs/email docs/geography docs/reports docs/wrk NONE
set quantize_choices=True False
set debug_choices=True False
set 

:menu
cls
echo.
echo Select an option by number to rotate its values, "R" to run, or "Q" to quit.
echo.

REM Display options with alignment
call :display_option 1 retreiver_name " " !retreiver_name! "  "  "[Naive_ST_FAISS_Retriever,giraffe,ostritch]"
call :display_option 2 generator_name " " !generator_name! "  " "[TinyLLmGenerator, TinyLLmGenerator, beer, wine]"
call :display_option 3 chunk_dist_scoring " " !chunk_dist_scoring! "  " "[EUCLIDIAN, DOT_PRODUCT,COSINE]"
call :display_option 4 docs_dir "       " !docs_dir! "  "       "[docs/airrag_docs, docs/email, docs/geography, docs/reports, docs/wrk, NONE]"
call :display_option 5 quantize "       " !quantize! "  "       "[True, False]"
call :display_option 6 debug "          " !debug! "  "          "[True, False]"
echo.
echo R RUN!
echo Q QUIT

REM Get user input
set /p choice=Choose option, R to run, or Q to quit:

REM Rotate option, run script, or quit based on input
if /i "%choice%"=="Q" goto end
if /i "%choice%"=="R" goto run_script
if "%choice%"=="1" call :rotate_option retreiver_name retreiver_name_choices
if "%choice%"=="2" call :rotate_option generator_name generator_name_choices
if "%choice%"=="3" call :rotate_option chunk_dist_scoring chunk_dist_scoring_choices
if "%choice%"=="4" call :rotate_option docs_dir docs_dir_choices
if "%choice%"=="5" call :rotate_option quantize quantize_choices
if "%choice%"=="6" call :rotate_option debug debug_choices

REM Return to menu after each selection
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
REM 1 retreiver_name:    <giraffe> ... [Naive_ST_FAISS_Retriever,giraffe,ostritch]
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
set args=--retreiver_name=%retreiver_name% --generator_name=%generator_name% --chunk_dist_scoring=%chunk_dist_scoring% --quantize=%quantize% --debug=%debug% --docs_dir=%docs_dir%
echo python main_ai.py %args%
python main_ai.py %args%
goto end

:end
REM Exit the batch file and return to the command prompt
echo Exiting...
exit /b
