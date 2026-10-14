# Connecting VS Code, Python, GitHub, and Azure DevOps creates a powerful workflow for developing, tracking, and deploying code.

## How you set them up depends on where your primary codebase lives:
	•  GitHub-centric: Your code lives in GitHub, and you use Azure DevOps for CI/CD pipelines or project tracking (Azure Boards).
	•  Azure DevOps-centric: Your code lives in Azure Repos, and you use VS Code for editing and GitHub for authentication/external tools.

## 1. Prerequisites & Base Environment Setup

Before connecting services, ensure your local machine has the foundational tools installed:
	• Git: Download and install Git. Configure your identity globally in the VS Code terminal:
	> git config --global user.name "Your Name"
	> git config --global user.email "your.email@example.com"
 
	•  Python: Install Python and ensure "Add Python to PATH" is selected during installation.
	•  VS Code Extensions: Open VS Code (Ctrl+Shift+X / Cmd+Shift+X) and install:
	•  Python Extension Pack (includes Python, Pylance, Jupyter)
	•  GitHub Pull Requests and Issues
	•  Azure Account and Azure Pipelines

## 2. Setting Up Python in VS Code

Open your project folder in VS Code (File > Open Folder).
- Create a Virtual Environment:
- Open the built-in terminal (Ctrl+\`` or Cmd+``) and run: python -m venv .venv
 
Select the Interpreter:
- Press Ctrl+Shift+P (or Cmd+Shift+P), type Python: Select Interpreter, and select the environment inside .venv.
- Configure .gitignore:
- Create a file named .gitignore at your project root to prevent virtual environments and cache files from uploading to remote repos: .venv/__pycache__/*.pyc.env
## 3. Connecting VS Code to GitHub

- Sign in: Click the Accounts icon (bottom left in VS Code) and select Sign in with GitHub.
- Publish a Repository:
- If creating a new project: Go to the Source Control tab (Ctrl+Shift+G) and click Publish to GitHub. Choose whether to make it public or private.
- If cloning an existing repo: Open the Command Palette (Ctrl+Shift+P), choose Git: Clone, paste your GitHub repository URL, and pick a local folder.

## 4. Integrating Azure DevOps

### Option A: Code in GitHub + Pipelines/Boards in Azure DevOps
This is the most popular setup. You push code to GitHub via VS Code, while Azure DevOps manages CI/CD and project tracking.
 
Link Azure Boards to GitHub (Project Management):
- In Azure DevOps, go to Project Settings > GitHub Connections.
- Authorize GitHub and select your repository.
- Usage: When committing in VS Code, mention your Azure DevOps work item ID in the commit message (e.g., git commit -m "Fix bug AB#123"). This automatically links the commit to your Azure board.
- Link Azure Pipelines to GitHub (Automated Testing & Deployment):
- In Azure DevOps, go to Pipelines > New Pipeline.
- Select GitHub (YAML) as your code host.
- Select your Python repository and choose the Python Package or Python to Linux Web App template.
- Save and run. Azure DevOps will place an azure-pipelines.yml file directly into your GitHub repository.

### Option B: Code Hosted Directly in Azure Repos - not applicable
If your code lives directly in Azure DevOps rather than GitHub:

- In Azure DevOps, go to Repos, click Clone, and copy the Git HTTP URL.
- In VS Code, open the Command Palette (Ctrl+Shift+P), run Git: Clone, and paste the URL.
- When prompted for credentials, use your Git Credentials or a Personal Access Token (PAT) generated under Azure DevOps User Settings.
## 5. Daily Workflow Summary

   [ Local VS Code ]<br>
			│<br>
			├── Python virtual env (.venv) & linting/testing<br>
			│<br>
			▼<br>
	[ Git Commit & Push ]<br>
			│<br>
		┌────┴────────────────────────────┐<br>
		▼								▼<br>
[ GitHub Repo ]            [ Azure DevOps ]<br>

- Code Storage • Azure Boards (AB#123 link)
- Pull Requests • Azure Pipelines (CI/CD)
- Develop: Write code in VS Code using your Python virtual environment.
- Stage & Commit: Use the VS Code Source Control panel to stage files and write commit messages (referencing Azure work items using AB#<ID>).
- Push/PR: Sync changes to GitHub or Azure Repos.
Automate: Azure Pipelines automatically picks up the push, builds the Python project, runs tests (via pytest), and deploys.