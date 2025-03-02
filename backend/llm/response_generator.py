"""
Response generation module.

Handles the generation of responses using Google's Gemini API with proper legal formatting.
"""
import os
import re
from typing import Dict, Tuple, Any, List
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)

def call_llm(prompt: str) -> str:
    """
    Call the Gemini 2.0 Flash API to generate a response.
    
    Args:
        prompt: The formatted prompt with query and context
        
    Returns:
        The generated response from Gemini
    """
    try:
        # Use Gemini-2.0-flash model as it's fast and cost-effective
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Return the text of the response
        return response.text
        
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        # Fallback response in case of API error
        return "I encountered an error while processing your query. Please try again later."

def construct_prompt(query: str, context: Dict) -> str:
    """
    Construct a prompt for the LLM with query and context.
    
    Args:
        query: The user's question
        context: The assembled context with source attribution
        
    Returns:
        Formatted prompt for the LLM
    """
    prompt = f"""You are a legal assistant providing accurate information from legal documents. 
Answer the following query based ONLY on the provided context. 
If the information is not present in the context, respond with "I don't have enough information to answer this question based on the provided documents."

Format your answer in a professional legal style with proper citations. 
Use citation format [Source X] to refer to sources.
If directly quoting, use quotation marks and include the citation.
Be concise but thorough.

QUERY: {query}

CONTEXT:
{context['text']}

ANSWER:
"""
    return prompt

def extract_citations(response: str) -> list:
    """
    Extract source citations from the response.
    
    Args:
        response: The generated response from the LLM
        
    Returns:
        List of citation references
    """
    # Regular expression to find citation references like [Source 1], [Source 2], etc.
    citation_pattern = r'\[Source (\d+)\]'
    citations = re.findall(citation_pattern, response)
    
    # Convert to integers and remove duplicates
    return list(set(int(citation) - 1 for citation in citations))

def estimate_confidence(response: str, citations: list, context: Dict) -> float:
    """
    Estimate the confidence level of the generated response.
    
    Args:
        response: The generated response
        citations: List of citation references
        context: The context used for generation
        
    Returns:
        Confidence score (0.0 to 1.0)
    """
    # Base confidence on:
    # 1. Number of citations (more citations = higher confidence)
    # 2. Relevance scores of cited sources
    # 3. Presence of uncertainty markers in the response
    
    # Get number of unique citations
    citation_count = len(citations)
    
    # If no citations, low confidence
    if citation_count == 0:
        return 0.3
    
    # Get average relevance score of cited sources
    avg_relevance = 0.0
    if citations and context['sources']:
        relevance_scores = [context['sources'][i]['relevance_score'] for i in citations if i < len(context['sources'])]
        if relevance_scores:
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
    
    # Check for uncertainty markers
    uncertainty_markers = ['may', 'might', 'could', 'possibly', 'perhaps', 'unclear', 'uncertain']
    uncertainty_count = sum(1 for marker in uncertainty_markers if marker in response.lower())
    
    # Calculate confidence score (simplified formula)
    confidence = 0.5 + (0.1 * min(citation_count, 5)) + (0.3 * avg_relevance) - (0.05 * uncertainty_count)
    
    # Ensure confidence is between 0 and 1
    return max(0.0, min(1.0, confidence))

def format_response(response: str) -> str:
    """
    Format the response with proper legal citation formatting.
    
    Args:
        response: The raw response from the LLM
        
    Returns:
        Formatted response
    """
    # Replace citation markers with superscript-style formatting
    citation_pattern = r'\[Source (\d+)\]'
    formatted_response = re.sub(citation_pattern, r'[\\1]', response)
    
    return formatted_response

def verify_against_sources(response: str, context: Dict) -> str:
    """
    Verify the response against source material to reduce hallucinations.
    
    Args:
        response: The generated response
        context: The context used for generation
        
    Returns:
        Verified response with corrections if needed
    """
    # Extract facts from response (simplified implementation)
    # In a production environment, this would use more sophisticated fact-checking
    
    # For now, we'll just check if any significant claims in the response 
    # aren't supported by the context
    if not any(part.lower() in context['text'].lower() for part in response.split('.')):
        # Append a disclaimer if content seems ungrounded
        response += "\n\nNote: The information provided is based on the available documents, but you may want to verify with additional sources."
    
    return response

def generate_response(query: str, context: Dict) -> Tuple[str, float]:
    """
    Generate a response to a query using Gemini LLM with the provided context.
    
    Args:
        query: The user's question
        context: The assembled context with source attribution
        
    Returns:
        Tuple of (response, confidence_score)
    """
    # Construct prompt
    prompt = construct_prompt(query, context)
    
    # Call LLM
    response = call_llm(prompt)
    
    # Extract citations
    citations = extract_citations(response)
    
    # Verify response against sources
    verified_response = verify_against_sources(response, context)
    
    # Format response
    formatted_response = format_response(verified_response)
    
    # Estimate confidence
    confidence = estimate_confidence(formatted_response, citations, context)
    
    return formatted_response, confidence
