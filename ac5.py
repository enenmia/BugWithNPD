import serial
import threading
from gtts import gTTS
import time
import os
import random
import speech_recognition as sr
from openai import OpenAI

interrupt_sentences = ["hmm", "yes", "ok", "well"]

arduino_port = '/dev/cu.usbserial-1120'  # Change this to the arduino port, sometimes 1100 sometimes 110
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate, timeout=1)
ser_lock = threading.Lock()

# 用锁包裹串口写操作
def write_to_serial(message):
    with ser_lock:
        ser.write(message)
# def write_to_serial_and_print(message):
#     print(message)
#     for char in message:
#         ser.write(char.encode())
#         time.sleep(0.01)  # Small delay between characters
#     ser.write('\n'.encode())  # Send a newline character as the end of the message



def generate_response_with_gpt3(text, api_key):
    client = OpenAI(api_key=api_key)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a friend of mine with Toxic personality disorder, which means you have a pattern of grandiosity, are in need for admiration, and lack of empathy. Pretend to be such a person and give a reaction to what the user just said. Limit your answer within 2 sentences and remember to showcase your toxic personality. Say it in first person perspective.Don't show too obciously your nature. Express it in a more subtle way and use some passive-aggresiveness.Also talk about yourself."},
                {"role": "user", "content": text}
            ],
            model="gpt-3.5-turbo",
        )
        if hasattr(chat_completion, 'choices') and chat_completion.choices:
            return chat_completion.choices[0].message.content
        else:
            return "No response generated."
    except Exception as e:
        print(f"Error in generating response: {e}")
        return "I'm sorry, I couldn't generate a response."

import uuid

def speak_text(text):
    language = 'en'
    temp_filename = "temp_" + str(uuid.uuid4()) + ".mp3"  
    myobj = gTTS(text=text, lang=language, slow=False)
    myobj.save(temp_filename)
    os.system(f"afplay {temp_filename}")
    os.remove(temp_filename)
    


def interrupter(stop_listening):
    last_time_spoken = time.time()
    while not stop_listening.is_set():
        current_time = time.time()
        # Check if 4 seconds have passed since the last interruption
        if current_time - last_time_spoken >= 4:
            sentence_to_speak = random.choice(interrupt_sentences)
            print(sentence_to_speak)
            speak_text(sentence_to_speak)
            last_time_spoken = current_time
        time.sleep(0.1)  # Short sleep for responsive stopping
def main():
recognized_hello = False
while not recognized_hello:
    write_to_serial(b'y')
    # write_to_serial_and_print("Are you ok? If not, remember I am always here for help")
    speak_text("Are you ok? If not, remember I am always here for help")
    print("Are you ok? If not, remember I am always here for help")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:
                print("Listening for 'hello'...")
                # write_to_serial_and_print("Listening for 'hello'...")
                audio = recognizer.listen(source, timeout=5)  # Adjust the timeout as needed
                recognized_text = recognizer.recognize_google(audio)
                if "hello" in recognized_text.lower():
                    # write_to_serial_and_print("Hello recognized. Listening for speech...")
                    print("Hello recognized. Listening for speech...")
                    
                    stop_listening = threading.Event()
                    interrupt_thread = threading.Thread(target=interrupter, args=(stop_listening,))
                    interrupt_thread.start()
                    conversation = []

                    while True:
                        try:
                            audio = recognizer.listen(source, timeout=5)  # Adjust the timeout as needed
                            recognized_text = recognizer.recognize_google(audio)
                            conversation.append(recognized_text)

                            if "do you have any suggestion" in recognized_text.lower():
                                stop_listening.set()
                                conversation_string = " ".join(conversation).replace("do you have any suggestion", "").strip()
                                print(f"Recognized: {conversation_string}")
                                # write_to_serial_and_print(f"Recognized: {conversation_string}")

                                gpt_response = generate_response_with_gpt3(conversation_string, "apikey")
                                print(gpt_response)
                                # write_to_serial_and_print(gpt_response)
                                write_to_serial(b'g')
                                speak_text(gpt_response)
                                time.sleep(5)

                                break
                        except sr.UnknownValueError:
                            continue
                        except sr.RequestError as e:
                            print(f"Could not request results from Google Speech Recognition service; {e}")
                            continue
                    break
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    while True:
        main()
