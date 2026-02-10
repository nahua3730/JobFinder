# JobFinder

Make sure Python version is 3.10.x
## Setup
1) Create venv: `python -m venv .venv`
2) Activate venv
3) Install: `pip install -r requirements.txt`
4) Migrate: `python manage.py migrate`
5) Run: `python manage.py runserver`

## Apps
- users: auth + roles + profiles
- jobs: job posts + search + map
- applications: apply + status + pipeline
