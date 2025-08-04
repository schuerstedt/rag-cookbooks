from ollama_ocr import OCRProcessor

# Initialize OCR processor
ocr = OCRProcessor(model_name='Granite3.2-Vision', base_url="http://localhost:11434/api/generate")  # You can use any vision model available on Ollama
# you can pass your custom ollama api

# Process an image
result = ocr.process_image(
    image_path="./data/tesla_q3.pdf", # path to your pdf files "path/to/your/file.pdf"
    format_type="markdown",  # Options: markdown, text, json, structured, key_value
    #custom_prompt="convert to markdown, try to keep tables, layout etc. as much as possible", # Optional custom prompt
    language="English" # Specify the language of the text (New! 🆕)
)
print(result)