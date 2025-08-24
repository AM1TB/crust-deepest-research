"""
Custom tools for the CrewAI research agent.
"""

import requests
import json
from crewai_tools import BaseTool


class TodoAPITool(BaseTool):
    name: str = "Todo API Tool"
    description: str = (
        "A tool to fetch todo items from the JSONPlaceholder API. "
        "This tool can retrieve todo information including user ID, title, and completion status. "
        "Useful for gathering sample data for research purposes."
    )

    def _run(self, todo_id: int = 1) -> str:
        """
        Fetch a todo item from the JSONPlaceholder API.
        
        Args:
            todo_id (int): The ID of the todo item to fetch (default: 1)
            
        Returns:
            str: JSON string containing the todo data or error message
        """
        try:
            url = f"https://jsonplaceholder.typicode.com/todos/{todo_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            todo_data = response.json()
            
            # Format the response for better readability
            formatted_data = {
                "userId": todo_data.get("userId"),
                "id": todo_data.get("id"),
                "title": todo_data.get("title"),
                "completed": todo_data.get("completed")
            }
            
            return json.dumps(formatted_data, indent=2)
            
        except requests.exceptions.RequestException as e:
            return f"Error fetching todo data: {str(e)}"
        except json.JSONDecodeError as e:
            return f"Error parsing JSON response: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"


class MultiTodoAPITool(BaseTool):
    name: str = "Multi Todo API Tool"
    description: str = (
        "A tool to fetch multiple todo items from the JSONPlaceholder API. "
        "Can retrieve all todos or todos for a specific user. "
        "Useful for comprehensive research and data analysis."
    )

    def _run(self, user_id: int = None, limit: int = 10) -> str:
        """
        Fetch multiple todo items from the JSONPlaceholder API.
        
        Args:
            user_id (int, optional): Filter todos by user ID
            limit (int): Maximum number of todos to fetch (default: 10)
            
        Returns:
            str: JSON string containing the todo data or error message
        """
        try:
            if user_id:
                url = f"https://jsonplaceholder.typicode.com/users/{user_id}/todos"
            else:
                url = "https://jsonplaceholder.typicode.com/todos"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            todos_data = response.json()
            
            # Limit the results
            limited_todos = todos_data[:limit] if isinstance(todos_data, list) else [todos_data]
            
            # Format for better readability
            formatted_todos = []
            for todo in limited_todos:
                formatted_todo = {
                    "userId": todo.get("userId"),
                    "id": todo.get("id"),
                    "title": todo.get("title"),
                    "completed": todo.get("completed")
                }
                formatted_todos.append(formatted_todo)
            
            return json.dumps(formatted_todos, indent=2)
            
        except requests.exceptions.RequestException as e:
            return f"Error fetching todos data: {str(e)}"
        except json.JSONDecodeError as e:
            return f"Error parsing JSON response: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
