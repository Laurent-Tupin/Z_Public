import pyttsx3
import PyPDF2


def ReadAudioBook(str_BookPath, int_pageToStartRead = 1):
    # Open PDF
    book = open(str_BookPath, 'rb')
    pdfReader = PyPDF2.PdfFileReader(book)
    nbPages = pdfReader.numPages
    print('nbPages in PDF:', nbPages)
    
    # Read Aloud
    speaker = pyttsx3.init()
    for i_page in range(int_pageToStartRead, nbPages):
        page = pdfReader.getPage(i_page)
        text = page.extractText()
        speaker.say(text)
    speaker.runAndWait()


# PARAM
str_BookPath = r'C:\Users\laurent.tupin\Documents\0. HR\Group Life Member Briefing_2018 by Aon.pdf'
int_pageToStartRead = 7

ReadAudioBook(str_BookPath, int_pageToStartRead)