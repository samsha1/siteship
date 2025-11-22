from src.common.logger import get_logger
from typing import Optional, List, Dict, Any

logger = get_logger(__name__)

async def get_user_by_phone(supabase, phone_number: str) -> Optional[Dict[str, Any]]:
    """
    Get user by phone number.
    """
    try:
        response = await supabase.table("users").select("*").eq("phone_number", phone_number).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error fetching user by phone {phone_number}: {e}")
        return None

async def create_user(supabase, name: str, phone_number: str, platform: str) -> Optional[Dict[str, Any]]:
    """
    Create a new user with initial state.
    """
    try:
        data = {"name": name, "phone_number": phone_number, "platform": platform, "state": "WAITING_FOR_PROJECT_NAME"}
        response = await supabase.table("users").insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error creating user {phone_number}: {e}")
        return None

async def update_user_state(supabase, user_id: str, state: str) -> Optional[Dict[str, Any]]:
    """
    Update user state.
    """
    try:
        response = await supabase.table("users").update({"state": state}).eq("id", user_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error updating user state for {user_id}: {e}")
        return None

async def create_project(supabase, user_id: str, project_name: str) -> Optional[Dict[str, Any]]:
    """
    Create a new project for the user.
    """
    try:
        data = {"user_id": user_id, "name": project_name}
        response = await supabase.table("projects").insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error creating project {project_name} for user {user_id}: {e}")
        return None

async def get_user_projects(supabase, user_id: str) -> List[Dict[str, Any]]:
    """
    Get all projects for a user.
    """
    try:
        response = await supabase.table("projects").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching projects for user {user_id}: {e}")
        return []

async def get_project_by_id(supabase, project_id: str) -> Optional[Dict[str, Any]]:
    """
    Get project by ID.
    """
    try:
        response = await supabase.table("projects").select("*").eq("id", project_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {e}")
        return None

async def save_prompt(supabase, user_id: str, project_id: str, message_id: str, prompt_text: str, model_response: str = None) -> Optional[Dict[str, Any]]:
    """
    Save a prompt to the prompts table.
    """
    try:
        data = {
            "user_id": user_id,
            "project_id": project_id,
            "message_id": message_id,
            "prompt_text": prompt_text,
            "model_response": model_response
        }
        response = await supabase.table("prompts").insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error saving prompt for user {user_id}: {e}")
        return None
