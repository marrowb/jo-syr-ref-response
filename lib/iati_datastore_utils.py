import requests
from typing import Optional, Dict, Any, Tuple, Union, List
from definitions import IATI_API_KEY



BASE_URL = "https://api.iatistandard.org/datastore"
ENDPOINTS = {
    "activity": "/activity/select",
    "activity_xml": "/activity/iati",
    "activity_json": "/activity/iati_json",
    "budget": "/budget/select",
    "transaction": "/transaction/select",

    "identifier_check": "/iati-identifiers/exist"
}


def create_request_session(
        api_key: Optional[str] = None,
        base_headers: Optional[Dict[str, str]] = None,
        timeout: int = 30
) -> requests.Session:
    """
    Create a configured requests session for the IATI Datastore API.

    Args:
        api_key: Optional API key for authentication (if required in future)
        base_headers: Optional dictionary of headers to include in all requests
        timeout: Default timeout for requests in seconds

    Returns:
        Configured requests.Session object

    Example:
        # Basic usage (current IATI API - no auth required)
        session = create_request_session()
        response = session.get(BASE_URL + ENDPOINTS["activity"], params={"q": "*"})

        # With custom headers
        session = create_request_session(base_headers={"User-Agent": "MyApp/1.0"})

        # If API key becomes required in future
        session = create_request_session(api_key="your-api-key")
    """
    session = requests.Session()

    # Set default headers
    headers = {}
    # headers = {
    #     "Content-Type": "application/json",
    #     "Accept": "application/json",
    #     "Cache-Control": "no-cache"
    # }

    # Add custom headers if provided
    if base_headers:
        headers.update(base_headers)

    # Add API key to headers if provided (for future use or other APIs)
    if api_key:
        headers["Ocp-Apim-Subscription-Key"] = api_key

    session.headers.update(headers)

    # Set default timeout
    session.timeout = timeout

    return session


def make_api_request(
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        session: Optional[requests.Session] = None,
        **kwargs
) -> requests.Response:
    """
    Generic function to make API requests to the IATI Datastore.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        endpoint: API endpoint path (e.g., "/activity/select")
        params: URL parameters for GET requests
        data: Data for POST/PUT requests (form data or string)
        json_data: JSON data for POST/PUT requests
        headers: Additional headers for this specific request
        session: Optional session object (will create new one if not provided)
        **kwargs: Additional arguments passed to requests

    Returns:
        requests.Response object

    Example:
        # GET request with query parameters
        response = make_api_request(
            method="GET",
            endpoint="/activity/select",
            params={"q": "description_narrative:water", "rows": 10}
        )

        # POST request with JSON data
        response = make_api_request(
            method="POST",
            endpoint="/iati-identifiers/exist",
            json_data={"iati_identifiers": ["GB-GOV-1-300123", "GB-GOV-1-300124"]}
        )

        # With custom session
        session = create_request_session()
        response = make_api_request(
            method="GET",
            endpoint="/budget/select",
            params={"q": "*", "rows": 5},
            session=session
        )
    """
    # Create session if not provided
    if session is None:
        session = create_request_session(api_key=IATI_API_KEY)

    # Build full URL
    url = BASE_URL + endpoint

    # Prepare request arguments
    request_kwargs = {
        "params": params,
        "headers": headers,
        **kwargs
    }

    # Add data/json based on what's provided
    if json_data is not None:
        request_kwargs["json"] = json_data
    elif data is not None:
        request_kwargs["data"] = data

    # Make the request
    response = session.request(method.upper(), url, **request_kwargs)

    # Raise for bad status codes
    response.raise_for_status()

    return response


def ping_api() -> bool:
    """
    Simple function to test API connectivity.

    Returns:
        True if API is reachable, False otherwise
    """
    try:
        response = make_api_request(
            method="GET",
            endpoint="/activity/select",
            params={"q": 'recipient_country_code:"JO"', "rows": 1}
        )
        return response.status_code == 200
    except Exception:
        return False


def get_docs(response: requests.Response) -> Dict:
    """
    Extract the docs from a response object
    """
    if not response:
        return None
    docs = response.json().get('response').get('docs')
    if not docs:
        return None
    else:
        return docs

def get_num_results(response: requests.Response) -> int:
    """
    Get total number of results from a query response
    """
    if not response:
        return None
    num_found = response.json().get('response').get('numFound')
    if not num_found:
        return None
    else:
        return num_found

def query_collection(
        collection_name: str,
        query_params: Dict[str, Any],
        preview: bool = False,
        fetch_all: bool = False,
        count_only: bool = False
        ) -> Tuple: 
    """
    Queries a specific collection in the IATI Datastore (e.g., activity, budget, transaction).
    This function is intended for 'select' type queries on collections.

    Args:
        collection_name: The name of the collection to query ("activity", "budget", "transaction").
        query_params: Dictionary of query parameters for the Solr request.
        fetch_all: If True, fetch all the documents.
        preview: If True, limits results to a small number (default 5 rows).
                 Overrides 'rows' in query_params if set.
        count_only: If True, sets 'rows' to 0 to fetch only the count of matching documents.
                    Overrides 'rows' in query_params and takes precedence over 'preview'.


    Returns:
        Tuple with count and Python dictionary with all the docs from the results

    Raises:
        ValueError: If the collection_name is not valid for querying (i.e., not in ENDPOINTS or not a select endpoint).
    """
    if collection_name not in ["activity", "budget", "transaction"]:
        raise ValueError(
            f"Invalid collection_name: {collection_name}. Must be 'activity', 'budget', or 'transaction' for this function."
        )

    endpoint = ENDPOINTS[collection_name] # Fetches e.g. "/activity/select"

    # Make a copy to modify params for this request
    effective_params = query_params.copy()

    if fetch_all:
        original_params = effective_params.copy()
        effective_params["rows"] = 0

        response = make_api_request("GET", endpoint, params=effective_params)
        num_results = get_num_results(response) 
        print(f"{num_results} found for query with parameters: \n{original_params}")

        all_docs = []
        original_params["rows"] = 1000
        while len(all_docs) < num_results:
            original_params["start"] = len(all_docs)
            print(f"Fetching results with offset {original_params["start"]}")
            response = make_api_request("GET", endpoint, params=original_params)
            docs = get_docs(response)
            if not docs:
                break # Retrieved all the results
            all_docs.extend(docs)
            print(f"Fetched {len(all_docs)} of {num_results} results")
    else:
        if count_only:
            effective_params["rows"] = 0
        elif preview:
            effective_params["rows"] = 5  # Default preview size
        response = make_api_request("GET", endpoint, params=effective_params)
        num_results = get_num_results(response) 
        all_docs = get_docs(response) 

    return (num_results, all_docs)


def check_identifiers(iati_identifiers: list) -> requests.Response:
    """Convenience function for checking if IATI identifiers exist."""
    return make_api_request(
        "POST",
        ENDPOINTS["identifier_check"],
        json_data={"iati_identifiers": iati_identifiers}
    )


# --- Query Builder Functions ---

def build_sector_query(sector_codes: List[str]) -> Optional[str]:
    """
    Builds a sector query string for the IATI API.
    Assumes DAC 5-digit sector codes (vocabulary 1).
    Example: sector_vocabulary_1_code:(<code> OR <code>)
    """
    if not sector_codes:
        return None
    codes_str = " OR ".join(f'"{code}"' for code in sector_codes)
    return f"sector_vocabulary_1_code:({codes_str})"


def build_humanitarian_scope_query(plan_codes: List[str]) -> Optional[str]:
    """
    Builds a humanitarian scope query string for FTS Plan Codes.
    Assumes Humanitarian Scope Vocabulary 2-1 for FTS Plan Codes.
    Example: (humanitarian_scope_vocabulary:"2-1" AND humanitarian_scope_code:(<code> OR <code>))
    """
    if not plan_codes:
        return None
    codes_str = " OR ".join(f'"{code}"' for code in plan_codes)
    return f'(humanitarian_scope_vocabulary:"2-1" AND humanitarian_scope_code:({codes_str}))'


def build_recipient_country_query(country_codes: List[str], include_transaction_recipients: bool = True) -> Optional[
    str]:
    """
    Builds a recipient country query string.
    Can include recipient countries at activity level and/or transaction level.
    Example: (recipient_country_code:(<JO>) OR transaction_recipient_country_code:(<JO>))
    """
    if not country_codes:
        return None
    country_codes_str = " OR ".join(f'"{code.upper()}"' for code in country_codes)
    activity_level_query = f"recipient_country_code:{country_codes_str}"
    if include_transaction_recipients:
        transaction_level_query = f"transaction_recipient_country_code:{country_codes_str}"
        return f"({activity_level_query} OR {transaction_level_query})"
    else:
        return activity_level_query


def build_transaction_type_query(transaction_types: List[str]) -> Optional[str]:
    """
    Builds a transaction type query string.
    Common types: 'C' (Commitment), 'D' (Disbursement).
    Full codelist: https://iatistandard.org/en/iati-standard/203/codelists/transactiontype/
    Example: transaction_type_code:(<D> OR <C>)
    """
    if not transaction_types:
        return None
    types_str = " OR ".join(f'"{ttype.upper()}"' for ttype in transaction_types)
    return f"transaction_type_code:({types_str})"


def build_combined_query(
        sector_codes: Optional[List[str]] = None,
        humanitarian_plan_codes: Optional[List[str]] = None,
        recipient_country_codes: Optional[List[str]] = None,
        include_transaction_recipients: bool = True,
        transaction_types: Optional[List[str]] = None,
        additional_query_params: Optional[str] = None,
        fl: Optional[List[str]] = None,
        wt: str = "json"
) -> Dict[str, Any]:
    """
    Builds a combined query dictionary for the IATI Datastore API.
    Args:
        sector_codes: List of DAC 5-digit sector codes.
        humanitarian_plan_codes: List of FTS Humanitarian Plan codes.
        recipient_country_codes: List of recipient country codes (e.g., "JO").
        include_transaction_recipients: If True, also search in transaction recipient countries.
        transaction_types: List of transaction type codes (e.g., "C", "D").
        additional_query_params: Any other raw query string to AND with the built query.
        fl: List of fields to return. If None, returns all fields.
        wt: Response writer type (default "json").

    Returns:
        A dictionary of parameters suitable for make_api_request or query_collection.
    """
    query_parts = []
    if sector_codes:
        sector_q = build_sector_query(sector_codes)
        if sector_q: query_parts.append(sector_q)
    if humanitarian_plan_codes:
        humanitarian_q = build_humanitarian_scope_query(humanitarian_plan_codes)
        if humanitarian_q: query_parts.append(humanitarian_q)
    if recipient_country_codes:
        country_q = build_recipient_country_query(recipient_country_codes, include_transaction_recipients)
        if country_q: query_parts.append(country_q)
    if transaction_types:
        transaction_q = build_transaction_type_query(transaction_types)
        if transaction_q: query_parts.append(transaction_q)
    if additional_query_params:
        query_parts.append(f"({additional_query_params})")

    final_query = "*:*" if not query_parts else " AND ".join(f"({part})" for part in query_parts)
    params = {"q": final_query, "wt": wt}
    if fl:
        params["fl"] = ",".join(fl)
    return params


if __name__ == "__main__":
    print(f"API Reachable: {ping_api()}")

    print("\n--- Example Combined Query using query_collection ---")
    example_params = build_combined_query(
        recipient_country_codes=["JO"],
        rows=5, # This will be overridden if preview=True or count_only=True
        fl=["iati_identifier", "title_narrative", "activity_status_code"]
    )
    print("Generated query parameters:")
    for key, value in example_params.items():
        print(f"  {key}: {value}")

    print("\nMaking example API request (normal):")
    try:
        response = query_collection("activity", example_params)
        print(f"Response Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Found {response_data.get('response', {}).get('numFound', 0)} activities.")
        # print("Response JSON (first few activities):")
        # for i, doc in enumerate(response_data.get("response", {}).get("docs", [])):
        #     if i < 2: print(f"  Activity {i+1}: {doc.get('iati_identifier')}")
        #     else: break
    except requests.exceptions.RequestException as e:
        print(f"Error during example API request: {e}")

    print("\nMaking example API request (preview):")
    try:
        # example_params_for_preview = example_params.copy() # query_collection makes its own copy
        response = query_collection("activity", example_params, preview=True)
        print(f"Response Status Code (preview): {response.status_code}")
        response_data = response.json()
        docs = response_data.get("response", {}).get("docs", [])
        print(f"Preview mode: Found {response_data.get('response', {}).get('numFound', 0)} total, showing {len(docs)} activities.")
        # for i, doc in enumerate(docs):
        #     print(f"  Preview Activity {i+1}: {doc.get('iati_identifier')}")
    except requests.exceptions.RequestException as e:
        print(f"Error during preview API request: {e}")

    print("\nMaking example API request (count_only):")
    try:
        # example_params_for_count = example_params.copy()
        response = query_collection("activity", example_params, count_only=True)
        print(f"Response Status Code (count_only): {response.status_code}")
        response_data = response.json()
        print(f"Count_only mode: Found {response_data.get('response', {}).get('numFound', 0)} activities. Documents expected: 0, got: {len(response_data.get('response', {}).get('docs', []))}")

    except requests.exceptions.RequestException as e:
        print(f"Error during count_only API request: {e}")

    print("\n--- Example Humanitarian Scope Query using query_collection ---")
    fts_example_params = build_combined_query(
        humanitarian_plan_codes=["HSDN18"],
        recipient_country_codes=["SD"],
        rows=3,
        fl=["iati_identifier", "title_narrative", "humanitarian_scope_code"]
    )
    print("Generated query parameters for humanitarian scope: ")
    for key, value in fts_example_params.items():
        print(f"  {key}: {value}")
    try:
        response = query_collection("activity", fts_example_params) # Normal query
        print(f"Response Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Found {response_data.get('response', {}).get('numFound', 0)} activities.")
    except requests.exceptions.RequestException as e:
        print(f"Error during example API request: {e}")
