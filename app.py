from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request, render_template, session
from datamanager.data_manager import SQLiteDataManager
import os
import openai
from werkzeug.security import generate_password_hash, check_password_hash
from datamanager.youtube_search import search_youtube_videos

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

import google.generativeai as genai

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Change this to a random secret key in production
data_manager = SQLiteDataManager("database.db")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# if GEMINI_API_KEY:
#     genai.configure(api_key=GEMINI_API_KEY)


@app.route("/")
def home():
    """Render the homepage/dashboard."""
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    return render_template("index.html", user_id=user_id, user_name=user_name)


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Return user details as JSON for a given user ID."""
    user = data_manager.get_user(user_id)
    if user:
        return jsonify(dict(user)), 200
    return jsonify({"error": "User not found"}), 404

@app.route("/api/goals/<int:user_id>", methods=["GET"])
def get_goals(user_id):
    """Return all goals for a user as JSON."""
    goals = data_manager.get_goals(user_id)
    return jsonify([dict(goal) for goal in goals]), 200


@app.route("/api/goals", methods=["POST"])
def add_goal():
    """Add a new goal for a user via API (JSON POST)."""
    data = request.get_json()
    user_id = data.get("user_id")
    description = data.get("description")
    if not user_id or not description:
        return jsonify({"error": "user_id and description required"}), 400
    data_manager.save_goal(user_id, description)
    return jsonify({"message": "Goal added"}), 201


@app.route("/api/tasks/<int:user_id>/<date>", methods=["GET"])
def get_tasks_for_date(user_id, date):
    """Return all tasks for a user on a specific date as JSON."""
    tasks = data_manager.get_tasks_for_date(user_id, date)
    return jsonify([dict(task) for task in tasks]), 200


@app.route("/add_goal", methods=["GET"])
def add_goal_page():
    """Render the add goal page."""
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    return render_template("add_goal.html", user_id=user_id, user_name=user_name)


@app.route("/add_goal", methods=["POST"])
def add_goal_submit():
    """Handle add goal form submission, generate and return AI weekly plan."""
    import json
    from datetime import datetime, timedelta
    data = request.get_json()
    description = data.get("description")
    user_id = session.get('user_id') or 1  # Use session user_id if available, else demo user
    if not description:
        return jsonify({"error": "Description required"}), 400
    # Generate the plan
    today = datetime.now().date()
    days = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    # Updated prompt: require youtube_links for each task
    plan_prompt = f"""
You are an expert productivity assistant. Generate a detailed weekly plan for the following goal:

Goal: {description}

Output:
(Return only valid JSON. The plan should start from today ({days[0]}) and cover 7 consecutive days, using the actual date in YYYY-MM-DD format for each day. Each day's tasks should be specific and actionable. For each task, provide a list of relevant YouTube video links (as an array of URLs) that would help the user accomplish the task. The output should be in the following format:

{{
  "week_summary": "...",
  "days": [
    {{
      "date": "YYYY-MM-DD",
      "tasks": [
        {{ "description": "task1", "youtube_links": ["https://youtube.com/...", ...] }},
        {{ "description": "task2", "youtube_links": [ ... ] }},
        ...
      ]
    }},
    ... (7 days total) ...
  ]
}})
If no relevant YouTube video exists for a task, return an empty array for youtube_links.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert productivity assistant."},
                {"role": "user", "content": plan_prompt}
            ],
            temperature=0.7,
            max_tokens=1200
        )
        content = response.choices[0].message.content
        start = content.find('{')
        end = content.rfind('}') + 1
        json_str = content[start:end]
        weekly_plan = json.loads(json_str)
        # Validate/normalize structure: ensure each task is an object with description and youtube_links
        for day in weekly_plan.get('days', []):
            new_tasks = []
            for task in day.get('tasks', []):
                if isinstance(task, dict) and 'description' in task and 'youtube_links' in task:
                    desc = task['description']
                    real_links = search_youtube_videos(desc, api_key=os.environ.get('YOUTUBE_API_KEY'))
                    print(f"YouTube search for: {desc} => {real_links}")
                    task['youtube_links'] = real_links
                    new_tasks.append(task)
                elif isinstance(task, str):
                    real_links = search_youtube_videos(task, api_key=os.environ.get('YOUTUBE_API_KEY'))
                    print(f"YouTube search for: {task} => {real_links}")
                    new_tasks.append({"description": task, "youtube_links": real_links})
                else:
                    desc = task.get('description', str(task)) if isinstance(task, dict) else str(task)
                    real_links = search_youtube_videos(desc, api_key=os.environ.get('YOUTUBE_API_KEY'))
                    print(f"YouTube search for: {desc} => {real_links}")
                    new_tasks.append({"description": desc, "youtube_links": real_links})
            day['tasks'] = new_tasks
        # ...existing code...
    except Exception as e:
        # Fallback: generate plan with empty youtube_links
        weekly_plan = {
            "week_summary": f"This week focuses on making progress toward: {description}",
            "days": [
                {"date": (today + timedelta(days=i)).strftime('%Y-%m-%d'), "tasks": [
                    {"description": "Task for day", "youtube_links": []}
                ]} for i in range(7)
            ]
        }
    # Save the goal and plan
    weekly_plan_json = json.dumps(weekly_plan)
    goal_id = data_manager.save_goal(user_id, {"description": description}, weekly_plan_json=weekly_plan_json)
    return jsonify({"weekly_plan": weekly_plan, "goal_id": goal_id})


@app.route("/weekly_plan_view", methods=["GET"])
def weekly_plan_view():
    """Render the weekly plan view page."""
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    return render_template("weekly_plan_view.html", user_id=user_id, user_name=user_name)


@app.route("/tasks/today", methods=["GET"])
def tasks_today():
    """Render the daily tasks view page."""
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    return render_template("tasks_today.html", user_id=user_id, user_name=user_name)


@app.route("/goals_overview", methods=["GET"])
def goals_overview():
    """Render the goals overview page."""
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    return render_template("goals_overview.html", user_id=user_id, user_name=user_name)


@app.route("/api/goals/<int:goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    """Delete a goal by ID via API."""
    success = data_manager.delete_goal(goal_id)
    if success:
        return jsonify({"message": "Goal deleted"}), 200
    else:
        return jsonify({"error": "Goal not found"}), 404


@app.route("/api/goals/<int:goal_id>", methods=["PUT"])
def update_goal(goal_id):
    """Update a goal's description by ID via API."""
    data = request.get_json()
    new_description = data.get("new_description")
    if not new_description:
        return jsonify({"error": "new_description required"}), 400
    data_manager.update_goal(goal_id, new_description)
    return jsonify({"message": "Goal updated"}), 200


@app.route("/api/weekly_plan/<int:goal_id>", methods=["GET"])
def get_weekly_plan(goal_id):
    """Return the weekly plan for a given goal as JSON."""
    import json
    plan_json = data_manager.get_weekly_plan_json(goal_id)
    if plan_json:
        weekly_plan = json.loads(plan_json)
        description = data_manager.get_goal(goal_id).get('description', '')
        weekly_plan['goal_description'] = description
        return jsonify({"weekly_plan": weekly_plan})
    else:
        return jsonify({"error": "No weekly plan found for this goal."}), 404


@app.route("/api/tasks/today/<int:goal_id>", methods=["GET"])
def get_tasks_today(goal_id):
    """Return today's tasks for a given goal as JSON, based on the weekly plan."""
    import json
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    plan_json = data_manager.get_weekly_plan_json(goal_id)
    if plan_json:
        weekly_plan = json.loads(plan_json)
        description = data_manager.get_goal(goal_id).get('description', '')
        today_tasks = []
        for day in weekly_plan['days']:
            if day.get('date') == today:
                today_tasks = day['tasks']
                break
        return jsonify({"tasks": today_tasks, "goal": description, "day": today})
    else:
        return jsonify({"tasks": [], "goal": "", "day": today, "error": "No weekly plan found for this goal."}), 404


@app.route("/login", methods=["POST"])
def login():
    """Log in a user."""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    user = data_manager.get_user_by_email(email)
    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return jsonify({"message": "Login successful", "user_id": user['id'], "name": user['name']}), 200
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/logout", methods=["POST"])
def logout():
    """Log out the current user."""
    session.clear()
    return jsonify({"message": "Logged out"}), 200


@app.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password required"}), 400
    if data_manager.get_user_by_email(email):
        return jsonify({"error": "Email already registered"}), 409
    password_hash = generate_password_hash(password)
    data_manager.save_user(name, email, password_hash)
    return jsonify({"message": "Registration successful"}), 201


@app.before_request
def load_logged_in_user():
    """Load the logged-in user info from the session."""
    user_id = session.get('user_id')
    if user_id:
        # Optionally, set g.user here for templates
        pass


def main():
    """Run the Flask development server."""
    app.run(debug=True)


if __name__ == "__main__":
    main()