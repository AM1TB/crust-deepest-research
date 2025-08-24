import os
import requests
from typing import Dict, Any, Optional


def make_api_call(
    url: str,
    request_body: Dict[str, Any],
    method: str = "POST",
    additional_headers: Optional[Dict[str, str]] = None
) -> requests.Response:
    """
    Utility function to make API calls with proper authorization and content type headers.
    
    Args:
        url (str): The API endpoint URL
        request_body (Dict[str, Any]): The request body/payload
        method (str): HTTP method (default: POST)
        additional_headers (Optional[Dict[str, str]]): Any additional headers to include
    
    Returns:
        requests.Response: The response from the API call
    """
    # Get the API key from environment variables
    api_key = os.getenv('CRUSTDATA_API_KEY', 'placeholder_api_key_value')
    
    # Set up default headers
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Add any additional headers if provided
    if additional_headers:
        headers.update(additional_headers)
    
    # Make the API call based on the method
    if method.upper() == "GET":
        response = requests.get(url, headers=headers, params=request_body)
    elif method.upper() == "POST":
        response = requests.post(url, headers=headers, json=request_body)
    elif method.upper() == "PUT":
        response = requests.put(url, headers=headers, json=request_body)
    elif method.upper() == "DELETE":
        response = requests.delete(url, headers=headers, json=request_body)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    return response


def make_authenticated_request(
    url: str,
    data: Dict[str, Any],
    method: str = "POST"
) -> Dict[str, Any]:
    """
    Simplified wrapper for making authenticated API requests that returns JSON response.
    
    Args:
        url (str): The API endpoint URL
        data (Dict[str, Any]): The request data
        method (str): HTTP method (default: POST)
    
    Returns:
        Dict[str, Any]: The JSON response from the API
    
    Raises:
        requests.exceptions.RequestException: If the request fails
        ValueError: If the response is not valid JSON
    """
    response = make_api_call(url, data, method)
    
    # Raise an exception for bad status codes
    response.raise_for_status()
    
    try:
        return response.json()
    except ValueError as e:
        raise ValueError(f"Invalid JSON response: {e}")
