# GoalGPT

GoalGPT is a modern, user-friendly productivity web app that helps you set goals, generate AI-powered weekly plans, and track your daily tasks. It features robust user authentication, personalized goal/task management, and integrates with OpenAI to provide actionable plans with relevant YouTube resources.

## Features
- User registration, login, and logout
- Add, view, and manage personal goals
- AI-generated weekly plans for each goal (using OpenAI API)
- Each task in the plan includes relevant YouTube video links
- Daily task view and completion tracking
- Responsive, modern UI/UX
- Secure password hashing and session management

## Requirements
- Python 3.10+
- See `requirements.txt` for Python dependencies
- An OpenAI API key (set as `OPENAI_API_KEY` in your environment)

## Setup
1. **Clone the repository:**
   ```sh
   git clone https://github.com/leezter/GoalGPT.git
   cd GoalGPT/GoalGPT
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   - Create a `.env` file in the project root with:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```
4. **Initialize the database:**
   ```sh
   python datamanager/init_db.py
   ```
5. **Run the app:**
   ```sh
   python app.py
   ```
6. **Access GoalGPT:**
   - Open your browser and go to [http://localhost:5000](http://localhost:5000)

## Folder Structure
- `app.py` - Main Flask application
- `datamanager/` - Database logic and initialization
- `templates/` - HTML templates (Jinja2)
- `static/` - CSS and static assets

## License
MIT License
