import os
import shutil
from multiprocessing import Pool, cpu_count

from docx import Document
from docx.shared import Inches
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from tqdm import tqdm

def convert_single_pdf_to_image(args):
    pdf_path, img_path, dpi = args
    try:
        images = convert_from_path(pdf_path, dpi=dpi, fmt='png')
        if not images:
            return None
        images[0].save(img_path, 'PNG')
        return img_path
    except Exception:
        return None

def pdf_to_word_appendix(
    pdf_path,
    word_output,
    temp_dir='temp_pages',
    dpi=300,
    width=8.27,
    height=11.69,
    num_proc=cpu_count(),
    cleanup=True
):
    os.makedirs(temp_dir, exist_ok=True)

    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)

    single_page_pdfs = []
    for i, page in enumerate(tqdm(reader.pages, desc="Splitting PDF")):
        writer = PdfWriter()
        writer.add_page(page)
        single_pdf_path = os.path.join(temp_dir, f"page_{i:04d}.pdf")
        with open(single_pdf_path, "wb") as f_out:
            writer.write(f_out)
        single_page_pdfs.append(single_pdf_path)

    image_paths = [os.path.join(temp_dir, f"page_{i:04d}.png") for i in range(num_pages)]
    convert_args = [(pdf, img, dpi) for pdf, img in zip(single_page_pdfs, image_paths)]

    with Pool(processes=num_proc) as pool:
        results = list(tqdm(pool.imap(convert_single_pdf_to_image, convert_args),
                            total=num_pages, desc="Converting to images"))

    valid_image_paths = [img for img in results if img is not None]
    if not valid_image_paths:
        raise RuntimeError("No images were generated. Check your PDF and Poppler setup.")

    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0)
        section.bottom_margin = Inches(0)
        section.left_margin = Inches(0)
        section.right_margin = Inches(0)

    for img_path in sorted(valid_image_paths):
        doc.add_picture(img_path, width=Inches(width), height=Inches(height))

    doc.save(word_output)

    if cleanup:
        shutil.rmtree(temp_dir, ignore_errors=True)
