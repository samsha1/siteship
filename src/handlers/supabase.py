# Handles Supabase database and storage operations.
from datetime import datetime
from src.common.logger import get_logger


logger = get_logger(__name__)

async def save_html_to_storage(supabase_client, user_id: str, project_name: str, html_code: str) -> str:
    """
    Uploads the HTML code to Supabase Storage and returns the public URL.
    """
    # Make sure you have a Supabase bucket named `projects` or similar
    bucket_name = "projects"

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    file_path = f"{user_id}/{project_name}/{timestamp}/index.html"

    # Upload bytes
    response = supabase_client.storage.from_(bucket_name).upload(
        file_path, html_code.encode("utf-8"), {"content-type": "text/html"}
    )
    
    if hasattr(response, 'error') and response.error:
        logger.error("Upload failed with error: %s", response.error)

    # Supabase public URL format
    public_url = f"{supabase_client.storage.from_(bucket_name).get_public_url(file_path)}"

    return public_url
