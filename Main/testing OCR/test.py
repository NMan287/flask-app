from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

image = Image.open('C:/Users/richb/Desktop/Project/Main/testing OCR/test.png')
text = pytesseract.image_to_string(image)   
print(text)