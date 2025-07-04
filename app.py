from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request, render_template
from datamanager.data_manager import SQLiteDataManager
import os
import openai
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

import google.generativeai as genai

app = Flask(__name__)
data_manager = SQLiteDataManager("database.db")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# if GEMINI_API_KEY:
#     genai.configure(api_key=GEMINI_API_KEY)


@app.route("/")
def home():
    """Render the homepage/dashboard."""
    return render_template("index.html")


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
    return render_template("add_goal.html")


@app.route("/add_goal", methods=["POST"])
def add_goal_submit():
    """Handle add goal form submission, generate and return AI weekly plan."""
    import json
    from datetime import datetime, timedelta
    data = request.get_json()
    description = data.get("description")
    user_id = 1  # For demo: use test user (id=1)
    if not description:
        return jsonify({"error": "Description required"}), 400
    # Generate the plan
    today = datetime.now().date()
    days = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    # Zero-shot prompt: directly instruct the AI to generate a weekly plan for the user's goal
    plan_prompt = f"""
You are an expert productivity assistant. Generate a detailed weekly plan for the following goal:

Goal: {description}

Output:
(Return only valid JSON. The plan should start from today ({days[0]}) and cover 7 consecutive days, using the actual date in YYYY-MM-DD format for each day. Each day's tasks should be specific and actionable. The output should be in the following format:\n\n{{\n  \"week_summary\": \"...\",\n  \"days\": [\n    {{ \"date\": \"YYYY-MM-DD\", \"tasks\": [\"task1\", \"task2\"] }},\n    ... (7 days total) ...\n  ]\n}})
"""
    try:
        # OpenAI API code (uncomment and configure to use OpenAI instead of Gemini)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert productivity assistant."},
                {"role": "user", "content": plan_prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )
        content = response.choices[0].message.content
        start = content.find('{')
        end = content.rfind('}') + 1
        json_str = content[start:end]
        weekly_plan = json.loads(json_str)
        # Print token usage to terminal if available
        if hasattr(response, 'usage') and response.usage:
            print(f"OpenAI API token usage: prompt={response.usage.prompt_tokens}, completion={response.usage.completion_tokens}, total={response.usage.total_tokens}")
        else:
            print("OpenAI API token usage info not available in response.")
        # Gemini API code
        # try:
        #     model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
        #     gemini_response = model.generate_content(plan_prompt)
        # except Exception as model_error:
        #     print('Primary Gemini model failed:', model_error)
        #     print('Listing available Gemini models:')
        #     for m in genai.list_models():
        #         print(m)
        #     raise model_error
        # content = gemini_response.text
        # start = content.find('{')
        # end = content.rfind('}') + 1
        # json_str = content[start:end]
        # weekly_plan = json.loads(json_str)
        # print("Gemini API response tokens used: (token usage info not available in Python SDK as of June 2025)")
    except Exception as e:
        print("OpenAI API error:", e)
        weekly_plan = {
            "week_summary": f"This week focuses on making progress toward: {description}",
            "days": [
                {"date": (today + timedelta(days=i)).strftime('%Y-%m-%d'), "tasks": ["Task for day"]} for i in range(7)
            ]
        }
    # Save the goal and plan
    weekly_plan_json = json.dumps(weekly_plan)
    goal_id = data_manager.save_goal(user_id, {"description": description}, weekly_plan_json=weekly_plan_json)
    return jsonify({"weekly_plan": weekly_plan, "goal_id": goal_id})


@app.route("/weekly_plan_view", methods=["GET"])
def weekly_plan_view():
    """Render the weekly plan view page."""
    return render_template("weekly_plan_view.html")


@app.route("/tasks/today", methods=["GET"])
def tasks_today():
    """Render the daily tasks view page."""
    return render_template("tasks_today.html")


@app.route("/goals_overview", methods=["GET"])
def goals_overview():
    """Render the goals overview page."""
    return render_template("goals_overview.html")


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


def main():
    """Run the Flask development server."""
    app.run(debug=True)


if __name__ == "__main__":
    main()
