fuser -k 8000/tcp

source ./.env
source ./venv/bin/activate

echo "+ uvicorn"
uvicorn app.main:app --reload