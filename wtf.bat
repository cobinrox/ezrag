@echo off
setlocal EnableDelayedExpansion

REM Define default values for each option
set ReceiverType=Naive_ST_FAISS_Retriever
set GeneratorType=TinyLLmGenerator
set DocDir=docs/email
set Quantize=True
set Debug=True

REM Define possible values for each option
set ReceiverType_choices=Naive_ST_FAISS_Retriever giraffe ostritch
set GeneratorType_choices=TinyLLmGenerator TinyLLmGenerator beer wine
set DocDir_choices=docs/airrag_docs docs/email docs/geography docs/reports docs/udlstuff
set Quantize_choices=True False
set Debug_choices=True False

:menu
cls
echo.
echo Select an option by number to rotate its values, "R" to run the Python script, or "Q" to quit.
echo.

REM Display options with alignment
call :display_option 1 ReceiverType !ReceiverType! "[Naive_ST_FAISS_Retriever,giraffe,ostritch]"
call :display_option 2 GeneratorType !GeneratorType! "[TinyLLmGenerator, TinyLLmGenerator, beer, wine]"
call :display_option 3 DocDir !DocDir! "[docs/airrag_docs, docs/email, docs/geography, docs/reports, docs/udlstuff]"
call :display_option 4 Quantize !Quantize! "[true, false]"
call :display_option 5 Debug !Debug! "[true, false]"
echo.
echo R RUN!
echo Q QUIT

REM Get user input
set /p choice=Choose option, R to run, or Q to quit:

REM Rotate option, run script, or quit based on input
if /i "%choice%"=="Q" goto end
if /i "%choice%"=="R" goto run_script
if "%choice%"=="1" call :rotate_option ReceiverType ReceiverType_choices
if "%choice%"=="2" call :rotate_option GeneratorType GeneratorType_choices
if "%choice%"=="3" call :rotate_option DocDir DocDir_choices
if "%choice%"=="4" call :rotate_option Quantize Quantize_choices
if "%choice%"=="5" call :rotate_option Debug Debug_choices

REM Return to menu after each selection
goto menu

:display_option
REM Display formatted option line with aligned values
set option_number=%1
set option_name=%2
set option_value=%3
set option_choices=%4

REM Determine padding lengths for alignment
set "pad_name=               "  REM Adjust these spaces for name padding
set "pad_value=           "     REM Adjust these spaces for value padding

REM Calculate dynamic padding based on option name and value length
set /a name_pad_length=15 - !strlen_%option_name%!
set /a value_pad_length=10 - !strlen_%option_value%!

set "name_pad=!pad_name:~0,%name_pad_length%!"
set "value_pad=!pad_value:~0,%value_pad_length%!"

REM Display the formatted line with padding applied
echo %option_number% %option_name%%name_pad%: [%option_value%]%value_pad% %option_choices%

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
set args=ReceiverType=%ReceiverType% GeneratorType=%GeneratorType% DocDir=%DocDir% Quantize=%Quantize% Debug=%Debug%
echo python pythonScriptName.py %args%
python pythonScriptName.py %args%
goto end

:end
REM Exit the batch file and return to the command prompt
echo Exiting...
exit /b
