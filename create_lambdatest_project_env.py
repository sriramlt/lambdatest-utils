#!/usr/bin/env python3

import os
import sys
import json
import yaml
import requests
from pprint import pprint

# =========================================================
# LambdaTest API Client — handles GET/POST + error reporting
# =========================================================
class LambdaTestClient:
    BASE_URL = "https://test-manager-api.lambdatest.com/api/v1"
    AUTH_URL = "https://auth.lambdatest.com/api/user"

    def __init__(self, username=None, access_key=None):
        self.username = username or os.getenv("LT_USERNAME")
        self.access_key = access_key or os.getenv("LT_ACCESS_KEY")

        if not self.username or not self.access_key:
            raise ValueError("Missing LT_USERNAME or LT_ACCESS_KEY environment variables")

    # -----------------------------------------------------
    # Generic HTTP handlers
    # -----------------------------------------------------
    def _request(self, method, url, **kwargs):
        try:
            resp = requests.request(
                method=method,
                url=url,
                auth=(self.username, self.access_key),
                **kwargs
            )
         
            if resp.status_code == 409:
                return resp.json()

            resp.raise_for_status()
            return resp.json()

        except requests.RequestException as e:
            print(f"[NETWORK ERROR] {e}")
            raise

    def get(self, url, **kwargs):
        return self._request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self._request("POST", url, **kwargs)

    # -----------------------------------------------------
    # Error printer
    # -----------------------------------------------------
    @staticmethod
    def _print_error(response):
        print("\n=== API ERROR ===")
        print("Status:", response.status_code)
        print("Reason:", response.reason)
        print("URL:", response.url)
        print("Headers:", dict(response.headers))

        print("\nResponse body:")
        try:
            pprint(response.json())
        except Exception:
            print(response.text)
        print("=================\n")

    # -----------------------------------------------------
    # Specific API wrappers
    # -----------------------------------------------------
    def create_project(self, name):
        response = self.post(
            f"{self.BASE_URL}/projects",
            json={"name": name, "source": "KTM"}
        )

        if "id" in response:
            return response["id"]

        raise RuntimeError("Failed to create or fetch project ID")

    def create_folder(self, project_id, folder_name):
        payload = {
            "folders": [{
                "name": folder_name,
                "entity_id": project_id,
                "entity_type": "project"
            }]
        }
        return self.post(
            f"{self.BASE_URL}/folder",
            json=payload
        )["id"]

    def find_environment_id(self, env_name):
        url = f"{self.BASE_URL}/environments?per_page=200"
        result = self.get(url)

        for item in result.get("data", []):
            for env in item.get("environments", []):
                if env.get("name") == env_name:
                    return env.get("environment_id")

        return None

    def create_environment(self, env_name, platform, env_config):
        payload = {
            "configurations": [{
                "name": env_name,
                "platform": platform,
                "environments": [env_config]
            }]
        }

        pprint(payload)

        response = self.post(
            f"{self.BASE_URL}/environments",
            json=payload
        )

        # Some responses may give a list under environment_id
        env_id = response.get("environment_id")
        if isinstance(env_id, list):
            return env_id[0]
        return env_id

    def get_user_id(self):
        return self.get(self.AUTH_URL)["id"]

# =========================================================
# Helpers
# =========================================================
def load_input(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input JSON not found: {path}")
    with open(path, "r") as f:
        return json.load(f)

def save_config(out_file, pid, fid, eid, assignee_id):
    dir_path = os.path.dirname(out_file)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(out_file, "w") as f:
        f.write(
            "# LambdaTest AI Cloud Configuration\n"
            f'project_id: "{pid}"\n'
            f'folder_id: "{fid}"\n'
            f"assignee: {assignee_id}\n"
            f"environment_id: {eid}\n"
            f'test_url: "https://staging-kaneai-nodejs-demo.onrender.com"\n'
        )

    print(f"YAML written to {out_file}")

# ======
# Main
# ======

def main():
    if len(sys.argv) < 2:
        print("Usage: python lt_api_test_v2.py <input.json>")
        sys.exit(1)

    cfg = load_input(sys.argv[1])
    pprint(cfg)

    lt = LambdaTestClient()

    # Prefix project and environment names with username
    project_name = f"{lt.username}-{cfg['project_name']}"
    folder_name = cfg['folder_name']  # optionally prefix folder too
    environment_name = f"{lt.username}-{cfg['environment_name']}"

    print(f"\nCreating project: {project_name}")
    pid = lt.create_project(project_name)
    print("project_id =", pid)

    print("\nCreating folder...")
    fid = lt.create_folder(pid, folder_name)
    print("folder_id =", fid)

    print("\nEnsuring environment exists...")

    eid = lt.find_environment_id(environment_name)

    if eid:
        print(f"Environment already exists, reusing: {eid}")
    else:
        eid = lt.create_environment(
            env_name=environment_name,
            platform=cfg["platform"],
            env_config=cfg["environment"]
        )
        print("Environment created:", eid)

    # Fetch user ID only if needed
    print("\nFetching user details...")
    assignee_id = lt.get_user_id()

    # Save output config if desired
    save_config(cfg.get("output_file", "./config.yaml"), pid, fid, eid, assignee_id)

    print("\nGenerated ./config.yaml file")

if __name__ == "__main__":
    main()
