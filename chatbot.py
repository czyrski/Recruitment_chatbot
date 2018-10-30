import speech_recognition as sr
import pyglet
import time
import winsound #tylko na windowsie, na lina czy maca trzeba inna biblioteke
import pdfkit #dodatkowo instalacja wkhtmltopdf
import smtplib #obsluga emaili
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from gtts import gTTS
from wit import Wit


r = sr.Recognizer()
client = Wit('HJZOKFJGOINR33CIRY6RD6AGLZ3FV2QD')  # token do chatbota powinien być ukryty



class Chatbot():

    def __init__(self):
        self.progres = 0
        self.continuity = True
        self.recognition_fail = False    #zmienna zeby nie powtarzal dwa razy tych samych kwestii w ifach
        #zmienne uzyskane podczas rozmowy drukowane pozniej do pdfa'
        self.name = None
        self.offer_pick = None
        self.experience = None
        self.technologies = None
        self.languages = None
        self.salary = None
        #lista kwestii dialogowych robota
        self.greeting = 'Cześć! Jestem Twoim osobistym czatbotem rekrutacyjnym! Jak masz na imię?'  # progres = 0
        self.ask_offers = 'Miło mi Cię poznać! Czy chcesz poznać aktualne oferty pracy?' # progres = 5
        self.show_offers = 'Aktualne oferty pracy to: programista PYTHON, oraz programista Java'  # progres = 10
        self.ask_joke = 'Świetnie! Czy zanim zaczniemy, chcesz usłyszeć dowcip? Tak dla rozluźnienia'  # progres = 20
        self.joke = "Jak się nazywa kot złomiarza? Puszek"  # progres = 30
        self.after_joke = 'No dobra, nad modułem humoru muszę jeszcze popracować'  # progres = 40
        self.ask_experience = 'Przejdźmy do rozmowy rekrutacyjnej. Jakie jest Twoje doświadczenie zawodowe?' # progres = 50
        self.ask_technologies = 'Super! Chciałbym teraz zapytać o technologię w których pracujesz. Wymień je po kolei, jedna po drugiej'  # progres = 60
        self.ask_languages = 'Świetnie, zanotowałem! Jak z Twoimi językami obcymi? Jakie znasz języki i jak określisz swój poziom w każdym z nich?' #progres = 70
        self.ask_salary = 'Pozostaje już ostatnie i najważniejsze pytanie: ile chciałbyś zarabiać?' #progres = 80
        self.interview_fin = 'Ekstra. Rozmowa dobiegła końca! Twoje dane zostaną przesłane do działu kadr a następnie skontaktuje się z tobą specjalista do spraw rekrutacji! Jeżeli kiedykolwiek będziesz chciał zmienić pracę - wiesz gdzie mnie szukać! Do usłyszenia!' # progres = 90
        self.not_sure = 'Przepraszam, chyba nie zrozumiałem! Czy możesz powtórzyć to jeszcze raz lub innymi słowami?'
        self.farewell = 'Dobrze! Jezeli kiedykolwiek zmienisz zdanie będę tutaj do Twojej dyspozycji.'


def voice_recognition(time_limit= 2, lang='pl-PL'):  # domyslnie voice nasluchiwany przez 3sek i w jezyku polskim

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        winsound.Beep(400,300) # trzeba zmienic glosnosc dzwiekow systemowych bo bedzie glosne
        audio = r.listen(source, phrase_time_limit=time_limit)
    try:
        detected_text = r.recognize_google(audio, language=lang)
        return detected_text
    except:
        detected_text = '0'
        return detected_text


def text_to_speech(text, lang='pl'):
    file = gTTS(text=text, lang=lang)
    filename = 'temp.mp3'
    file.save(filename)

    music = pyglet.media.load(filename)
    music.play()

    time.sleep(music.duration)
    # os.remove(filename)            # ta linia wali errorem - plik jest nadal uzywany


def witai_query_intent(query_content):

    try:
        resp = client.message(query_content)
        witai_query_intent.resp_confidence = resp['entities']['intent'][0]['confidence'] #taki zapis jest zwiazany z tym, ze chce uzywac zmiennych funkcji poza funkcja. Ta linia tworzy zmienna funkcji.
        witai_query_intent.resp_value = resp['entities']['intent'][0]['value']
        return resp
    except:
        witai_query_intent.resp_confidence = None
        witai_query_intent.resp_value = None
        return resp


def witai_query_name(query_content):

    try:
        resp = client.message(query_content)
        witai_query_name.name_confidence = resp['entities']['contact'][0]['confidence'] #taki zapis jest zwiazany z tym, ze chce uzywac zmiennych funkcji poza funkcja. Ta linia tworzy zmienna funkcji.
        witai_query_name.name = resp['entities']['contact'][0]['value']
        witai_query_name.suggested = True
        return True
    except:
        witai_query_name.name_confidence = None
        witai_query_name.name = None
        witai_query_name.suggested = False
        return False


def recruitment_chatbot(Chatbot): # tu trzeba przekazac do funkcji obiekt chatbota, pozamieniac na duze litery

    while Chatbot.continuity: # Chatbot.continuity == True

        if Chatbot.progres == 0:

            if not Chatbot.recognition_fail:
                text_to_speech(Chatbot.greeting)
            witai_query_name(voice_recognition())
            if witai_query_name.suggested and witai_query_name.name_confidence > 0.5:
                Chatbot.name = witai_query_name.name
                Chatbot.recognition_fail = False
                Chatbot.progres = 5
            else:
                text_to_speech(Chatbot.not_sure)
                Chatbot.recognition_fail = True

        if Chatbot.progres == 5:

            if not Chatbot.recognition_fail:
                text_to_speech(Chatbot.ask_offers)
            witai_query_intent(voice_recognition())
            if witai_query_intent.resp_value == 'get_actual_offers' or witai_query_intent.resp_value == 'acceptance' and witai_query_intent.resp_confidence > 0.5:
                Chatbot.progres = 10
                Chatbot.recognition_fail = False
            elif witai_query_intent.resp_value == 'chat_leave':
                Chatbot.continuity = False
                text_to_speech(Chatbot.farewell)
            else:
                text_to_speech(Chatbot.not_sure)
                Chatbot.recognition_fail = True
        if Chatbot.progres == 10:

            if not Chatbot.recognition_fail:
                text_to_speech(Chatbot.show_offers)
            witai_query_intent(voice_recognition())
            if witai_query_intent.resp_value == 'python_dev' or witai_query_intent.resp_value == 'java_dev' and witai_query_intent.resp_confidence > 0.5:
                Chatbot.offer_pick = witai_query_intent.resp_value
                Chatbot.progres = 20
                Chatbot.recognition_fail = False
            elif witai_query_intent.resp_value == 'negation' or witai_query_intent.resp_value == 'chat_leave':
                Chatbot.continuity = False
                text_to_speech(Chatbot.farewell)
            else:
                text_to_speech(Chatbot.not_sure)
                Chatbot.recognition_fail = True

        if Chatbot.progres == 20:

            if not Chatbot.recognition_fail:
                text_to_speech(Chatbot.ask_joke)
            witai_query_intent(voice_recognition())
            if witai_query_intent.resp_value == 'acceptance' and witai_query_intent.resp_confidence > 0.5:
                Chatbot.progres = 30
                Chatbot.recognition_fail = False
            elif witai_query_intent.resp_value == 'negation' and witai_query_intent.resp_confidence > 0.5:
                Chatbot.progres = 50
                Chatbot.recognition_fail = False
            elif witai_query_intent.resp_value == 'chat_leave':
                Chatbot.continuity = False
                text_to_speech(Chatbot.farewell)
            else:
                text_to_speech(Chatbot.not_sure)
                Chatbot.recognition_fail = True

        if Chatbot.progres == 30:

            text_to_speech(Chatbot.joke)
            text_to_speech(Chatbot.after_joke)
            Chatbot.progres = 50

        if Chatbot.progres == 50:

            text_to_speech(Chatbot.ask_experience)                  #czy potrzebna jest tutaj obsluga bledu???
            Chatbot.experience = voice_recognition(time_limit=5)
            Chatbot.progres = 60

        if Chatbot.progres == 60:

            text_to_speech(Chatbot.ask_technologies)
            Chatbot.technologies = voice_recognition(time_limit=10, lang='en-EN')
            Chatbot.progres = 70

        if Chatbot.progres == 70:

            text_to_speech(Chatbot.ask_languages)
            Chatbot.languages = voice_recognition(time_limit=6)
            Chatbot.progres = 80

        if Chatbot.progres == 80:

            text_to_speech(Chatbot.ask_salary)
            Chatbot.salary = voice_recognition(time_limit=3)
            Chatbot.progres = 90

        if Chatbot.progres == 90:

            text_to_speech(Chatbot.interview_fin)
            Chatbot.continuity = False


def creating_pdf_from_string(Chatbot):

    # string przekazany jest w formacie HTML, to pozwala ladnie formatowac wynikowe CV, zgodnie z zasadami htmla
    cv_string = f'<!DOCTYPE html><html><head><meta charset="UTF-8"></head><b><font size="+4" color="red">Curriculum vitae</font></b><br>\
                <b><font size="+2">{Chatbot.name}</font></b><br><br><br><br><p>Desired offer: {Chatbot.offer_pick}\
                </p><p>Experience: {Chatbot.experience}</p><p>Known technologies: {Chatbot.technologies}</p>\
                <p>Languages: {Chatbot.languages}</p><p>Desired salary: {Chatbot.salary}</p><br></body></html>'
    path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe' # był problem ze sciezkami wina, trzeba do funkcji przekazac sciezke do pliku w ktorym zaisntalowany jest wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    pdfkit.from_string(cv_string, f"{Chatbot.name}_CV.pdf", configuration=config)


def sending_email(Chatbot):

    email_user = 'czatbot.paulina@gmail.com'
    email_send = 'paulina.wuczkowska@gmail.com'
    subject = f'{Chatbot.name}_CV'

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    body = "Hello! I'm your recruitement bot! Here is some CV which I gather!"
    msg.attach(MIMEText(body, 'plain'))

    filename = f"{Chatbot.name}_CV.pdf"
    attachment = open(filename, 'rb')

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= "+filename)

    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_user, "1234abcd!") #haslo powinno byc ukryte

    server.sendmail(email_user, email_send, text)
    server.quit()

# MAIN
nowy_chatbot = Chatbot()

recruitment_chatbot(Chatbot)
creating_pdf_from_string(Chatbot)
sending_email(Chatbot)
