"""Highflame LLM integration (unified provider for OpenAI and Google/Gemini)."""

import os
from langchain_openai import ChatOpenAI
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_llm(temperature: float = 0.8):
    """
    Get configured LLM via Highflame.

    Args:
        provider: Ignored - always uses Highflame. Kept for API compatibility.
        temperature: Temperature for sampling (default: 0.8)

    Returns:
        Configured LLM instance via Highflame

    Raises:
        ValueError: If API key not set
    """
    logger.debug(f"Getting LLM instance - temperature: {temperature}")

    # Highflame integration (always uses Highflame)
    highflame_api_key = os.getenv("HIGHFLAME_API_KEY")
    if not highflame_api_key:
        logger.error("HIGHFLAME_API_KEY not set in environment variables")
        raise ValueError("HIGHFLAME_API_KEY not set in environment variables")

    # Read route and model from env vars
    route = os.getenv("HIGHFLAME_ROUTE", "").strip()
    model = os.getenv("MODEL", "").strip()
    llm_api_key = os.getenv("LLM_API_KEY", "").strip()
    
    # Route is required
    if not route:
        logger.error("HIGHFLAME_ROUTE not set in environment variables")
        raise ValueError("HIGHFLAME_ROUTE must be set (e.g., 'openai' or 'google')")
    
    # Model is required
    if not model:
        logger.error("MODEL not set in environment variables")
        raise ValueError("MODEL must be set (e.g., 'gpt-4o-mini' or 'gemini-2.5-flash-lite')")
    
    # LLM API key is required
    if not llm_api_key:
        logger.error("LLM_API_KEY not set in environment variables")
        raise ValueError("LLM_API_KEY must be set (OpenAI API key for 'openai' route, Gemini API key for 'google' route)")
    
    logger.info(f"Initializing Highflame LLM - route: {route}, model: {model}")
    
    # Highflame provides a unified OpenAI-compatible API for both OpenAI and Gemini
    return ChatOpenAI(
        model=model,
        base_url="https://api.highflame.app/v1",
        api_key=llm_api_key,
        default_headers={
            "X-Javelin-apikey": highflame_api_key,
            "X-Javelin-route": route,
        },
        temperature=temperature,
    )
