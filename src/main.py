from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.responses import json_response

from api import router


app = FastAPI(
    title="GoSend API",
    description="GoSend+ API Documentation",
    version="0.1.0"
)

app.include_router(router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    
    return json_response(
        message= str(exc.detail),
        status_code=exc.status_code
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return json_response(
        message="Validaton error occured",
        data = {"errors": exc.errors()},
        status_code = 400
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}