# Prototypia Python Part

A `Python` Package helping the Writing & Encoding(Compiling) of Aerials Chart[Fumen].

Also available on [**PyPI**](https://pypi.org/project/Prototypia/) .

## Common Usage

1. Update `Python` on your platform to **3.12 or upper** ;

2. Install the Package via `pip3` :
   
   ```shell
   pip3 install Prototypia
   ```

3. Import the Package **at the top of your chart[fumen] prototype file** like this :
   
   ```python
   from Prototypia import *
   
   # Fumen Body
   ```

## Bundle Manually

1. Maintain the `pyproject.toml` as you please ;

2. Upgrade Package `build` & `twine` via `pip3` :
   
   ```shell
   pip3 install --upgrade build
   pip3 install --upgrade twine
   ```

3. Go to the root of Project Volume, and bundle the Packages like this :
   
   ```shell
   python -m build
   ```

4. Upload the bundles like this (use the username `__token__`, and you'll need a `token` generated from the PyPI console) :
   
   ```shell
   twine upload dist/*
   ```


