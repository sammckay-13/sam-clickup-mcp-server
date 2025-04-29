import pytest
from unittest.mock import patch, MagicMock
from clickup_mcp_server.client import ClickUpClient
import requests

class TestClickUpClient:
    @pytest.fixture
    def client(self):
        return ClickUpClient("test_api_key")
    
    @patch("requests.request")
    def test_get_workspaces(self, mock_request, client):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"teams": [{"id": "123", "name": "Test Workspace"}]}
        mock_request.return_value = mock_response
        
        # Call method
        result = client.get_workspaces()
        
        # Verify results
        assert len(result) == 1
        assert result[0]["id"] == "123"
        assert result[0]["name"] == "Test Workspace"
        
        # Verify request was made correctly
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.clickup.com/api/v2/team",
            headers={"Authorization": "test_api_key", "Content-Type": "application/json"},
            params=None,
            json=None
        )
    
    @patch("requests.request")
    def test_get_tasks(self, mock_request, client):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"tasks": [{"id": "abc123", "name": "Test Task"}]}
        mock_request.return_value = mock_response
        
        # Call method
        result = client.get_tasks("list123")
        
        # Verify results
        assert len(result) == 1
        assert result[0]["id"] == "abc123"
        assert result[0]["name"] == "Test Task"
        
        # Verify request was made correctly
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.clickup.com/api/v2/list/list123/task",
            headers={"Authorization": "test_api_key", "Content-Type": "application/json"},
            params=None,
            json=None
        )
    
    @patch("requests.request")
    def test_create_task(self, mock_request, client):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "task123", "name": "New Task"}
        mock_request.return_value = mock_response
        
        # Call method
        result = client.create_task("list123", "New Task", description="Task description")
        
        # Verify results
        assert result["id"] == "task123"
        assert result["name"] == "New Task"
        
        # Verify request was made correctly
        mock_request.assert_called_once_with(
            method="POST",
            url="https://api.clickup.com/api/v2/list/list123/task",
            headers={"Authorization": "test_api_key", "Content-Type": "application/json"},
            params=None,
            json={"name": "New Task", "description": "Task description"}
        )
    
    @patch("requests.request")
    def test_update_task_status(self, mock_request, client):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "task123", "status": {"status": "In Progress"}}
        mock_request.return_value = mock_response
        
        # Call method
        result = client.update_task_status("task123", "In Progress")
        
        # Verify results
        assert result["id"] == "task123"
        assert result["status"]["status"] == "In Progress"
        
        # Verify request was made correctly
        mock_request.assert_called_once_with(
            method="PUT",
            url="https://api.clickup.com/api/v2/task/task123",
            headers={"Authorization": "test_api_key", "Content-Type": "application/json"},
            params=None,
            json={"status": "In Progress"}
        )
    
    @patch("requests.request")
    def test_request_error_handling(self, mock_request, client):
        # Setup mock to raise an exception
        mock_error_response = MagicMock()
        mock_error_response.text = "API Error"
        
        mock_exception = requests.exceptions.HTTPError()
        mock_exception.response = mock_error_response
        
        mock_request.side_effect = mock_exception
        
        # Call method and check for exception
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_workspaces()
EOF < /dev/null