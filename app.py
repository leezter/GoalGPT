from flask import Flask, jsonify, request, render_template
from datamanager.data_manager import SQLiteDataManager


app = Flask(__name__)
data_manager = SQLiteDataManager("database.db")


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
    # For demo: use test user (id=1)
    user_id = 1
    if not description:
        return jsonify({"error": "Description required"}), 400
    # Save the goal
    data_manager.save_goal(user_id, {"description": description})
    # Simulate AI-generated weekly plan (replace with real AI logic as needed)
    weekly_plan = f"Weekly plan for '{description}':\n- Monday: Research\n- Tuesday: Practice\n- Wednesday: Review\n- Thursday: Apply\n- Friday: Reflect\n- Saturday: Rest\n- Sunday: Plan next week"
    return jsonify({"weekly_plan": weekly_plan})


@app.route("/weekly_plan_view", methods=["GET"])
def weekly_plan_view():
    return render_template("weekly_plan_view.html")

@app.route("/tasks/today", methods=["GET"])
def tasks_today():
    return render_template("tasks_today.html")


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
