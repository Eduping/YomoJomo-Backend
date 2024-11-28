from fastapi import FastAPI, Depends
from exceptions import http_exception_handler, validation_exception_handler, global_exception_handler, custom_exception_handler, CustomException
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from routes import user, chatroom, message, student_record
app = FastAPI()

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(CustomException, custom_exception_handler)
# 라우터 등록
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(chatroom.router, prefix="/chatrooms", tags=["ChatRooms"], dependencies=[Depends(user.get_current_user)])
app.include_router(message.router, prefix="/messages", tags=["Messages"], dependencies=[Depends(user.get_current_user)])
app.include_router(student_record.router, prefix="/student-records", tags=["Student Records"], dependencies=[Depends(user.get_current_user)])
@app.get("/")
def read_root():
    return {"message": "Welcome to the Chatbot API"}