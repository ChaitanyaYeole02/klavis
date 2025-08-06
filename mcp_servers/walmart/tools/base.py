import logging
import os

from contextvars import ContextVar
from typing import Optional

from dotenv import load_dotenv

# Load env vars from .env
load_dotenv()

logger = logging.getLogger(__name__)

# Context variable to store the auth token per request
auth_token_context: ContextVar[str] = ContextVar('auth_token')

def get_auth_token() -> str:
    """
    Get the Walmart API token from context or fallback to env.
    """
    try:
        token = auth_token_context.get()
        if not token:
            # Fallback to environment variable
            token = os.getenv("WALMART_API_KEY")
            logger.debug(f"Using token from environment: {token}")
            if not token:
                raise RuntimeError("No Walmart auth token found in context or environment")
        return token
    except LookupError:
        # Context variable not set at all
        token = os.getenv("WALMART_API_KEY")
        if not token:
            raise RuntimeError("No Walmart auth token found in context or environment")
        return token

def get_walmart_client() -> Optional[str]:
    """
    Return a Walmart client config ready to use.
    """
    try:
        auth_token = get_auth_token()
        return auth_token
    except RuntimeError as e:
        logger.warning(f"Failed to get Walmart auth token: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Walmart client: {e}")
        return None 