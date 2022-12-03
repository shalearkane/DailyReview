# DailyReview

## How to contribute
0. Clone the repository using `git clone https://github.com/shalearkane/DailyReview/`
1. Enter the Daily Review directory andcCreate a virtual environment using `virtualenv .venv` command
2. Activate the virtualenv by `source .venv/bin/activate` and then install python dependencies using `pip install -r requirements.txt`
3. Create a `.env` file to get Google Authentication working
4. Run `python manage.py migrate` to setup your datatbase.
5. Run `python manage.py createsuperuser` to setup initial superuser to access the admin panel
6. Go to `http://127.0.0.1:8000/admin/socialaccount/socialapp/add/` and add
    - Provider `Google`
    - Name `GoogleAuth`
    - Client id `copy-from-.env-file`
    - Secret key `copy-from-.env-file`
    - Save it. Now your Google Auth will work.