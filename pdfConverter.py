import tkinter as tk
from tkinter import filedialog, messagebox
import fitz
import pytesseract
from PIL import Image
import io
from reportlab.pdfgen import canvas
from textwrap import wrap

def extract_images_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        for img_index, img in enumerate(doc[page_num].get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)
    return images

def perform_ocr(images):
    text_list = []
    for image in images:
        text = pytesseract.image_to_string(image)
        text_list.append(text)
    return text_list

def create_new_pdf(text_list, output_pdf_path):
    c = canvas.Canvas(output_pdf_path)
    page_width = 550
    text_object = c.beginText(50, 800)  # Start text at (x=50, y=800)
    text_object.setFont("Helvetica", 12)

    for page_text in text_list:
        wrapped_lines = []
        for line in page_text.split("\n"):
            wrapped_lines.extend(wrap(line, width=80))

        for wrapped_line in wrapped_lines:
            text_object.textLine(wrapped_line)

        text_object.textLine("")  # Add a blank line between text blocks

    c.drawText(text_object)
    c.showPage()
    c.save()


def pdf_conversion(pdf_path, output_pdf_path):
    images = extract_images_from_pdf(pdf_path)
    text_list = perform_ocr(images)
    create_new_pdf(text_list, output_pdf_path)


def select_file():
    """Open file dialog for PDF selection."""
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        file_label.config(text=f"Selected: {file_path}")
        global selected_file
        selected_file = file_path

def run_conversion():
    if not selected_file:
        messagebox.showerror("Error", "No file selected!")
        return
    output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not output_path:
        return
    try:
        pdf_conversion(selected_file, output_path)
        messagebox.showinfo("Success", f"Searchable PDF created: {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

root = tk.Tk()
root.title("PDF OCR Tool")
root.geometry("400x200")

file_label = tk.Label(root, text="No file selected", wraplength=350)
file_label.pack(pady=10)

select_button = tk.Button(root, text="Select PDF", command=select_file)
select_button.pack(pady=5)

# Run Conversion Button
run_button = tk.Button(root, text="Run OCR and Convert", command=run_conversion)
run_button.pack(pady=10)

selected_file = None
root.mainloop()