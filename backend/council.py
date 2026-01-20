"""3-stage LLM Council orchestration."""

from typing import List, Dict, Any, Tuple
from .openrouter import query_models_parallel, query_model
from .config import COUNCIL_MODELS, CHAIRMAN_MODEL


async def stage1_collect_responses(user_query: str) -> List[Dict[str, Any]]:
    """
    Stage 1: Collect individual responses from all council models.

    Args:
        user_query: The user's question

    Returns:
        List of dicts with 'model' and 'response' keys
    """
    messages = [{"role": "user", "content": user_query}]

    # Query all models in parallel
    responses = await query_models_parallel(COUNCIL_MODELS, messages)

    # Format results
    stage1_results = []
    for model, response in responses.items():
        if response is not None:  # Only include successful responses
            stage1_results.append({
                "model": model,
                "response": response.get('content', '')
            })

    return stage1_results


async def stage2_collect_rankings(
    user_query: str,
    stage1_results: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Stage 2: Each model ranks the anonymized responses.

    Args:
        user_query: The original user query
        stage1_results: Results from Stage 1

    Returns:
        Tuple of (rankings list, label_to_model mapping)
    """
    # Create anonymized labels for responses (Response A, Response B, etc.)
    labels = [chr(65 + i) for i in range(len(stage1_results))]  # A, B, C, ...

    # Create mapping from label to model name
    label_to_model = {
        f"Response {label}": result['model']
        for label, result in zip(labels, stage1_results)
    }

    # Build the ranking prompt
    responses_text = "\n\n".join([
        f"Response {label}:\n{result['response']}"
        for label, result in zip(labels, stage1_results)
    ])

    ranking_prompt = f"""You are evaluating different responses to the following question:

Question: {user_query}

Here are the responses from different models (anonymized):

{responses_text}

Your task:
1. First, evaluate each response individually. For each response, explain what it does well and what it does poorly.
2. Then, at the very end of your response, provide a final ranking.

IMPORTANT: Your final ranking MUST be formatted EXACTLY as follows:
- Start with the line "FINAL RANKING:" (all caps, with colon)
- Then list the responses from best to worst as a numbered list
- Each line should be: number, period, space, then ONLY the response label (e.g., "1. Response A")
- Do not add any other text or explanations in the ranking section

Example of the correct format for your ENTIRE response:

Response A provides good detail on X but misses Y...
Response B is accurate but lacks depth on Z...
Response C offers the most comprehensive answer...

FINAL RANKING:
1. Response C
2. Response A
3. Response B

Now provide your evaluation and ranking:"""

    messages = [{"role": "user", "content": ranking_prompt}]

    # Get rankings from all council models in parallel
    responses = await query_models_parallel(COUNCIL_MODELS, messages)

    # Format results
    stage2_results = []
    for model, response in responses.items():
        if response is not None:
            full_text = response.get('content', '')
            parsed = parse_ranking_from_text(full_text)
            stage2_results.append({
                "model": model,
                "ranking": full_text,
                "parsed_ranking": parsed
            })

    return stage2_results, label_to_model


async def stage3_synthesize_final(
    user_query: str,
    stage2_5_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Stage 3: Chairman synthesizes final response.

    Args:
        user_query: The original user query
        stage2_5_results: Self-corrected responses from Stage 2.5 (after peer feedback)
        stage2_results: Rankings from Stage 2

    Returns:
        Dict with 'model' and 'response' keys
    """
    # Build comprehensive context for chairman using corrected responses
    stage2_5_text = "\n\n".join([
        f"Model: {result['model']}\nCorrected Response: {result['corrected_response']}"
        for result in stage2_5_results
    ])

    stage2_text = "\n\n".join([
        f"Model: {result['model']}\nRanking: {result['ranking']}"
        for result in stage2_results
    ])

    chairman_prompt = f"""You are the Chairman of an LLM Council. Multiple AI models have provided responses to a user's question, received peer feedback, and then corrected their responses based on that feedback.

Original Question: {user_query}

STAGE 2.5 - Corrected Responses (after peer review):
{stage2_5_text}

STAGE 2 - Peer Rankings:
{stage2_text}

Your task as Chairman is to synthesize all of this information into a single, comprehensive, accurate answer to the user's original question. Consider:
- The corrected responses that have incorporated peer feedback
- The peer rankings and what they reveal about response quality
- Any patterns of agreement or disagreement

Provide a clear, well-reasoned final answer that represents the council's collective wisdom:"""

    messages = [{"role": "user", "content": chairman_prompt}]

    # Query the chairman model
    response = await query_model(CHAIRMAN_MODEL, messages)

    if response is None:
        # Fallback if chairman fails
        return {
            "model": CHAIRMAN_MODEL,
            "response": "Error: Unable to generate final synthesis."
        }

    return {
        "model": CHAIRMAN_MODEL,
        "response": response.get('content', '')
    }


def parse_ranking_from_text(ranking_text: str) -> List[str]:
    """
    Parse the FINAL RANKING section from the model's response.

    Args:
        ranking_text: The full text response from the model

    Returns:
        List of response labels in ranked order
    """
    import re

    # Look for "FINAL RANKING:" section
    if "FINAL RANKING:" in ranking_text:
        # Extract everything after "FINAL RANKING:"
        parts = ranking_text.split("FINAL RANKING:")
        if len(parts) >= 2:
            ranking_section = parts[1]
            # Try to extract numbered list format (e.g., "1. Response A")
            # This pattern looks for: number, period, optional space, "Response X"
            numbered_matches = re.findall(r'\d+\.\s*Response [A-Z]', ranking_section)
            if numbered_matches:
                # Extract just the "Response X" part
                return [re.search(r'Response [A-Z]', m).group() for m in numbered_matches]

            # Fallback: Extract all "Response X" patterns in order
            matches = re.findall(r'Response [A-Z]', ranking_section)
            return matches

    # Fallback: try to find any "Response X" patterns in order
    matches = re.findall(r'Response [A-Z]', ranking_text)
    return matches


def format_peer_critiques(
    model: str,
    stage2_results: List[Dict[str, Any]]
) -> str:
    """
    Format peer critiques for a specific model, excluding its own evaluation.

    Args:
        model: The model identifier to get critiques for
        stage2_results: Results from Stage 2 (peer rankings/evaluations)

    Returns:
        Formatted string containing all peer evaluations with attribution
    """
    critiques = []
    
    for result in stage2_results:
        # Skip the model's own evaluation (models shouldn't see their own critique)
        if result['model'] == model:
            continue
        
        critic_model = result['model']
        critique_text = result['ranking']
        
        critiques.append(f"Peer evaluation from {critic_model}:\n{critique_text}")
    
    return "\n\n".join(critiques)


def build_correction_prompt(
    user_query: str,
    original_response: str,
    peer_critiques: str
) -> str:
    """
    Build the Stage 2.5 correction prompt for a model.

    Args:
        user_query: The original user question
        original_response: The model's original Stage 1 response
        peer_critiques: Formatted peer feedback text

    Returns:
        The prompt string for the correction request
    """
    return f"""You previously answered a question, and your peers have provided feedback on your response.

Original Question: {user_query}

Your Original Answer:
{original_response}

Peer Feedback:

{peer_critiques}

Based on this feedback from your peers, please provide a corrected and improved version of your response. Address the valid criticisms and incorporate any useful suggestions while maintaining the strengths of your original answer.

Corrected Response:"""


def calculate_aggregate_rankings(
    stage2_results: List[Dict[str, Any]],
    label_to_model: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Calculate aggregate rankings across all models.

    Args:
        stage2_results: Rankings from each model
        label_to_model: Mapping from anonymous labels to model names

    Returns:
        List of dicts with model name and average rank, sorted best to worst
    """
    from collections import defaultdict

    # Track positions for each model
    model_positions = defaultdict(list)

    for ranking in stage2_results:
        ranking_text = ranking['ranking']

        # Parse the ranking from the structured format
        parsed_ranking = parse_ranking_from_text(ranking_text)

        for position, label in enumerate(parsed_ranking, start=1):
            if label in label_to_model:
                model_name = label_to_model[label]
                model_positions[model_name].append(position)

    # Calculate average position for each model
    aggregate = []
    for model, positions in model_positions.items():
        if positions:
            avg_rank = sum(positions) / len(positions)
            aggregate.append({
                "model": model,
                "average_rank": round(avg_rank, 2),
                "rankings_count": len(positions)
            })

    # Sort by average rank (lower is better)
    aggregate.sort(key=lambda x: x['average_rank'])

    return aggregate


async def stage2_5_collect_corrections(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Stage 2.5: Each model corrects its response based on peer feedback.

    Args:
        user_query: The original user query
        stage1_results: Individual model responses from Stage 1
        stage2_results: Peer rankings/evaluations from Stage 2

    Returns:
        List of dicts with model, original_response, peer_critiques, and corrected_response
    """
    import asyncio
    
    # Build correction tasks for each model
    tasks = []
    task_metadata = []
    
    for stage1_result in stage1_results:
        model = stage1_result['model']
        original_response = stage1_result['response']
        
        # Collect peer critiques (exclude self-evaluation)
        peer_critiques = format_peer_critiques(model, stage2_results)
        
        # Build correction prompt
        prompt = build_correction_prompt(user_query, original_response, peer_critiques)
        messages = [{"role": "user", "content": prompt}]
        
        # Create async task for this model
        tasks.append(query_model(model, messages))
        task_metadata.append({
            'model': model,
            'original_response': original_response,
            'peer_critiques': peer_critiques
        })
    
    # Query all models in parallel
    responses = await asyncio.gather(*tasks)
    
    # Format results with fallback to original response if model fails
    stage2_5_results = []
    for i, metadata in enumerate(task_metadata):
        response = responses[i]
        
        # Use corrected response if available, otherwise fall back to original
        if response is not None:
            corrected_response = response.get('content', metadata['original_response'])
        else:
            corrected_response = metadata['original_response']
        
        stage2_5_results.append({
            'model': metadata['model'],
            'original_response': metadata['original_response'],
            'peer_critiques': metadata['peer_critiques'],
            'corrected_response': corrected_response
        })
    
    return stage2_5_results


async def generate_conversation_title(user_query: str) -> str:
    """
    Generate a short title for a conversation based on the first user message.

    Args:
        user_query: The first user message

    Returns:
        A short title (3-5 words)
    """
    title_prompt = f"""Generate a very short title (3-5 words maximum) that summarizes the following question.
The title should be concise and descriptive. Do not use quotes or punctuation in the title.

Question: {user_query}

Title:"""

    messages = [{"role": "user", "content": title_prompt}]

    # Use gemini-2.5-flash for title generation (fast and cheap)
    response = await query_model("google/gemini-2.5-flash", messages, timeout=30.0)

    if response is None:
        # Fallback to a generic title
        return "New Conversation"

    title = response.get('content', 'New Conversation').strip()

    # Clean up the title - remove quotes, limit length
    title = title.strip('"\'')

    # Truncate if too long
    if len(title) > 50:
        title = title[:47] + "..."

    return title


async def run_full_council(user_query: str) -> Tuple[List, List, List, Dict, Dict]:
    """
    Run the complete council process including Stage 2.5.

    Args:
        user_query: The user's question

    Returns:
        Tuple of (stage1_results, stage2_results, stage2_5_results, stage3_result, metadata)
    """
    # Stage 1: Collect individual responses
    stage1_results = await stage1_collect_responses(user_query)

    # If no models responded successfully, return error
    if not stage1_results:
        return [], [], [], {
            "model": "error",
            "response": "All models failed to respond. Please try again."
        }, {}

    # Stage 2: Collect rankings
    stage2_results, label_to_model = await stage2_collect_rankings(user_query, stage1_results)

    # Calculate aggregate rankings
    aggregate_rankings = calculate_aggregate_rankings(stage2_results, label_to_model)

    # Stage 2.5: Collect self-corrections based on peer feedback
    stage2_5_results = await stage2_5_collect_corrections(user_query, stage1_results, stage2_results)

    # Stage 3: Synthesize final answer (now uses Stage 2.5 corrected responses)
    stage3_result = await stage3_synthesize_final(
        user_query,
        stage2_5_results,
        stage2_results
    )

    # Prepare metadata
    metadata = {
        "label_to_model": label_to_model,
        "aggregate_rankings": aggregate_rankings
    }

    return stage1_results, stage2_results, stage2_5_results, stage3_result, metadata
