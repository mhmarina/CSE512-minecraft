# Steps for setting up automated function on Google Cloud Run
1. From Google Cloud SDK Shell, navigate to the `cloud-deploy` folder
2. Run the following command to _build_ a container and image from the folder: `gcloud run jobs deploy hourly-data-fetch --source . --tasks 1 --max-retries 5 --region us-west1 --project=project-3ef7264f-b261-47c4-964`
3. To manually _run_ the function, navigate to the function dashboard (or use this link: https://console.cloud.google.com/run/jobs/details/us-west1/hourly-data-fetch/executions?authuser=1&project=project-3ef7264f-b261-47c4-964&supportedpurview=project) and click the "execute" button.

Notes:
 - Currently, this does not use multithreading for quicker execution (see that `tasks` is set to 1).
 - This can only be done by a user with appropriate permissions, which as of 10/28/25 is Alyssa.

# Running the App
Prereqs: Node.js, python, cockroachDB
## Set up database
This app uses cockroachDB as its data layer. The schema is available in `SQL Queries/insert_table.sql`. Note down the DB host, name, username and password for `.env` in next step.
## Running the Backend
The backend is a flask server. to run: 
```bash
cd backend
```
Optional, set up virtual environment:
```bash
 python -m venv .venv && source .venv/bin/activate
```
Install dependencies:
```bash
 pip install -r requirements.txt
```
 Setup `.env` file with the following variables:
 ```.env
DB_USER
DB_PASS
DB_HOST
DB_NAME
```
 Run app:
 ```bash
 python app.py
```
# Running the Frontend
The frontend is a React app. To run:
```bash
cd frontend
```
Install dependencies:
```bash
npm i
```
Run app:
```bash
npm run dev
```

# Screenshots
<img width="1894" height="975" alt="image" src="https://github.com/user-attachments/assets/601d5d2b-f3d5-4987-9e5c-3405fc2b8f63" />
<img width="1884" height="946" alt="image" src="https://github.com/user-attachments/assets/503cf532-bacc-4a50-8f91-9a2c76c2da08" />

