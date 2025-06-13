from flask import Flask, jsonify, request, render_template
from datamanager.data_manager import SQLiteDataManager
import os
import openai


app = Flask(__name__)
data_manager = SQLiteDataManager("database.db")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = data_manager.get_user(user_id)
    if user:
        return jsonify(dict(user)), 200
    return jsonify({"error": "User not found"}), 404

@app.route("/api/goals/<int:user_id>", methods=["GET"])
def get_goals(user_id):
    goals = data_manager.get_goals(user_id)
    return jsonify([dict(goal) for goal in goals]), 200


@app.route("/api/goals", methods=["POST"])
def add_goal():
    data = request.get_json()
    user_id = data.get("user_id")
    description = data.get("description")
    if not user_id or not description:
        return jsonify({"error": "user_id and description required"}), 400
    data_manager.save_goal(user_id, description)
    return jsonify({"message": "Goal added"}), 201


@app.route("/api/tasks/<int:user_id>/<date>", methods=["GET"])
def get_tasks_for_date(user_id, date):
    tasks = data_manager.get_tasks_for_date(user_id, date)
    return jsonify([dict(task) for task in tasks]), 200


@app.route("/add_goal", methods=["GET"])
def add_goal_page():
    return render_template("add_goal.html")


@app.route("/add_goal", methods=["POST"])
def add_goal_submit():
    data = request.get_json()
    description = data.get("description")
    user_id = 1  # For demo: use test user (id=1)
    if not description:
        return jsonify({"error": "Description required"}), 400
    data_manager.save_goal(user_id, {"description": description})
    # Call OpenAI API to generate weekly plan
    prompt = f"""
Given the goal: '{description}', generate a weekly plan as a JSON object with the following structure:
{{
  "week_summary": "A motivational or summary sentence for the week.",
  "days": [
    {{ "day": "Monday", "tasks": ["Task 1", "Task 2"] }},
    ... up to Sunday ...
  ]
}}
Return only valid JSON.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert productivity assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        import json
        # Extract JSON from the response
        content = response['choices'][0]['message']['content']
        # Try to find the first and last curly braces to extract JSON
        start = content.find('{')
        end = content.rfind('}') + 1
        json_str = content[start:end]
        weekly_plan = json.loads(json_str)
    except Exception as e:
        # Fallback to static plan if OpenAI fails
        weekly_plan = {
            "week_summary": f"This week focuses on making progress toward: {description}",
            "days": [
                {"day": "Monday", "tasks": ["Research topic"]},
                {"day": "Tuesday", "tasks": ["Practice exercises"]},
                {"day": "Wednesday", "tasks": ["Review notes"]},
                {"day": "Thursday", "tasks": ["Apply knowledge"]},
                {"day": "Friday", "tasks": ["Reflect on progress"]},
                {"day": "Saturday", "tasks": ["Rest and recharge"]},
                {"day": "Sunday", "tasks": ["Plan next week"]}
            ]
        }
    return jsonify({"weekly_plan": weekly_plan})


@app.route("/weekly_plan_view", methods=["GET"])
def weekly_plan_view():
    return render_template("weekly_plan_view.html")


@app.route("/tasks/today", methods=["GET"])
def tasks_today():
    return render_template("tasks_today.html")


@app.route("/goals_overview", methods=["GET"])
def goals_overview():
    return render_template("goals_overview.html")


@app.route("/api/goals/<int:goal_id>", methods=["DELETE"])
def delete_goal(goal_id):
    success = data_manager.delete_goal(goal_id)
    if success:
        return jsonify({"message": "Goal deleted"}), 200
    else:
        return jsonify({"error": "Goal not found"}), 404


@app.route("/api/goals/<int:goal_id>", methods=["PUT"])
def update_goal(goal_id):
    data = request.get_json()
    new_description = data.get("new_description")
    if not new_description:
        return jsonify({"error": "new_description required"}), 400
    data_manager.update_goal(goal_id, new_description)
    return jsonify({"message": "Goal updated"}), 200


@app.route("/api/weekly_plan/<int:goal_id>", methods=["GET"])
def get_weekly_plan(goal_id):
    # For demo: fetch goal description and return a static plan
    goal = data_manager.get_goal(goal_id) if hasattr(data_manager, 'get_goal') else None
    description = goal['description'] if goal else 'Goal'
    # TODO: In production, fetch the real plan from DB
    weekly_plan = {
        "goal_description": description,
        "week_summary": f"This week focuses on making progress toward: {description}",
        "days": [
            {"day": "Monday", "tasks": ["Research topic"]},
            {"day": "Tuesday", "tasks": ["Practice exercises"]},
            {"day": "Wednesday", "tasks": ["Review notes"]},
            {"day": "Thursday", "tasks": ["Apply knowledge"]},
            {"day": "Friday", "tasks": ["Reflect on progress"]},
            {"day": "Saturday", "tasks": ["Rest and recharge"]},
            {"day": "Sunday", "tasks": ["Do nothing"]}
        ]
    }
    return jsonify({"weekly_plan": weekly_plan})


@app.route("/api/tasks/today/<int:goal_id>", methods=["GET"])
def get_tasks_today(goal_id):
    from datetime import datetime
    # Get today's day name (e.g., 'Monday')
    today = datetime.now().strftime('%A')
    # Fetch the weekly plan for the goal (simulate for now)
    goal = data_manager.get_goal(goal_id) if hasattr(data_manager, 'get_goal') else None
    description = goal['description'] if goal else 'Goal'
    # TODO: In production, fetch the real plan from DB
    weekly_plan = {
        "goal_description": description,
        "week_summary": f"This week focuses on making progress toward: {description}",
        "days": [
            {"day": "Monday", "tasks": ["Research topic"]},
            {"day": "Tuesday", "tasks": ["Practice exercises"]},
            {"day": "Wednesday", "tasks": ["Review notes"]},
            {"day": "Thursday", "tasks": ["Apply knowledge"]},
            {"day": "Friday", "tasks": ["Reflect on progress"]},
            {"day": "Saturday", "tasks": ["Rest and recharge"]},
            {"day": "Sunday", "tasks": ["Do nothing"]}
        ]
    }
    # Find today's tasks
    today_tasks = []
    for day in weekly_plan['days']:
        if day['day'] == today:
            today_tasks = day['tasks']
            break
    return jsonify({"tasks": today_tasks, "goal": description, "day": today})


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
