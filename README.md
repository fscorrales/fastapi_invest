# FastAPI Invest
FastAPI ...

## Instructions (lazy version, for VSCode users)
1. Open the preview of this file to continue:

   `[CTRL] + [SHIFT] + [V]` (Windows/Linux) or `[CMD] + [SHIFT] + [V]` (Mac)
1. [Install Python 3.12]((https://www.python.org/downloads/))
1. Install poetry (globally):
    - For windows
   ```bash
   pip install poetry
   ```
    - For Linux/Max
   ```bash
   pipx install poetry
   ```

1. Configure poetry:
   ```bash
   poetry config virtualenvs.in-project true
   ```
1. Create the venv and install dependencies:
   ```bash
   poetry install
   ```
1. Install Playwright browsers (if not already installed):
    ```bash
    playwright install
    ```
    Or:
    ```bash
    poetry run playwright install
    ```

1. Open the project directory in VSCode.

1. In VSCode, select the appropriate interpreter:

   `[CTRL] + [SHIFT] + [P]` (Windows/Linux) or `[CMD] + [SHIFT] + [P]` (Mac) 
   Type: _Python: Select Interpreter_ and select the one corresponding to the environment created by `poetry`.
   >Alternative: Check the status bar (at the bottom of the VSCode window); if you open a Python file (e.g., main.py), you should see the selected interpreter in this bar, and you can change it by clicking there.
1. Now, if we open an integrated terminal in VSCode, the virtual environment should activate automatically. But just in case, you can manually activate it with:
   ```bash
   poetry shell
   ```
1. Run our server:
   ```bash
   fastapi dev src/main.py
   ```
1. As the console should say, visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Important: Playwright Browsers Installation

If you are using Playwright for the first time or after updating it, you need to install the required browsers. Otherwise, you may encounter the following warning:

>WARNING: Playwright browsers not found. Looks like Playwright was just installed or updated. Please run the following command to download new browsers: playwright install

To resolve this, run the following command in your terminal:
```bash
playwright install
```

Or, using poetry, do the following:
```bash
poetry run playwright install
```

## Running Scripts in the `handlers` Folder

Inside the `handlers` folder, you can execute the scripts that have been created using `argparse`. To run a script, simply use the following command, with activated venv:
```bash
python -m src.{module_name}.handlers.{script_name} {args if necessary}
```

Or, using poetry, do the following:
```bash
poetry run python -m src.{module_name}.handlers.{script_name} {args if necessary}
```