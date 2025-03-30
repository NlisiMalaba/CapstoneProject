from fastapi import APIRouter
from app.controllers.user_controller import router as user_controller_router

# Create router
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={401: {"description": "Unauthorized"}}
)

# Include controller routes
router.include_router(user_controller_router)