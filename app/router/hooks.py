from fastapi import APIRouter, Request, Response

import subprocess

router = APIRouter(prefix="/hook")

@router.post("/deploy")
async def hook_deploy(request: Request):
    
    data = await request.json()

    # perform git source code updation
    subprocess.run(["git", "pull", "--force", "origin", "v2"])
    subprocess.run(["refresh"])

    return Response(status_code=202)