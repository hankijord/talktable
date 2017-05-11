import time, os, webbrowser, sys, pyaudio
from pprint import pprint
import speech_recognition as sr

# Imports the Google Cloud client library
from google.cloud import language

# Import the search function from search.py
from search import Searcher 

# import thread for threading
import thread

# import urllib for code checking
import urllib

# Requires that your env/bin/activate script contains the following line
# and that the env/credentials.json file exists
# eg. export GOOGLE_APPLICATION_CREDENTIALS=$VIRTUAL_ENV/credentials.json

# A class to parse audio from either a microphone or file and provide keywords from it
class AudioParser:
    # Initialise with microphone name 
    def __init__(self, inputName):
        self.recogniser = sr.Recognizer()

        # Initiates a microphone from its name 
        for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
            if mic_name == inputName:
                self.microphone = sr.Microphone(i)
                self.name = mic_name

        # Google's Natural Language Client
        self.language_client = language.Client()

    # Start listening through microphone
    def start_listening(self):
        with self.microphone as source:
            self.recogniser.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening
        
        print("Started listening through " + self.name + "...")
    
        # Starts listening in another thread, use self.stop_listening() to stop
        self.stop_listening = self.recogniser.listen_in_background(self.microphone, self.thread_callback)
    
    # Analyses the keywords of a phrase
    def analyse_keywords(self, phrase):
        document = self.language_client.document_from_text(phrase)
        # sentiment = document.analyze_sentiment().sentiment
        entity_response = document.analyze_entities()

        # Empty keyword list
        keywords = []
        for entity in entity_response.entities:
            print(self.name + ": Google Natural Language thinks you are talking about '" 
                    + entity.name + "' which is a " + entity.entity_type)
            if entity.metadata:
                print(self.name + ":        - Here's some more useful metadata about '" + entity.name + "': %s" % (entity.metadata))
            keywords.append(entity.name)
        return keywords

    # Analyses the sentiment of a text phrase
    def analyse_sentiment(self, phrase):
        document = self.language_client.document_from_text(phrase)
        sentiment = document.analyze_sentiment().sentiment
        percentage = sentiment.magnitude * 100
        emotion = "neutral"
        if sentiment.score > 0:
            emotion = "\033[92m" + "positive" + "\033[0m"
        elif sentiment.score < 0:
            emotion = "\033[91m" + "negative" + "\033[0m"
        else:
            emotion = "neutral"

        print(self.name + ": Google thinks what you said was "+str(percentage)+"% "+emotion) 
        return 
    
    # Searches for images and downloads due to 
    def download_images(self, keywords):
        searcher = Searcher()
        for keyword in keywords:
            print(self.name + ": Searching for " + keyword + " image.")
            imageResults = searcher.searchImages(keyword)
            if self.HTTP_code_check(imageResults[0]):
                print('appending link...')
                searcher.appendLink(imageResults[0])
            else:
                pass
             
    # Threaded callback
    def thread_callback(self, recognizer, audio):
        thread.start_new_thread(self.callback, (recognizer,audio))
             
    # A callback to analyse the speech to text
    def callback(self, recognizer, audio):
        try:
            self.results = self.recogniser.recognize_google_cloud(audio)
            print("_" * 20)
            print("")
            print(self.name + ": Google Cloud Speech thinks you said: \n'" + self.results +"'\033")
            self.aftermath(self.results)
        except sr.UnknownValueError:
            print(self.name + ": Google Cloud Speech could not understand audio.")
            print(self.name + ": Retrying...")
        except sr.RequestError as e:
            print(self.name + ": Could not request results from Google Cloud Speech service; {0}".format(e))
    
    # Checks whether URL is valid
    def HTTP_code_check(self, url):
        print('Checking HTTP Code...')
        print(url)
        #try:
        a = urllib.urlopen(url)
        print (a.getcode())
        if a.getcode() == 200:
            print ('link OK!')
            return True
        else:
            print ('link HTTPCode fucked')
            return False
        '''
        except:
            print ('link fucked')
            return False
        '''
    
    def aftermath(self, results):
        keywords = self.analyse_keywords(results)
        self.download_images(keywords) 
        print("")
        self.analyse_sentiment(results)
        print("")

def print_input_list():
    print "Input List:"
    print "\n".join(sr.Microphone.list_microphone_names())
    print ""

def main():
    print_input_list()

    audio = AudioParser("Built-in Microph")  
    audio.start_listening()

    # listens infinitely
    while True: time.sleep(0.1)

if __name__ == '__main__':
    main()