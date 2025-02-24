from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uuid
from .auth.oauth import GoogleOAuth
from .auth.dependencies import get_current_user, create_session
from .redis_manager import RedisManager

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
google_oauth = GoogleOAuth()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/auth/login")
async def login():
    state = str(uuid.uuid4())
    redis_client = RedisManager.get_client()
    redis_client.setex(f"oauth_state:{state}", 300, "1")
    auth_url = google_oauth.get_auth_url(state)
    return RedirectResponse(auth_url)

@app.get("/auth/callback")
async def callback(code: str, state: str, response: Response):
    redis_client = RedisManager.get_client()
    
    if not redis_client.get(f"oauth_state:{state}"):
        raise HTTPException(status_code=400, detail="Invalid state")
    
    redis_client.delete(f"oauth_state:{state}")
    
    token_data = await google_oauth.get_token(code)
    user_info = await google_oauth.get_user_info(token_data["access_token"])
    
    session_id = create_session(user_info)
    
    
    response = RedirectResponse(url="/")
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=86400
    )
    return response

@app.get("/answer")
async def protected_endpoint(
    prompt: str,
    current_user: dict = Depends(get_current_user)
):
    return {"response": f"Hello {current_user['email']}, your prompt was: {prompt}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    