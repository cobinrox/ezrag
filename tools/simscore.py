def similarity_score(metric_type: str, value: str) -> str:
    # Convert the second input to a float
    try:
        float_value = float(value)
    except ValueError:
        raise ValueError("The second input must be a string representing a numeric value.")

    # Define the maximum threshold for EUCLIDIAN and DOT_PRODUCT to normalize the score
    max_threshold = 2.0  # Adjust as needed based on your context

    # Calculate the percentage of closeness
    if metric_type == "EUCLIDIAN" or metric_type == "DOT_PRODUCT":
        if float_value < 0:
            return "0.00%"  # Negative values are not valid in this context, closest to 0%
        score = max(0.0, 100 * (1 - float_value / max_threshold))
    
    elif metric_type == "COSINE":
        if not (0 <= float_value <= 1):
            return "0.00%"  # Invalid value for cosine similarity, closest to 0%
        score = 100 * float_value
    
    else:
        raise ValueError("The first input must be 'EUCLIDIAN', 'DOT_PRODUCT', or 'COSINE'.")

    # Return the score as a formatted string rounded to 2 decimal places
    return f"{round(score, 2):.2f}%"

# Example usage:
print(similarity_score("EUCLIDIAN", "0.89"))  # e.g., "55.50%"
print(similarity_score("EUCLIDIAN", "1.49"))  # e.g., "25.50%"
print(similarity_score("COSINE", "0.95"))     # e.g., "95.00%"
