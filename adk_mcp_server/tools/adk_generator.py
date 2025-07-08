import logging
import ast
import google.genai as genai, types
from mcp.server.fastmcp import FastMCP

from adk_mcp_server.settings import settings
from adk_mcp_server.services.rag_service import rag_service # Import the RAG service

logger = logging.getLogger(__name__)
TOOL_NAME = "generate_adk_agent"

def register_tool(mcp: FastMCP):
    @mcp.tool(name=TOOL_NAME)
    def generate_adk_agent(prompt: str) -> str:
        logger.info(f"Received prompt to generate ADK agent: '{prompt}'")
        try:
            # Step 1: Retrieve relevant context using RAG
            retrieved_context = rag_service.search(prompt)

            # Step 2: Construct the meta-prompt with the retrieved context
            meta_prompt = _get_adk_meta_prompt(prompt, retrieved_context)
            
            logger.info("Calling the generative model with RAG context...")
            generated_code = _generate_code(meta_prompt)
            logger.info("Code generation successful.")

            if not _is_syntax_valid(generated_code):
                logger.warning(f"Generated code failed syntax validation. Code:\n{generated_code}")
                return "Error: The model generated code with a syntax error. Please try a more specific prompt."

            logger.info("Generated code passed syntax validation.")
            return f"```python\n{generated_code}\n```"
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            return f"Error: An internal server error occurred. Details: {e}"

def _get_adk_meta_prompt(user_prompt: str, retrieved_context: list[str]) -> str:
    """Constructs the system prompt, now including a section for RAG context."""
    
    context_section = "No retrieved examples."
    if retrieved_context:
        formatted_context = "\n\n---\n\n".join(retrieved_context)
        context_section = f"""
        --- RETRIEVED EXAMPLES (Use these for inspiration) ---
        You MUST prioritize using patterns from these retrieved examples if they are relevant to the user's request.

        {formatted_context}
        --- END OF RETRIEVED EXAMPLES ---
        """

    return f"""
    You are a world-class expert Python developer specializing in the Google Agent Development Kit (ADK).
    Your sole task is to generate a complete, single-file, production-quality Python script for a Google ADK agent based on the user's request.
    You must analyze the user's prompt to determine if they need a simple agent, an agent with memory, a hierarchy of agents (A2A), or a multi-step workflow.

    {context_section}

    **CRITICAL INSTRUCTIONS FOR GENERATING THE CODE:**
    1.  **RAW PYTHON ONLY:** The output MUST be a single, complete Python script. Do NOT output any conversational text, explanations, or markdown formatting (like ```python). Only raw Python code.
    2.  **ENTRY POINT:** The final agent or workflow to be run MUST be assigned to a variable named `root_agent`. This is a strict requirement for the `adk run` command.
    3.  **IMPORTS:** Always include ALL necessary imports at the top, e.g., `from google.adk import agents, llms, tools, memory, workflow`.
    4.  **LLM CONFIGURATION:** Always set the LLM for agents using `llm=llms.Llm(model="{settings.llm_model_name}")`.
    5.  **DOCUMENTATION:** Include clear docstrings for agents, tools, and functions. Add inline comments for complex logic.
    6.  **TOOL DEFINITIONS:** If a request implies an external capability (e.g., API call, calculation), define a Python function with type hints and wrap it as a `tools.FunctionTool`.

    **Based on the retrieved examples and the guide below, analyze the following user request carefully and generate the complete, raw Python script.**

    **User Request:**
    "{user_prompt}"
    """

def _generate_code(prompt: str) -> str:
    # This function remains the same as before
    client = genai.Client()
    generation_config = types.GenerateContentConfig(temperature=0.2) # Lower temp as RAG provides creativity
    response = client.models.generate_content(prompt, config=generation_config)
    return response.text.strip()

def _is_syntax_valid(code: str) -> bool:
    # This function remains the same as before
    if not code:
        logger.warning("Syntax validation failed: Generated code is empty.")
        return False
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        logger.error(f"Syntax validation failed: {e}", exc_info=True)
        return False