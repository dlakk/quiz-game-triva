#Create a multiple-choice quiz with questions about Python, movies, or any fun topic! Display scores at the end and allow the user to play again

import requests
import random
import html  # Import to decode HTML entities
import time
import threading #import threading to create a timer and enable parallel code excution for the timer function

base_url = "https://opentdb.com/api.php?amount=10&category=18&difficulty=medium&type=multiple"


def quiz_up():
  response = requests.get(base_url)


  #start game
  if response.status_code == 200:
    data= response.json()
  

    print("\n************Welcome to the quiz game**************\n")

    print("📝 You will be asked 10 questions.")
    print("🏆 Answer correctly to win the game and be a champ!")
    time.sleep(2)
    print("\n🛑 Rules:")
    print("🔹 You have 4 choices (A, B, C, D).")
    print("🔹 Type the letter of the correct option.")
    print("🔹 You have **9 seconds** to answer each question!\n")
    time.sleep(3)

    start= input("Are you ready to play? (y/n): ").strip().lower()
    if start == "n":
      print("Goodbye! 👋")
    else:
      print("🎮\nLet's get started!\n")
      time.sleep(2)
      game(data)

  else:
    print(f"⛔failed to retrived data from the api. Status code: {response.status_code}")  

def game(data):
  """Runs the quiz game logic."""
  global answer_recieved
  score = 0

  for count, item in enumerate(data['results'], start=1):
    item['question'] = html.unescape(item['question'])
    item['correct_answer'] = html.unescape(item['correct_answer'])  
    item['incorrect_answers'] = [html.unescape(answer) for answer in item['incorrect_answers']]

    answers = [item['correct_answer']] + item['incorrect_answers'] #make the correct answer a list and add  it to the incorrect answers
    random.shuffle(answers) #shuffle the answers

    print(f"{count}. {item['question']}")
    choices ={
      "A": answers[0],
      "B": answers[1],
      "C": answers[2],
      "D": answers[3]
    }
    for key, value in choices.items():
      print(f"\t{key}.{value}")
    
    # Reset the answer_recieved flag to False for the next question
    answer_recieved = False
    stop_event = threading.Event()


    def countdown():
      """Runs a timer for 9 seconds and checks if the user has answered"""      
      for _ in range(9):
        
        if stop_event.is_set():
          return
        time.sleep(1)
      if not stop_event.is_set():
        print("\n⏰ Time's up! Moving to the next question...\n")
        print("press enter")
        stop_event.set()

    #start the countdown in a separate thread
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
  test = input("Do you want to play again? (y/n): ").strip().lower()
  if test == "y":
    quiz_up()
  else:
    print("\nThanks for playing! Goodbye! 👋")  


quiz_up()




