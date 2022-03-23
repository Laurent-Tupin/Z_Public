import pyttsx3
import speech_recognition as sr
# import PyAudio


def SetVoices(speaker, bl_womanVoice = False):
    voices = speaker.getProperty('voices')
    if bl_womanVoice:
        speaker.setProperty('voice', voices[1].id)
    else: speaker.setProperty('voice', voices[0].id)



listener = sr.Recognizer()
engine = pyttsx3.init()
SetVoices(engine, True)
engine.say('I am starting...')

# Listening
try:
    with sr.Microphone() as source:
        engine.say('I am Listening...')
        print('Listening...')
        voice = listener.listen(source)
        command = listener.recognize_google(voice)
        if 'tupinexa' in command.lower():
            print(command)
            engine.say(command)    
except Exception as err: print('ERROR: ', err)


engine.runAndWait()
            