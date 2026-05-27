def clean_messages(input_messages):
    """
    Only strip tool_result blocks that don't have a 
    corresponding tool_use in the previous message.
    """
    dumped = [i.model_dump() for i in input_messages]
    
    # Collect all tool_use IDs from the conversation
    valid_tool_use_ids = set()
    for msg in dumped:
        content = msg.get("content", [])
        if isinstance(content, list):
            for block in content:
                if block.get("type") == "tool_use":
                    valid_tool_use_ids.add(block.get("id"))
    
    # Filter out tool_result blocks with no matching tool_use
    cleaned = []
    for msg in dumped:
        content = msg.get("content", [])
        if isinstance(content, list):
            filtered = [
                block for block in content
                if not (
                    block.get("type") == "tool_result" and
                    block.get("tool_use_id") not in valid_tool_use_ids
                )
            ]
            if filtered:
                msg["content"] = filtered
                cleaned.append(msg)
            elif msg.get("role") == "user":
                # Keep user messages even if content is empty
                cleaned.append(msg)
        else:
            cleaned.append(msg)
    
    return cleaned
