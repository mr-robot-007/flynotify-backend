import os
from fastapi import HTTPException
from supabaseclient import get_supabase_client
from fastapi.responses import JSONResponse

supabase = get_supabase_client()

async def supabase_login(username: str, password: str):
    try:
        response = supabase.auth.sign_in_with_password({"email":username, "password":password})
        x = supabase.auth.get_user(response.session.access_token) 
        # supabase.auth.sign_out()
        return response.session.access_token
    

    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid credentials")



async def supbase_getUser(jwt: str):
    try:
        # print(jwt)
        response = supabase.auth.get_user(jwt)
        # print(response)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid token")
        return e


async def supabase_logout():
    try:
        response = supabase.auth.sign_out()
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid token")
        return e
    

async def forgot_password(email: str):
    try:
        res = await supabase.auth.reset_password_email(email)
        return JSONResponse(status_code=200, content={"message": "Reset Link sent successfully"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": "Email Rate limit exceeded"})