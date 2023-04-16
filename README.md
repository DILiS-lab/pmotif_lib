# pMotif Masterthesis

## Setup

### Virtualenv
Create a virtualenv and activate it:
```bash
venv .venv
source .venv/bin/activate
```
Now, install all the requirements:
```bash
pip3 install -r requirements.txt
```

### Pythonpath
For ease of use you can add the `pmotifs` module to the `PYTHONPATH`. This can also be scoped only for your virtualenv by changing `.venv/bin/activate`
([see this stackoverflow question](https://stackoverflow.com/a/4758351)):

```bash
# Append these line to `.venv/bin/activate`
export OLD_PYTHONPATH="$PYTHONPATH"
export PYTHONPATH="/the/path/to/motif_position_tooling_repo"

# Add this line to the beginning of the deactivate method in the same file
export PYTHONPATH="$OLD_PYTHONPATH"
```

To use the notebooks, you need to export the virtualenv as jupyter kernel spec and add the `PYTHONPATH` there too:
1. Activate the virtualenv
2. Export the kernel: `python -m ipykernel install --user --name=<kernel_name>`
3. Use `jupyter kernelspec list` to find the directory of your kernel
4. Edit the `kernel.json` in that directory, adding `"env": {"PYTHONPATH": "/the/path/to/motif_position_tooling_repo"}` to it
