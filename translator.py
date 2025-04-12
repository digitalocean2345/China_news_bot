# translator.py
import requests
import logging
from config import (MS_TRANSLATOR_KEY, MS_TRANSLATOR_REGION,
                    TRANSLATOR_API_VERSION, TRANSLATOR_TIMEOUT)

def translate_text(text):
    """Translates text from Chinese (Simplified) to English using Microsoft Translator."""
    if not MS_TRANSLATOR_KEY:
        logging.warning("No Microsoft Translator key configured - returning original text.")
        return text
    if not text or text.isspace():
        logging.debug("Skipping translation for empty text.")
        return text

    endpoint = "https://api.cognitive.microsofttranslator.com/translate"
    params = {
        'api-version': TRANSLATOR_API_VERSION,
        'from': 'zh-Hans',
        'to': 'en'
    }
    headers = {
        'Ocp-Apim-Subscription-Key': MS_TRANSLATOR_KEY,
        'Ocp-Apim-Subscription-Region': MS_TRANSLATOR_REGION,
        'Content-Type': 'application/json'
    }
    body = [{'text': text}]

    try:
        response = requests.post(endpoint, params=params, headers=headers, json=body, timeout=TRANSLATOR_TIMEOUT)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        translation_result = response.json()

        if translation_result and isinstance(translation_result, list) and 'translations' in translation_result[0]:
            translated_text = translation_result[0]['translations'][0]['text']
            logging.debug(f"Translated '{text[:30]}...' to '{translated_text[:30]}...'")
            return translated_text
        else:
            logging.error(f"Unexpected translation API response format for text: {text[:50]}...")
            return text # Return original on unexpected format

    except requests.exceptions.RequestException as e:
        logging.error(f"Translation network error: {e}")
        return text  # Return original text if translation fails
    except (KeyError, IndexError, Exception) as e:
        logging.error(f"Translation processing error: {e}")
        return text # Return original text on other errors
    
