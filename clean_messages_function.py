def clean_messages(input_messages):
    """
    Filter out tool_result blocks from conversation history.
    Prevents multi-turn errors when tool_use blocks from 
    previous turns are missing.
    """
    cleaned = []
    for msg in input_messages:
        dumped = msg.model_dump()
        role = dumped.get("role", "")
        content = dumped.get("content", [])

        if role == "user":
            cleaned.append(dumped)
        elif role == "assistant":
            if isinstance(content, list):
                text_only = [c for c in content if c.get("type") == "text"]
                if text_only:
                    dumped["content"] = text_only
                    cleaned.append(dumped)
            elif isinstance(content, str) and content:
                cleaned.append(dumped)
    return cleaned
