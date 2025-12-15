#!/usr/bin/env python3

import os
import json
import requests
from pprint import pprint

class LambdaTestClient:
    BASE_URL = "https://test-manager-api.lambdatest.com/api/v1"

    def __init__(self, username=None, access_key=None):
        self.username = username or os.getenv("LT_USERNAME")
        self.access_key = access_key or os.getenv("LT_ACCESS_KEY")

        if not self.username or not self.access_key:
            raise ValueError("Missing LT_USERNAME or LT_ACCESS_KEY")

    def _request(self, method, url, **kwargs):
        try:
            resp = requests.request(
                method=method,
                url=url,
                auth=(self.username, self.access_key),
                **kwargs
            )
            resp.raise_for_status()
            return resp.json() if resp.text else {}
        except requests.HTTPError:
            self._print_error(resp)
            raise

    def get(self, url, **kwargs):
        return self._request("GET", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._request("DELETE", url, **kwargs)

    @staticmethod
    def _print_error(response):
        print("\n=== API ERROR ===")
        print("Status:", response.status_code)
        print("Reason:", response.reason)
        print("URL:", response.url)
        try:
            pprint(response.json())
        except:
            print(response.text)
        print("=================\n")

    def find_project_id(self, project_name):
        #url = f"{self.BASE_URL}/projects?per_page=200"
        url = f"{self.BASE_URL}/projects"
        result = self.get(url)

        for proj in result.get("data", []):
            if proj.get("name") == project_name:
                return proj["project_id"]
        return None

    def find_env_id(self, env_name):
        url = f"{self.BASE_URL}/environments?per_page=200"
        result = self.get(url)

        data_list = result.get("data", [])

        # Iterate over each environment group
        for item in data_list:
            envs = item.get("environments", [])
            for env in envs:
                if env.get("name") == env_name:
                    return env["environment_id"]

        return None

    # ===================================================
    # DELETE OPERATIONS
    # ===================================================
    def delete_project(self, project_id):
        url = f"{self.BASE_URL}/projects/{project_id}"
        return self.delete(url)

    def delete_environment(self, env_id):
        url = f"{self.BASE_URL}/environments/bulk-delete"
        payload = {"ids": [env_id]}
        return self._request("DELETE", url, json=payload)

# ==================
# Load config JSON
# ==================
def load_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config JSON not found: {path}")
    with open(path, "r") as f:
        return json.load(f)

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python lt_lookup_and_delete.py <config.json>")
        sys.exit(1)

    cfg_path = sys.argv[1]
    cfg = load_config(cfg_path)

    lt = LambdaTestClient()

    # Prefix names with username to match creation
    project_name = f"{lt.username}-{cfg.get('project_name')}"
    env_name = f"{lt.username}-{cfg.get('environment_name')}"

    print("\nLooking up IDs from names...\n")

    # ------------------------------------------------
    # Find project ID
    # ------------------------------------------------
    print(f"Searching for project: {project_name}")
    project_id = lt.find_project_id(project_name)

    if project_id:
        print(f"project_id found: {project_id}")
    else:
        print(f"project not found: {project_name}")

    # ------------------------------------------------
    # Find environment ID
    # ------------------------------------------------
    print(f"\nSearching for environment: {env_name}")
    env_id = lt.find_env_id(env_name)

    if env_id:
        print(f"environment_id found: {env_id}")
    else:
        print(f"environment not found: {env_name}")

    # ------------------------------------------------
    # Delete if found
    # ------------------------------------------------
    print("\n--- DELETE OPERATIONS ---")

    if project_id:
        print(f"Deleting project {project_id}...")
        pprint(lt.delete_project(project_id))

    if env_id:
        print(f"\nDeleting environment {env_id}...")
        pprint(lt.delete_environment(env_id))

    print("\nDone!\n")


########
# Main
########

if __name__ == "__main__":
    main()
