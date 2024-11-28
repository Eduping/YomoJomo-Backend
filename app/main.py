from fastapi import FastAPI, Depends
from routes import user, chatroom, message
app = FastAPI()

# 라우터 등록
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(chatroom.router, prefix="/chatrooms", tags=["ChatRooms"], dependencies=[Depends(user.get_current_user)])
app.include_router(message.router, prefix="/messages", tags=["Messages"], dependencies=[Depends(user.get_current_user)])
@app.get("/")
def read_root():
    return {"message": "Welcome to the Chatbot API"}