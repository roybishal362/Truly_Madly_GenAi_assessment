"""
Configuration loader for environment variables
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_env_variable(var_name: str, required: bool = True) -> str:
    """
    Get environment variable with validation
    
    Args:
        var_name: Name of environment variable
        required: Whether variable is required
        
    Returns:
        Environment variable value
        
    Raises:
        ValueError: If required variable is missing
    """
    value = os.getenv(var_name)
    
    if required and not value:
        raise ValueError(
            f"{var_name} not found in environment variables. "
            f"Please check your .env file."
        )
    
    return value
