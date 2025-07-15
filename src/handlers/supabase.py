# Handles Supabase database and storage operations.
from datetime import datetime
import aiofiles
from src.common.logger import get_logger


logger = get_logger(__name__)

async def save_html_to_storage(supabase_client, user_id: str, project_name: str, file_path: str) -> str:
    """
    Uploads the HTML code to Supabase Storage and returns the public URL.
    """
    # Make sure you have a Supabase bucket named `projects` or similar
    bucket_name = "projects"

    async with aiofiles.open(file_path, "rb") as f:
        zip_data = await f.read()
    # Upload bytes
    bucket_file_path = f"{user_id}/{project_name}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

    response = supabase_client.storage.from_(bucket_name).upload(
        bucket_file_path, zip_data, {"content-type": "application/zip"}
    )
    
    if hasattr(response, 'error') and response.error:
        logger.error("Upload failed with error: %s", response.error)

    # Supabase public URL format
    public_url = f"{supabase_client.storage.from_(bucket_name).get_public_url(bucket_file_path)}"

    return public_url
