from fastapi import APIRouter, Depends, HTTPException, status


router = APIRouter(prefix="/auth")

@router.post("/login")
def login(payload):
    ...