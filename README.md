## Steps for setting up automated function on Google Cloud Run
1. From Google Cloud SDK Shell, navigate to the `cloud-deploy` folder
2. Run the following command to _build_ a container and image from the folder: `gcloud run jobs deploy hourly-data-fetch --source . --tasks 1 --max-retries 5 --region us-west1 --project=project-3ef7264f-b261-47c4-964`
3. To manually run

Notes:
 - Currently, this does not use multithreading for quicker execution (see that `tasks` is set to 1).
 - This can only be done by a user with appropriate permissions, which as of 10/28/25 is Alyssa.


## Running the App
Prereqs: Node.js, python
<br>
Backend: ```cd backend run pip install -r requirements.txt && python3 app.py```
<br>
Frontend: ```cd frontend/minecraft-project npm i && npm run dev```