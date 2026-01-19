import requests, time, json, re
from typing import List, Dict
from model import EmailPreview

BASE_URL = "https://gmail.googleapis.com/gmail/v1"
BATCH_BASE_URL = "https://gmail.googleapis.com/batch/gmail/v1"

def get_recent_thread_ids(access_token: str, max_results: int = 30) -> Dict:
    """
    List thread IDs for threads with messages in the last 24 hours.
    """
    url = f"{BASE_URL}/users/me/threads"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "q": "newer_than:1d",
        "maxResults": max_results
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    return data['threads']

def batch_get_threads(access_token: str, headers: Dict, batch_body: str) -> Dict:
    """
    Get detailed info for a specific thread (all messages).
    """
    url = f"{BATCH_BASE_URL}"

    # You can choose "format" like "full" or "metadata"; default returns full payload.

    response = requests.post(url, headers=headers, data=batch_body)
    response.raise_for_status()
    return response

def get_all_threads(access_token: str, max_threads: int = 30) -> Dict:
    """
    Fetch recent threads (last 24h) including all messages per thread.
    """
    threads = get_recent_thread_ids(access_token, max_threads)
    
    boundary = f"batch_{int(time.time() * 1000)}"
    
    batch_body = ""
    for index, thread in enumerate(threads, start=1):
        batch_body += f"--{boundary}\n"
        batch_body += f"Content-Type: application/http\n"
        batch_body += f"Content-ID: <request-{index}>\n\n"
        batch_body += (
            f"GET /gmail/v1/users/me/threads/{thread.get('id')}"
            f"?format=full HTTP/1.1\n\n"
        )
    
    batch_body += f"--{boundary}--\n"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": f"multipart/mixed; boundary={boundary}",
    }
    
    data = batch_get_threads(access_token, headers, batch_body)   
    
    threads = parse_gmail_batch_response(data)
    emails = extract_email_content(threads)

    return emails

def parse_gmail_batch_response(response) -> List[Dict]:
    """
    Parses a Gmail batch response and returns a list of thread objects.
    """

    content_type = response.headers.get("Content-Type", "")
    boundary = extract_boundary(content_type)

    raw = response.text
    parts = raw.split(f"--{boundary}")

    threads = []

    for part in parts:
        part = part.strip()

        if not part or part == "--":
            continue

        # Each part contains a full HTTP response
        if "HTTP/1.1 200" not in part:
            continue  # skip failed requests

        # JSON starts after the first empty line following headers
        try:
            json_start = part.index("{")
            json_body = part[json_start:]
            thread = json.loads(json_body)
            threads.append(thread)
        except Exception:
            continue

    return threads

def extract_boundary(content_type: str) -> str:
    match = re.search(r'boundary=([^\s;]+)', content_type)
    if not match:
        raise ValueError("Boundary not found in Content-Type")
    return match.group(1)

def extract_email_content(threads: List[Dict]) -> List[Dict]:
    emails = []
    for thread in threads:
        for message in thread['messages']:
            from_email, subject = extract_from_and_subject(message)
            emails.append(EmailPreview(
                id=message['id'],
                thread_id=message['threadId'],
                snippet=message['snippet'],
                from_=from_email,
                subject=subject
            ))
    return emails

def extract_headers(message: dict) -> dict:
    headers = message.get("payload", {}).get("headers", [])
    return {h["name"]: h["value"] for h in headers}

def extract_from_and_subject(message: dict) -> tuple[str | None, str | None]:
    header_map = extract_headers(message)

    from_email = header_map.get("From")
    subject = header_map.get("Subject")

    return from_email, subject