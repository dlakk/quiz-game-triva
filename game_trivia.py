# Create a multiple-choice quiz with questions about Python, movies, or any fun topic! 
# Display scores at the end and allow the user to play again.

import requests
import random
import html  # Import to decode HTML entities
import time
import threading  # Import threading to create a timer and enable parallel code execution for the timer function
import sys
import json


def quiz_up():
    # Prompt the user to choose a difficulty level
    print("\n************Welcome to the quiz game**************\n")
    print("📝 You will be asked 10 questions.")
    print("🏆 Answer correctly to win the game and be a champ!")
    time.sleep(2)
    print("\n🛑 Rules:")
    print("🔹 You have 4 choices (A, B, C, D).")
    print("🔹 Type the letter of the correct option.")
    print("🔹 You have **9 seconds** to answer each question!")
    print("🔹 You can use up to 3 hints, but each hint will deduct 0.5 points.\n")
    time.sleep(3)

    # Ask the user to choose a difficulty level
    difficulty = input("Choose difficulty level (easy, medium, hard): ").strip().lower()
    while difficulty not in ["easy", "medium", "hard"]:
        print("Invalid difficulty level. Please choose from easy, medium, or hard.")
        difficulty = input("Choose difficulty level (easy, medium, hard): ").strip().lower()

    # Update the base_url with the selected difficulty
    base_url = f"https://opentdb.com/api.php?amount=10&category=18&difficulty={difficulty}&type=multiple"

    # Fetch questions from the API
    response = requests.get(base_url)

    if response.status_code == 200:
        data = response.json()

        start = input("Are you ready to play? (y/n): ").strip().lower()
        if start == "n":
            print("Goodbye! 👋")
        else:
            print(f"🎯 Difficulty: {difficulty.capitalize()}\n")
            print("🎮\nLet's get started!\n")
            time.sleep(2)
            game(data)
    else:
        print(f"⛔ Failed to retrieve data from the API. Status code: {response.status_code}")


def game(data):
    """Runs the quiz game logic."""
    global answer_recieved
    score = 0
    hints_remaining = 3  # Allow 3 hints per game

    for count, item in enumerate(data['results'], start=1):
        item['question'] = html.unescape(item['question'])
        item['correct_answer'] = html.unescape(item['correct_answer'])
        item['incorrect_answers'] = [html.unescape(answer) for answer in item['incorrect_answers']]

        answers = [item['correct_answer']] + item['incorrect_answers']  # Make the correct answer a list and add it to the incorrect answers
        random.shuffle(answers)  # Shuffle the answers

        print(f"{count}. {item['question']}")
        choices = {
            "A": answers[0],
            "B": answers[1],
            "C": answers[2],
            "D": answers[3]
        }
        for key, value in choices.items():
            print(f"\t{key}. {value}")

        # Reset the answer_recieved flag to False for the next question
        answer_recieved = False
        stop_event = threading.Event()

        # Ask if the user wants a hint
        if hints_remaining > 0:
            hint_option = input(f"Do you want a hint? ({hints_remaining} hints remaining) (y/n): ").strip().lower()
            if hint_option == "y":
                get_hint(item['correct_answer'], item['incorrect_answers'])
                score -= 0.5  # Deduct points for using a hint
                hints_remaining -= 1  # Reduce the number of hints remaining
        else:
            print("You have no hints remaining.")

        def countdown():
            """Runs a timer for 9 seconds and checks if the user has answered."""
            for i in range(9, 0, -1):
                if stop_event.is_set():
                    return
                sys.stdout.write(f"\rTime left: [{'#' * (9 - i)}{' ' * i}] {i} seconds")
                sys.stdout.flush()
                time.sleep(1)
            if not stop_event.is_set():
                print("\n⏰ Time's up! Moving to the next question...\n")
                stop_event.set()

        # Start the countdown in a separate thread
        timer_thread = threading.Thread(target=countdown)
        timer_thread.start()

        user_answer = None  # Default to None in case of timeout

        while not stop_event.is_set():  # Stop waiting if time runs out
            user_answer = input("Enter your answer: ").strip().upper()

            if user_answer in choices:
                answer_recieved = True  # Mark question as answered
                stop_event.set()  # Stop the timer thread
                break

        # If the user didn't answer before time ran out
        if not answer_recieved:
            user_answer = None  # Ensure no answer is selected
            stop_event.set()  # Stop the timer thread

        timer_thread.join()  # Ensure the timer stops before moving on

        # Handle correct/incorrect answer checking
        if user_answer and choices[user_answer] == item['correct_answer']:
            print("\n✅ Correct!\n")
            score += 1
            time.sleep(1)
        else:
            print(f"\n❌ Sorry! The correct answer is {item['correct_answer']}\n")
            time.sleep(1)
        time.sleep(1)

    print("\n🎯 Quiz Over! 🎯")
    print(f"\nYour Final Score: {score} / 10")
    if score == 10:
        print("🏆 Congratulations! You got a perfect score! 🎉")
    elif score >= 6:
        print("👏 Great job! You did well! 😃")
    else:
        print("🙂 Nice attempt! Keep practicing! 💪")

    # Update the leaderboard
    player_name = input("Enter your name for the leaderboard: ").strip()
    update_leaderboard(player_name, score)

    # Display the leaderboard
    display_leaderboard()

    test = input("Do you want to play again? (y/n): ").strip().lower()
    if test == "y":
        quiz_up()
    else:
        print("\nThanks for playing! Goodbye! 👋")


def get_hint(correct_answer, incorrect_answers):
    """Provides a hint by revealing part of the correct answer."""
    hint = correct_answer[:len(correct_answer) // 2] + "_" * (len(correct_answer) - len(correct_answer) // 2)
    print(f"Hint: {hint}")


def update_leaderboard(player_name, score):
    """Updates the leaderboard with the player's score."""
    try:
        with open("leaderboard.json", "r") as file:
            high_scores = json.load(file)
    except FileNotFoundError:
        high_scores = {}

    # Update the player's score if it's higher than their previous score
    if player_name in high_scores:
        if score > high_scores[player_name]:
            high_scores[player_name] = score
    else:
        high_scores[player_name] = score

    # Save the updated leaderboard
    with open("leaderboard.json", "w") as file:
        json.dump(high_scores, file)


def display_leaderboard():
    """Displays the top 10 scores from the leaderboard."""
    try:
        with open("leaderboard.json", "r") as file:
            high_scores = json.load(file)
    except FileNotFoundError:
        print("\nNo scores recorded yet. Be the first to top the leaderboard! 🎉")
        return

    sorted_scores = sorted(high_scores.items(), key=lambda x: x[1], reverse=True)
    print("\n🏆 Leaderboard:")
    for rank, (name, score) in enumerate(sorted_scores[:10], start=1):
        print(f"{rank}. {name}: {score}")


quiz_up()




