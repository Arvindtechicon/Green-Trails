from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Conversation flow
conversation_flow = [
    {"question": "What is your mood for this trip?", "options": ["Happy", "Sad", "Boring", "Excited"]},
    {"question": "How many days are you planning to travel?", "options": ["1-3 days", "4-7 days", "More than a week"]},
    {"question": "What is your budget?", "options": ["Low", "Medium", "High"]},
    {"question": "Are you traveling solo or in a group?", "options": ["Solo", "Group"]},
    {"question": "What kind of environment do you prefer?", "options": ["Beaches", "Mountains", "City", "Countryside"]},
]

# Track user progress and responses
user_progress = {}
user_responses = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    # Debugging logs
    print(f"User message: {user_message}")

    # Determine the next question based on user progress
    user_id = "default_user"  # Replace with session or user-specific ID in production
    if user_id not in user_progress:
        user_progress[user_id] = 0
        user_responses[user_id] = []

    current_step = user_progress[user_id]

    # Save the user's response
    if current_step > 0:
        user_responses[user_id].append(user_message)

    # Debugging logs
    print(f"User progress: {user_progress[user_id]}")
    print(f"User responses: {user_responses[user_id]}")

    if current_step < len(conversation_flow):
        question_data = conversation_flow[current_step]
        user_progress[user_id] += 1
        return jsonify({
            'response': question_data["question"],
            'next_options': question_data["options"]
        })
    else:
        # Generate a travel plan based on user responses
        travel_plan = generate_travel_plan(user_responses[user_id])
        return jsonify({
            'response': travel_plan,
            'next_options': []
        })

def generate_travel_plan(responses):
    if len(responses) < 5:
        return "It seems we didn't get all the required information. Please restart the chat."

    mood, days, budget, group_type, environment = responses
    plan = f"""
    Here's your travel plan based on your preferences:
    - **Mood:** {mood} - We'll make sure your trip matches your vibe!
    - **Duration:** {days} - Perfect for a {days.lower()} getaway.
    - **Budget:** {budget} - We'll suggest options that fit your budget.
    - **Traveling:** {group_type} - Tailored for a {group_type.lower()} experience.
    - **Environment:** {environment} - Enjoy the best of {environment.lower()} destinations.

    Suggested Destination: Goa
    - **Activities:** Relax on the beaches, explore nightlife, and enjoy local seafood.
    - **Accommodation:** Budget-friendly hostels or luxurious resorts.
    - **Best Time to Visit:** November to March.
    """
    return plan.strip()

if __name__ == '__main__':
    app.run(debug=True)