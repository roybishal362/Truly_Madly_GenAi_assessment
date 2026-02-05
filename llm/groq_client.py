"""
Groq LLM Client using LangChain
Handles all LLM interactions with Llama 3 70B model
"""
import os
import json
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, ValidationError

class GroqLLMClient:
    """Wrapper for Groq API using LangChain"""
    
    def __init__(self):
        """Initialize Groq client with API key from environment"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Initialize LangChain ChatGroq with Llama 3.3 70B
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.1,  # Low temperature for consistent outputs
            max_tokens=2048
        )
    
    def generate_structured_output(
        self, 
        prompt: str, 
        output_model: type[BaseModel],
        system_message: str = "You are a helpful AI assistant."
    ) -> BaseModel:
        """
        Generate structured output using Pydantic model
        
        Args:
            prompt: User prompt
            output_model: Pydantic model class for output structure
            system_message: System context for the LLM
            
        Returns:
            Instance of output_model with parsed response
        """
        # Get the JSON schema from the Pydantic model
        schema = output_model.model_json_schema()
        schema_str = json.dumps(schema, indent=2)
        
        # Build the full prompt manually (no template variables)
        full_prompt = f"""{system_message}

You must respond with valid JSON that matches this schema:
{schema_str}

Important: Respond with ONLY valid JSON, no other text or markdown.

User request: {prompt}"""
        
        # Call LLM directly without template
        from langchain_core.messages import HumanMessage
        response = self.llm.invoke([HumanMessage(content=full_prompt)])
        response_text = response.content
        
        # Clean the response - remove markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON and validate with Pydantic
        try:
            data = json.loads(response_text)
            result = output_model(**data)
            return result
        except (json.JSONDecodeError, ValidationError) as e:
            # If parsing fails, provide helpful error
            raise ValueError(f"Failed to parse LLM response as {output_model.__name__}: {e}\nResponse: {response_text[:200]}")
    
    def generate_text(self, prompt: str, system_message: str = "You are a helpful AI assistant.") -> str:
        """
        Generate plain text response
        
        Args:
            prompt: User prompt
            system_message: System context
            
        Returns:
            Generated text response
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{prompt}")
        ])
        
        chain = prompt_template | self.llm
        response = chain.invoke({"prompt": prompt})
        
        return response.content
