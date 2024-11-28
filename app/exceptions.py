from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

class CustomException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "success": False,
            "message": exc.detail,
            "data": None,
        },
    )

async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": 422,
            "success": False,
            "message": "Validation error",
            "data": exc.errors(),
        },
    )

async def custom_exception_handler(request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "success": False,
            "message": exc.message,
            "data": None,
        },
    )

async def global_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "success": False,
            "message": "Internal server error",
            "data": None,
        },
    )