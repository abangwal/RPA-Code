from uuid import uuid4
from browser.play import PlayBrowser
from llm.agents import CSS_Selector
from processor.html_processor import clean_html_for_llm_v2, extract_data_content

import json
import sys
import pandas as pd

dropbox_credentials = {
    "email": "ashishbangwal161@gmail.com",
    "password": "Ashish@12345",
}

trello_credentials = {
    "email": "ashishbangwal161@gmail.com",
    "password": "ashishbangwal@12345",
}

dropbox_steps = [
    ("Enter email and continue", "action"),
    ("Enter password and continue", "action"),
    ("Extract files table", "extract"),
]


trello_steps = [
    ("Enter email and continue", "action"),
    ("Enter password and continue", "action"),
    ("Click trello app link", "action"),
    ("https://trello.com/w/userworkspace21117702/members", "url_hop"),
    ("Extract members data", "extract"),
]

browser = PlayBrowser()
selector = CSS_Selector()

at_url = "https://id.atlassian.com/login"
dropbox_url = "https://dropbox.com/login"


def json_to_csv_single(json_data, filename):
    """Convert single table JSON to CSV"""
    # If json_data is string, parse it
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    # Create DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Saved single table to {filename}")

    return df


def run_workflow(wf_name: str):
    ans = []
    if wf_name == "trello":
        url = at_url
        cred = trello_credentials
        steps = trello_steps

    else:
        url = dropbox_url
        cred = dropbox_credentials
        steps = dropbox_steps

    html = browser.visit_page(url)
    for step in steps:
        task, process = step
        html = browser.page.content()
        clean_html = clean_html_for_llm_v2(html)

        if process == "action":
            response = selector.get_actions(clean_html, task)
            response = json.loads(response)
            print("LLM Actions for current page:")
            print(json.dumps(response, indent=2))
            for action_data in response["actions"]:
                browser.perform_action(action_data, cred)

        elif process == "extract":
            # More comprehensive data structure selectors
            browser.page.wait_for_selector(
                "table, ul, ol, div[class*='table'], div[class*='list'], div[class*='grid'], "
                "[role='table'], [role='list'], [role='grid'], .data-table, .results",
                timeout=10000,
            )
            tabels = extract_data_content(clean_html)
            response = selector.extract_data(tabels, task)
            response = json.loads(response)
            print("LLM Actions for current page:")
            print(json.dumps(response, indent=2))
            json_to_csv_single(response, f"{uuid4()}.csv")

        elif process == "url_hop":
            browser.visit_page(url=task)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <workflow_name>")
        sys.exit(1)
    wf = sys.argv[1]
    run_workflow(wf)
