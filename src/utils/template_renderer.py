def render_template(template: str, context: dict) -> str:
    """
    Render a string template with placeholders using the provided context.

    Args:
        template (str): The string template with placeholders (e.g., "{field_name}").
        context (dict): A dictionary containing field names and their values.

    Returns:
        str: The rendered string with placeholders replaced by context values.
    """
    try:
        return template.format(**context)
    except KeyError as e:
        raise ValueError(f"Missing placeholder in context: {e}")
