import pyttsx3
import vosk
import pyaudio
import openai
from bs4 import BeautifulSoup
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
import time

# Configura l'API di OpenAI
openai.api_key = 'your gpt api'

# Variabile globale per mantenere l'URL corrente
current_url = None

# Funzione per sintesi vocale
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
    engine.say(text)
    engine.runAndWait()

# Funzione per riconoscimento vocale con Vosk
def listen():
    model = vosk.Model("C:/Users/vince/PycharmProjects/speakipo/vosk-model-small-it-0.22")
    recognizer = vosk.KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
    stream.start_stream()

    print("Parla ora...")
    speak("Parla ora...")


    while True:
        data = stream.read(4000)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text = json.loads(result)["text"]
            print(f"Comando riconosciuto: {text}")
            return text
        else:
            data = stream.read(1000)

# Funzione per estrarre il contenuto di un sito
def extract_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    except requests.exceptions.RequestException as e:
        return f"Errore nel caricamento del sito: {e}"

# Funzione per interagire con ChatGPT
def ask_chatgpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sei un assistente utile e dettagliato."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Errore in ChatGPT: {e}"

# Funzione per gestire i cookie: accetta o rifiuta
def handle_cookies(driver, accept=False):
    try:
        keywords_accept = ["Accetta", "Conferma", "OK", "Accept", "Agree", "Accetto"]
        keywords_reject = ["Rifiuta", "Declina", "No", "Reject"]

        if accept:
            xpath_expression = " or ".join(
                [f"contains(text(), '{keyword}')" for keyword in keywords_accept]
            )
        else:
            xpath_expression = " or ".join(
                [f"contains(text(), '{keyword}')" for keyword in keywords_reject]
            )

        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//button[{xpath_expression}]"))
        )

        driver.execute_script("arguments[0].scrollIntoView();", button)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button))
        button.click()
        action = "accettati" if accept else "rifiutati"
        speak(f"Cookie {action}.")
    except (NoSuchElementException, TimeoutException):
        speak("Non è stato trovato il pulsante per gestire i cookie.")



# Funzione per rimuovere overlay e popup
def remove_overlays(driver):
    overlay_selectors = [
        "//*[contains(@class, 'overlay') or contains(@class, 'popup')]",  # Classi generiche
        "//div[contains(text(), 'Newsletter') or contains(text(), 'Iscriviti') or contains(text(), 'Subscribe') or contains(text(), 'Sign up') or contains(text(), 'Modal') or contains(text(), 'Registrati')]",  # Popup newsletter
        "//button[contains(text(), 'Chiudi') or contains(text(), 'No, grazie') or contains(text(), 'Close') or contains(text(), 'Dismiss') or contains(text(), 'Cancel')]",  # Pulsanti di chiusura
        "//*[contains(@style, 'position: fixed') or contains(@class, 'modal')]"  # Overlay con posizioni fisse o modali
    ]

    for selector in overlay_selectors:
        try:
            overlays = driver.find_elements(By.XPATH, selector)
            if overlays:
                for overlay in overlays:
                    # Nascondi gli overlay usando JavaScript
                    driver.execute_script("arguments[0].style.display = 'none';", overlay)
                    print(f"Overlay rimosso: {overlay}")
            else:
                print(f"Nessun overlay trovato per il selettore: {selector}")
        except Exception as e:
            print(f"Errore durante la rimozione dell'overlay: {e}")


# Inizializzazione globale del driver
driver = None

# Funzione per inizializzare il driver
def init_driver():
    global driver
    if driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(current_url)  # URL iniziale
        print("Driver inizializzato e finestra aperta.")


def navigate_site_dynamic(url, command):
    global current_url
    current_url = url  # Salva l'URL corrente

    # Usa il driver esistente (non creare una nuova finestra ogni volta)
    if driver is None:
        init_driver()

    driver.get(url)
    wait = WebDriverWait(driver, 20)

    try:
        # Attende che la pagina sia completamente caricata
        WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
        speak("Pagina caricata completamente.")

        # Rimuove gli overlay prima di proseguire
        remove_overlays(driver)

        handle_cookies(driver, accept=False)  # Rifiuta i cookie
        remove_overlays(driver)  # Rimuove popup e modali

        speak(f"Cerco la sezione '{command}'...")

        # Cerca l'elemento usando un XPATH più preciso o alternativo
        try:
            # Proviamo con un XPATH più generico e un'opzione aggiuntiva per la visibilità
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                                                f"//*[contains(text(), '{command}') or contains(@aria-label, '{command}') or contains(@class, '{command}')]"))
            )
            print(f"Elemento trovato: {element}")
        except TimeoutException:
            speak(f"Non ho trovato la sezione {command}.")
            return

        # Scroll per rendere l'elemento visibile
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

        # Verifica che l'elemento sia cliccabile
        try:
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element))
            print("Elemento cliccabile.")
        except TimeoutException:
            speak(f"Non posso cliccare sulla sezione {command}.")
            return

        # Tentativo di click normale
        try:
            ActionChains(driver).move_to_element(element).click().perform()
            speak(f"Navigazione verso {command} completata.")

            # Verifica che la navigazione sia avvenuta con successo
            WebDriverWait(driver, 10).until(lambda d: d.execute_script("return window.location.href") != current_url)
            print("Navigazione completata con successo.")
            current_url = driver.current_url  # Aggiorna l'URL corrente dopo la navigazione
        except Exception as e:
            print(f"Errore nel click normale: {e}")
            # Usa JavaScript per cliccare se il click normale fallisce
            driver.execute_script("arguments[0].click();", element)

            # Verifica la navigazione
            WebDriverWait(driver, 10).until(lambda d: d.execute_script("return window.location.href") != current_url)
            print("Navigazione completata con successo tramite JavaScript.")
            current_url = driver.current_url

    except Exception as e:
        print(f"Errore durante la navigazione: {e}")
        speak(f"Si è verificato un errore durante la navigazione.")


# Funzione per chiudere il driver (se desideri farlo)
def close_driver():
    global driver
    if driver is not None:
        driver.quit()
        driver = None
        print("Driver chiuso.")


# Funzione per gestire navigazione o interazione
def navigate_or_interact(command):
    global current_url

    if command.lower() in ["esci", "fine"]:
        speak("Arrivederci!")
        return False

    if "vai a" in command.lower() or "sezione" in command.lower():
        section = command.lower().split("vai a")[-1].strip()
        navigate_site_dynamic(current_url, section)
    else:
        content = extract_content(current_url)
        prompt = f"Rispondi alla domanda: {command} usando queste informazioni: {content}"
        answer = ask_chatgpt(prompt)
        print(f"ChatGPT: {answer}")
        speak(answer)

    return True

# Main
def main():
    global current_url

    speak("Benvenuto!")
    current_url = "https://www.alcott.eu/it_IT/uomo/saldi/maglieria?_gl=1*1ohquyb*_up*MQ..*_gs*MQ..*_ga*NTA3NTEyMzc2LjE3MzY4OTMyNjI.*_ga_G36T912VJS*MTczNjg5MzI2MC4xLjAuMTczNjg5MzI2MC4wLjAuMA..&gclid=Cj0KCQiAs5i8BhDmARIsAGE4xHxn7LPcLbFJfNWMxxyjvgfzTKc1yJAALgxw70WMQAg5vMz4XahcS9saAn-3EALw_wcB"
    print(f"URL iniziale: {current_url}")

    speak("Pagina caricata. Puoi navigare tra le sezioni o fare domande sul contenuto.")
    while True:
        speak("Cosa vuoi fare?")
        user_command = listen()
        if not navigate_or_interact(user_command):
            break

if __name__ == "__main__":
    main()
