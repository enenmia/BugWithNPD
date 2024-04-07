import serial
import threading
from gtts import gTTS
import time
import os
import random
import speech_recognition as sr
from openai import OpenAI

interrupt_sentences = ["enheng", "yes", "ok", "well"]

arduino_port = '/dev/cu.usbserial-1110'  # Change this to the arduino port, sometimes 1100 sometimes 110
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate, timeout=1)
ser_lock = threading.Lock()

# 用锁包裹串口写操作
def write_to_serial(message):
    with ser_lock:
        ser.write(message)

# 修改所有 ser.write 的调用


def generate_response_with_gpt3(text, api_key):
    client = OpenAI(api_key=api_key)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a friend of mine with Narcissistic personality disorder, which means you have a pattern of grandiosity, are in need for admiration, and lack of empathy. Pretend to be such a person and give a reaction to what the user just said. Limit your answer within 2 sentences and remember to showcase your NPD syndrome. Say it in first person perspective.Don't show too obciously your NPD nature. Express it in a more subtle way and use some passive-aggresiveness.Also talk about yourself."},
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
    while not stop_listening.is_set():
        time.sleep(4) 
        sentence_to_speak = random.choice(interrupt_sentences)
        print(sentence_to_speak)
        speak_text(sentence_to_speak) 


def main():
    
    speak_text("Are you ok? If not, remember I am always here for help")
    print("Are you ok? If not, remember I am always here for help")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            audio = recognizer.listen(source)
            
            try:
                recognized_text = recognizer.recognize_google(audio)
                if "hello" in recognized_text.lower():
                    print("Hello recognized. Listening for speech...")
                    # time.sleep(4)
                    stop_listening = threading.Event()
                    interrupt_thread = threading.Thread(target=interrupter, args=(stop_listening,))
                    interrupt_thread.start()
                    conversation = []

            
                

                    while True:
                        
                        
                        
                        audio = recognizer.listen(source)
                        try:
                            recognized_text = recognizer.recognize_google(audio)
                            conversation.append(recognized_text)

                            if "do you have any suggestion" in recognized_text.lower():
                                stop_listening.set()
                                conversation_string = " ".join(conversation).replace("do you have any suggestion", "").strip()
                                print(f"Recognized: {conversation_string}")


                                gpt_response = generate_response_with_gpt3(conversation_string, "your-api-key")
                                print(gpt_response)
                                write_to_serial(b'g')
                                speak_text(gpt_response)
                                

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
    main()