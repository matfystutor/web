This is the mftutor project. Django project in the mftutor/ folder, Django app
in the tutor/ folder.

Please indent Python code with 4 spaces and follow PEP8 as much as possible.

In Vim, you may wish to add the following to your .vimrc:

    autocmd FileType python set shiftwidth=4 softtabstop=4 expandtab
    filetype indent plugin on

You should run the Django project in a virtualenv. For a local non-root virtualenv installation:

    mkdir web-venv; cd web-venv
    wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    python virtualenv.py .
    source bin/activate
    cd ../tutorweb
    pip install -r requirements.txt

You need to create a mftutor/settings/local.py based on local.py.example in the
mftutor/settings folder.
