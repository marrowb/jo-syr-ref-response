import hashlib
import json


def add_unique_ids(activities):
    """Add unique IDs to activities based on their content."""
    seen_hashes = set()

    for i, activity in enumerate(activities):
        # Create a hash of the dictionary content
        content_str = json.dumps(activity, sort_keys=True, default=str)
        content_hash = hashlib.md5(content_str.encode()).hexdigest()

        # Handle duplicates by appending counter
        original_hash = content_hash
        counter = 1
        while content_hash in seen_hashes:
            content_hash = f"{original_hash}_{counter}"
            counter += 1

        seen_hashes.add(content_hash)
        activity["unique_id"] = content_hash

        # Progress indicator for large datasets
        if i % 1000 == 0:
            print(f"Processed {i}/9188 activities")

    return activities
