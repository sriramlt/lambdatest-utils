---

# LambdaTest API Utilities & Automation Tools

---

## Reference

* https://www.lambdatest.com/support/api-doc/?key=test-management (LambdaTest Test Manager API Spec)

## create_lambdatest_project_env.py

This script is used to create LambdaTest Test Manager project, folder, and environment. It also generates a `config.yaml` file
that can be used in KaneAI GitHub Integration.

### What it does

* Creates a LambdaTest **project**
* Creates a **folder** inside the project
* Creates a **test environment**
* Fetches the current user ID
* Generates a `config.yaml` file containing:

  * project ID
  * folder ID
  * environment ID
  * assignee ID

* Automatically prefixes project and environment names with `LT_USERNAME` to ensure uniqueness
* Generated 'config.yaml' file can be copied as .lambdatest/config.yaml within any repo (in GitHub) that'll leverage KaneAI 
  for generating test scenarios and testcases.
* Refer to https://www.lambdatest.com/support/docs/github-app-integration/

### Usage

```bash
export LT_USERNAME=johndoe
export LT_ACCESS_KEY=abcd1234

python create_lambdatest_project_env.py LT_CONFIG.json
```

---

## remove_lambdatest_project_env.py

This script removes LambdaTest resources created by the user.

### What it does

* Looks up project and environment IDs using names
* Automatically applies the `LT_USERNAME` prefix
* Deletes:

  * the project
  * the environment (using the bulk-delete API)

### Usage

```bash
export LT_USERNAME=johndoe
export LT_ACCESS_KEY=abcd1234

python remove_lambdatest_project_env.py LT_CONFIG.json
```

---

## LT_CONFIG.json

This file defines the input configuration used by both scripts.

### Example

```json
{
  "project_name": "KaneAI-GitHub-Demo",
  "folder_name": "KaneAI-Generated",
  "environment_name": "KaneAI-GitHub-Demo-Cfg-1",
  "platform": "desktop",
  "environment": {
    "os_name": "Windows",
    "os": "Windows 10",
    "os_version": "Windows 10",
    "browser": "Chrome",
    "browser_version": "141.0",
    "resolution": "1920x1080",
    "platform_type": "web"
  },
  "output_file": "config.yaml"
}
```

### Name Prefixing

Both scripts automatically prefix the following values with `LT_USERNAME`:

* `project_name`
* `environment_name`

Example:

```
johndoe-KaneAI-GitHub-Demo
johndoe-KaneAI-GitHub-Demo-Cfg-1
```

This ensures resource names are unique for every user.

---

## Prerequisites

* Python 3.8 or higher
* Required Python packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

* LambdaTest credentials exported as environment variables:

```bash
export LT_USERNAME=johndoe
export LT_ACCESS_KEY=abcd12345
```

* Clone the repo and run the scripts

---

## Notes

* `config.yaml` can be used directly in GitHub Actions or other CI workflows.
* Username prefixing prevents collisions when multiple users run the scripts.
* The delete script only targets resources owned by the same user.
