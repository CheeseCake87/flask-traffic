def prevent_long_paths(path: str, max_length: int = 512) -> str:
    """
    Prevents the path from being too long.

    Default max length is 512 characters.
    """
    max_ = max(2, max_length if max_length > 0 else 512)

    if len(path) <= max_:
        return path

    half = max_ // 2
    return f"{path[:half]}...{path[-half:]}"
