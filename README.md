This is the mftutor project. Django project in the mftutor/ folder, Django app
in the tutor/ folder.

Please indent Python code with 4 spaces and follow PEP8 as much as possible.

In Vim, you may wish to add the following to your .vimrc:

    autocmd FileType python set shiftwidth=4 softtabstop=4 expandtab
    filetype indent plugin on

Clone the repository:

    git clone https://github.com/matfystutor/web.git tutorweb

You should run the Django project in a virtualenv. For a local non-root virtualenv installation:

    virtualenv web-venv
    source web-venv/bin/activate (not windows)
    ./web-venv/scripts/activate (windows)
    pip install -r requirements.txt

You need to create a mftutor/settings/local.py based on local.py.example in the
mftutor/settings folder.

    cp mftutor/settings/local.py.example mftutor/settings/local.py

You can now create the tables and run the server.

    python manage.py syncdb
    python manage.py runserver
