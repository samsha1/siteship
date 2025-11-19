import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

# Mock the lifespan to avoid actual client initialization
@pytest.fixture
def mock_app_state():
    mock_supabase = AsyncMock()
    mock_twilio = MagicMock()
    mock_gemini = MagicMock()
    
    app.state.supabase = mock_supabase
    app.state.twilio = mock_twilio
    app.state.gemini = mock_gemini
    
    return mock_supabase, mock_twilio

client = TestClient(app)

@patch('src.routes.webhook.get_user_by_phone')
@patch('src.routes.webhook.create_user')
@patch('src.routes.webhook.send_message')
def test_new_user_flow(mock_send_message, mock_create_user, mock_get_user_by_phone):
    # Setup mocks
    mock_supabase = AsyncMock()
    mock_twilio = MagicMock()
    
    # We need to inject these into the app state manually since TestClient doesn't trigger lifespan in the same way for mocks
    # But actually, TestClient DOES trigger lifespan.
    # However, we want to override what lifespan does, or mock the init functions.
    
    with patch('main.init_supabase_client', return_value=mock_supabase), \
         patch('main.init_twilio_client', return_value=mock_twilio), \
         patch('main.init_gemini_client'):
        
        with TestClient(app) as client:
            print("Testing New User Flow...")
            # 1. New User
            mock_get_user_by_phone.return_value = None
            mock_create_user.return_value = {"id": "user123", "phone_number": "123", "state": "WAITING_FOR_PROJECT_NAME"}
            
            response = client.post("/whatsapp-webhook", data={
                "From": "whatsapp:+123",
                "To": "whatsapp:+456",
                "Body": "Hi",
                "SmsMessageSid": "msg1",
                "WaId": "123"
            })
            
            assert response.status_code == 200
            mock_create_user.assert_called_once()
            mock_send_message.assert_called_with(mock_twilio, "whatsapp:+456", "whatsapp:+123", "Welcome 👋\nI can help you build a website in minutes.\nLet's get started by Starting a new project. Please name your project")
            print("New User Flow Passed")

@patch('src.routes.webhook.get_user_by_phone')
@patch('src.routes.webhook.create_project')
@patch('src.routes.webhook.update_user_state')
@patch('src.routes.webhook.send_message')
def test_create_project_flow(mock_send_message, mock_update_user_state, mock_create_project, mock_get_user_by_phone):
    mock_supabase = AsyncMock()
    mock_twilio = MagicMock()
    
    with patch('main.init_supabase_client', return_value=mock_supabase), \
         patch('main.init_twilio_client', return_value=mock_twilio), \
         patch('main.init_gemini_client'):
         
        with TestClient(app) as client:
            print("Testing Create Project Flow...")
            # 2. Create Project
            mock_get_user_by_phone.return_value = {"id": "user123", "state": "WAITING_FOR_PROJECT_NAME"}
            mock_create_project.return_value = {"id": "proj1", "name": "Project X"}
            
            response = client.post("/whatsapp-webhook", data={
                "From": "whatsapp:+123",
                "To": "whatsapp:+456",
                "Body": "Project X",
                "SmsMessageSid": "msg2",
                "WaId": "123"
            })
            
            assert response.status_code == 200
            mock_create_project.assert_called_with(mock_supabase, "user123", "Project X")
            mock_update_user_state.assert_called_with(mock_supabase, "user123", "ACTIVE_PROJECT:proj1")
            mock_send_message.assert_called_with(mock_twilio, "whatsapp:+456", "whatsapp:+123", "Congratulations your project is created! Now, tell me more about this project so that I can help you build great websites.")
            print("Create Project Flow Passed")

if __name__ == "__main__":
    try:
        # We need to run this with pytest usually, but for simple script execution:
        # We can just run the functions if we handle the async mocks correctly.
        # However, since we use TestClient, it handles the async loop for the app.
        # But our mocks for db functions are async, so they need to return awaitables if called directly?
        # No, the route calls await on them. So our mocks should be AsyncMock or return a future.
        # The @patch decorator with AsyncMock (or default MagicMock in newer python) might need adjustment.
        # Let's just try running it.
        test_new_user_flow()
        test_create_project_flow()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
