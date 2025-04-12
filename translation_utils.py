from googletrans import Translator

def translate_article(text):
  """Translates the given text to English."""
  translator = Translator()
  translated = translator.translate(text, dest='en')
  return translated.text