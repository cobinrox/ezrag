# README #

This is an ai rag research project.

## To Set Up Virtual Environment (VERY HIGHLY RECOMMENDED)
1.  Open command window within the project.
1.  Run: `create_venv.bat`
1.  You should see a new folder calleed "myenv", this will have your new python env files and where new lib installations will go
1.  Run: `activate_venv.bat`
1.  You should see `(myenv)` now in the command window prompt, this indicates that you are running in your new python private env!
1.  You can now open VSCode and tell VSCode to use the private env as well.  To do this, once in VSCode press Ctl+Shift+P and type `Python: Select Interpreter` and you should get a popup that allows you to navigate to your new `myenv\Scripts\python.exe` file.  This tells VSCode to respect your new env.  Note that VSCode is finicky about indicating that it is using your private env, so be advised.

## The Following Files or Directories Are at Your Service
-   ./data:           temporary directory to store db vector embeddings
-   ./docs:           stores documents that you want to "query" in your rag
-   ./myvenv:         temporary directory that gets created when you use the `create_venv.bat` file to set up a python virtual env
-   ./packages:       directory of implementation python classes/files/utilities
-   __init__.py:      an idiom used by python to indicate that the current dir is a python "package"
-   create_env.bat:   creates private environment called "myenv"
-   activate_env.bat: activates the environment
-   delete_env.bat:   deletes the environment files and the __py_cache__ dir
-   freeze_env.bat:   runs the python freeze command against your environment and creates the requirements.txt file
-   install_crap.py   a python stand-alone program that can help you install python dependencies when they get out of hand, this is especially a problem when dealing with a myriad of python ai libraries that change and have nasty inter-dependencies
-   main_ai.py:       the main code to run
-   runez.bat:        a wrapper batch file to run the main_ai.py code, using simple menu to help establish commadn line args

