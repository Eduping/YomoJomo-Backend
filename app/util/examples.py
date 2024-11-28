from typing import Dict

def create_example_response(description: str, example: Dict):
    return {
        "description": description,
        "content": {"application/json": {"example": example}},
    }

common_examples = {
    # User API Responses
    "signup_success": {
        "status": 200,
        "success": True,
        "message": "User created successfully",
        "data": {"id": 1, "username": "testuser"}
    },
    "login_success": {
        "status": 200,
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            "token_type": "bearer"
        }
    },
    "user_retrieved": {
        "status": 200,
        "success": True,
        "message": "User retrieved successfully",
        "data": {"username": "testuser"}
    },

    # Student Record API Responses
    "upload_success": {
        "status": 200,
        "success": True,
        "message": "File uploaded successfully",
        "data": {
            "file_url": "https://your-s3-bucket.s3.amazonaws.com/path/to/file.pdf",
        },
    },
    "delete_success": {
        "status": 200,
        "success": True,
        "message": "File deleted successfully",
        "data": None,
    },

    # Student Record Error Responses
    "error_400_file_deleted": {
        "status": 400,
        "success": False,
        "message": "File already deleted.",
        "data": None,
    },
    "error_400_invalid_format": {
        "status": 400,
        "success": False,
        "message": "Only PDF files are allowed.",
        "data": None,
    },
    "error_404_file_not_found": {
        "status": 404,
        "success": False,
        "message": "File not found.",
        "data": None,
    },

    # General Error Responses
    "error_400": {
        "status": 400,
        "success": False,
        "message": "Bad Request",
        "data": None
    },
    "error_401_missing_refresh": {
        "status": 401,
        "success": False,
        "message": "Refresh token is missing",
        "data": None
    },
    "error_401_invalid_token": {
        "status": 401,
        "success": False,
        "message": "Invalid or expired token",
        "data": None
    },
    "error_403": {
        "status": 403,
        "success": False,
        "message": "Forbidden access",
        "data": None
    },
    "error_404_user": {
        "status": 404,
        "success": False,
        "message": "User not found",
        "data": None
    },
    "error_404_file": {
        "status": 404,
        "success": False,
        "message": "File not found",
        "data": None
    },
    "error_500": {
        "status": 500,
        "success": False,
        "message": "Internal Server Error",
        "data": None
    },

    # Token Refresh API Responses
    "refresh_success": {
        "status": 200,
        "success": True,
        "message": "Token refreshed successfully",
        "data": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            "token_type": "bearer"
        }
    },

    # Send Message API Responses
    "message_sent_success": {
        "status": 200,
        "success": True,
        "message": "Message sent successfully",
        "data": {
            "user_message": "Hello, how are you?",
            "bot_response": "I'm fine, thank you!"
        },
    },

    # Get Messages API Responses
    "messages_retrieved_success": {
        "status": 200,
        "success": True,
        "message": "Messages retrieved successfully",
        "data": [
            {
                "id": 1,
                "question": "Hello, how are you?",
                "answer": "I'm fine, thank you!",
                "timestamp": "2024-11-29T00:00:00",
                "chatroom_id": 1,
            },
            {
                "id": 2,
                "question": "What can you do?",
                "answer": "I can assist you with many tasks!",
                "timestamp": "2024-11-29T01:00:00",
                "chatroom_id": 1,
            },
        ],
    },
    "messages_not_found": {
        "status": 404,
        "success": False,
        "message": "No messages found in this chatroom",
        "data": None,
    },
    # Chatroom API Responses
    "chatroom_created_success": {
        "status": 200,
        "success": True,
        "message": "Chatroom created successfully",
        "data": {
            "id": 1,
            "name": "My Chatroom",
            "user_id": 1,
            "created_at": "2024-11-29T00:00:00",
            "updated_at": "2024-11-29T01:00:00",
            "deleted_at": None,
        },
    },
    "chatroom_list_success": {
        "status": 200,
        "success": True,
        "message": "Chatroom list retrieved successfully",
        "data": {
            "items": [
                {
                    "id": 1,
                    "name": "Hello, how are you?",
                    "last_message": "I am fine, thank you!",
                    "last_message_time": "2024-11-29T10:00:00",
                },
                {
                    "id": 2,
                    "name": "Any plans for today?",
                    "last_message": "Not really, just relaxing.",
                    "last_message_time": "2024-11-29T09:45:00",
                },
            ],
            "total": 2,
            "page": 1,
            "size": 10,
        },
    },
    # General Error Responses
    "error_400_invalid_request": {
        "status": 400,
        "success": False,
        "message": "Invalid request",
        "data": None,
    },
}