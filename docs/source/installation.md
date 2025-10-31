# Installation guide

1- Download and install the code editor [VSCode](https://code.visualstudio.com/). Make sure to select the "Add to PATH" option when installing 

2- Download and install [Python](https://www.python.org/downloads/).

3- Add the *Python* extension in the code editor (in "Extensions marketplace" on the left sidebar)

4- Open the terminal inside VS Code by clicking Terminal > New Terminal. Run the following command to create an environment ``.venv``:

``` bash
python -m venv .venv
```
7- Activate the environment writting in the terminal

``` bash
.venv\Scripts\Activate.ps1
```

**Note** (from [here](https://docs.python.org/3/library/venv.html))

On Microsoft Windows, it may be required to enable the Activate.ps1 script by setting the execution policy for the user. You can do this by issuing the following PowerShell command:

``` bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

8- Install the package:

``` bash
pip install simeasren
```