import img2pdf
from PIL import Image
import os
from django.conf import settings


def pdf_converter(file):
    try:
        file.converted_file = file.input_file
        file.save()
        return True
    except:
        return False


def jpg_converter(file):
    try:
        pdf_path_raw = file.get_pdf_path_raw
        pdf_path = file.get_pdf_path
        pdf_bytes = img2pdf.convert(file.input_file.path)
        pdf_file = open(pdf_path_raw, "wb")
        pdf_file.write(pdf_bytes)
        pdf_file.close()
        file.converted_file = pdf_path
        file.save()
        return True
    except Exception as e:
        return False


def jpeg_converter(file):
    try:
        pdf_path_raw = file.get_pdf_path_raw
        pdf_path = file.get_pdf_path
        pdf_bytes = img2pdf.convert(file.input_file.path)
        pdf_file = open(pdf_path_raw, "wb")
        pdf_file.write(pdf_bytes)
        pdf_file.close()
        file.converted_file = pdf_path
        file.save()
        return True
    except Exception as e:
        return False



def png_converter(file):
    try:
        png_path = file.input_file.path
        png = Image.open(png_path)
        jpg_path = file.get_jpg_path_temp
        rgb_im = png.convert('RGB')
        png.close()
        os.remove(png_path)
        rgb_im.save(jpg_path)
        file.input_file = jpg_path
        file.save()
        return True
    except Exception as e:
        print(e)
        return False



