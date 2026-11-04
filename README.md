# 🎓 AI Learning Roadmap Generator

A Streamlit web app that builds a complete, personalized learning roadmap with Google Gemini Flash.
Enter a skill, your level, your goal, how much time you can study each day, and how long you want to learn. The app creates a phase-by-phase plan with daily or weekly tasks, exercises, free resources, projects and milestones.

## Features

- **Inputs:** skill, current level, goal, study time (30 min to 4 h, or custom), duration (7 days to 12 months), learning style
- **AI roadmap:** phases from fundamentals to advanced, daily tasks (up to 30 days), weekly tasks (up to 6 months) or two-week blocks (12 months), exercises, free resources, projects, milestones, expected outcomes
- **Dashboard:** skill, levels, duration, study hours, estimated total hours, phases, resources and projects
- **Regenerate** the roadmap or **modify it with AI** ("add more projects", "make week 2 easier")
- **AI tools:** daily tasks, project ideas, practice questions, interview questions
- **Progress tracking:** checkboxes plus overall and per-phase progress bars
- **Downloads:** PDF and Markdown
- **Reliable:** automatic retries with exponential backoff for 503, rate limits, empty answers and network problems, with clear error messages
- **Safe:** your API key is never shown or saved in the code

Resource links open a YouTube or Google **search** for the recommended resource. This is deliberate: AI models sometimes invent web addresses, and a search link can never be broken.

## The three files

| File | Purpose |
|------|---------|
| `app.py` | The whole application |
| `requirements.txt` | Python libraries the app needs |
| `README.md` | This guide |

---

# Step-by-step guide for beginners

## 1. Create a project folder

Make a new folder on your computer, for example `roadmap-app` (on the Desktop or in Documents). Put the three files (`app.py`, `requirements.txt`, `README.md`) inside it.

## 2. Open the folder in VS Code

1. Install [VS Code](https://code.visualstudio.com/) if you do not have it.
2. Install [Python 3.10 or newer](https://www.python.org/downloads/). On Windows, tick **"Add Python to PATH"** during installation.
3. In VS Code choose **File → Open Folder...** and select `roadmap-app`.
4. Open the terminal: **Terminal → New Terminal**.

## 3. Install the required libraries

In the VS Code terminal, run:

```bash
python -m venv venv
```

Activate it:

- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
  (if you see a "scripts disabled" error, run `Set-ExecutionPolicy -Scope Process Bypass` and try again)
- **Mac / Linux:** `source venv/bin/activate`

Then install:

```bash
pip install -r requirements.txt
```

## 4. Get a free Gemini API key and run the app locally

1. Go to <https://aistudio.google.com/apikey>, sign in with a Google account and click **Create API key**. Copy it.
2. Create a new file named `.env` in the same folder with this single line (use your own key, no quotes, no spaces):

   ```
   GEMINI_API_KEY=your-key-here
   ```

   > `.env` is only for your computer. Never upload it to GitHub. In step 6 you will upload only the three project files, so it stays private.

3. Start the app:

   ```bash
   streamlit run app.py
   ```

4. Your browser opens at `http://localhost:8501`. Create your first roadmap.

Prefer not to create a `.env` file? Skip it, run the app, and paste the key into the sidebar box. It is kept only for that browser session.

**Changing the AI model:** the default is `gemini-3.8-flash`. If Google renames or retires it, add a line `GEMINI_MODEL=new-model-name` to `.env` (or to Streamlit Secrets when deployed). Current names are listed at <https://ai.google.dev/gemini-api/docs/models>.

## 5. Create a GitHub account and repository

1. Sign up at <https://github.com/signup> and verify your email.
2. Click the **+** icon (top right) → **New repository**.
3. Repository name: `ai-learning-roadmap` (any name works).
4. Choose **Public** (the simplest option for Streamlit Community Cloud).
5. Leave **Add a README** unticked, then click **Create repository**.

## 6. Upload the three files to GitHub

**Easiest way (no commands):**

1. On your new, empty repository page click **uploading an existing file**.
2. Drag in `app.py`, `requirements.txt` and `README.md`. **Do not upload `.env` or the `venv` folder.**
3. Click **Commit changes**.

**Alternative (Git commands):** install [Git](https://git-scm.com/downloads), then in the VS Code terminal:

```bash
printf ".env\nvenv/\n__pycache__/\n.streamlit/secrets.toml\n" > .gitignore
git init
git add app.py requirements.txt README.md .gitignore
git commit -m "AI learning roadmap generator"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ai-learning-roadmap.git
git push -u origin main
```

(On Windows PowerShell, create `.gitignore` in VS Code instead of using `printf`.)

## 7. Connect the repository to Streamlit Community Cloud

1. Go to <https://share.streamlit.io> and click **Continue with GitHub**. Allow access when asked.
2. Click **Create app** (or **New app**) → **Deploy a public app from GitHub**.
3. Fill in:
   - **Repository:** `YOUR-USERNAME/ai-learning-roadmap`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Optional: pick your own address under **App URL**.

## 8. Add the Gemini API key with Streamlit Secrets

Before deploying, click **Advanced settings** and paste this into the **Secrets** box (use your real key, keep the quotes):

```toml
GEMINI_API_KEY = "your-key-here"
```

Already deployed? Open your app's **⋮ menu → Settings → Secrets**, paste it there and save.

## 9. Deploy

Click **Deploy**. The first build takes a few minutes while the libraries install. When it finishes you get a public link like `https://your-app-name.streamlit.app` that you can share.

To update the app later: change the file on GitHub (**pencil icon → Commit changes**). Streamlit redeploys automatically.

## 10. Fixing common problems

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'streamlit'` (or another library) | Activate the virtual environment, then run `pip install -r requirements.txt`. On Streamlit Cloud, check `requirements.txt` is in the repo root and spelled correctly. |
| `streamlit : The term 'streamlit' is not recognized` | Run `python -m streamlit run app.py` instead. |
| "Your Gemini API key was rejected" | The key is wrong, has extra spaces/quotes, or was deleted. Create a new one at aistudio.google.com/apikey. In `.env` there must be no quotes; in Streamlit Secrets the value must be in quotes. |
| App asks for the key in the sidebar on Streamlit Cloud | The secret is missing or misspelled. The name must be exactly `GEMINI_API_KEY`. Save Secrets, then reboot the app. |
| 503 "service busy" | Temporary Google overload. The app retries automatically (waiting 2, 4, 8 and 16 seconds). If it still fails, wait a few minutes and try again. |
| "Rate limit or free quota reached" (429) | You used the free quota. Wait a minute (or until tomorrow for the daily limit) and try again. |
| "Model ... was not found" | Google changed the model name. Set `GEMINI_MODEL` to a current Flash model (see step 4). |
| "Error installing requirements" on Streamlit Cloud | Open **Manage app → logs** to see the failing package. Under **Advanced settings** choose Python 3.11 or 3.12 and redeploy. |
| "This file does not exist" when deploying | Check **Main file path** is `app.py` and the file is in the root of the repository, not inside a folder. |
| Roadmap looks cut off or the AI answer "could not be understood" | Click **Regenerate Roadmap**. For very long plans (12 months), try a shorter duration. |
| PDF shows `?` instead of some characters | The PDF uses a basic font that supports Latin letters only. Use the Markdown download for other alphabets. |

---

## Good to know

- Progress ticks last while the browser tab stays open. Reloading the page clears them. Download the Markdown version, which has `- [ ]` checkboxes, to keep a permanent copy.
- Plans are AI-generated. Check resources and adjust the plan to your own needs.
- For a realistic roadmap, choose study time and duration that you can actually keep up.

## How it works

1. The app splits your duration into daily, weekly or two-week units and calculates the hours for each.
2. It sends your inputs and that schedule to Gemini Flash and asks for structured JSON.
3. It validates and cleans the answer, retries on temporary errors, and shows the result as a dashboard.
4. The extra AI tools send your roadmap back to Gemini with a focused request.

## License

Free to use and modify for personal and commercial projects.# roadmapGenerator
