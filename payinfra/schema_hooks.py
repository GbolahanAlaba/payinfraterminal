

def count_endpoints(result, generator, request, public):
    """Custom hook to count endpoints and add it to API description"""
    total_endpoints = len(result.get("paths", {}))
    current_desc = result["info"].get("description", "")
    result["info"]["description"] = (
        current_desc + f"\n\n**Total API endpoints:** {total_endpoints}"
    )
    return result


def add_app_tags(result, generator, request, public):
    """
    Safely add tags based on URL path and FORCE OVERWRITE any existing tags.
    """
    paths = result.get("paths", {})

    for path, methods in paths.items():

        # default tag
        app_label = "API"

        # try to extract the app name from the path: /v1/{app}/...
        parts = path.strip("/").split("/")

        if len(parts) >= 2:
            app_label = parts[1].capitalize()

        for method, operation in methods.items():

            # Only process real HTTP methods
            if method.lower() not in ["get", "post", "put", "patch", "delete", "options", "head"]:
                continue

            if not isinstance(operation, dict):
                continue

            # FORCE OVERWRITE tags
            operation["tags"] = [app_label]

    return result

