import logging
import sys
import cv2
import numpy as np
import pytesseract
import click
from pdf2image import convert_from_path

# Set logger configuration and formats
log = logging.getLogger("ocr-logger")
log.setLevel(logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

# print logs to the console
consoleHandler = logging.StreamHandler() 
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)

# Set command line interface with Click
@click.command(context_settings={"ignore_unknown_options": True})
@click.option('--input', help='Path to the input file')
@click.option('--output', help='Path to the output file')
@click.option('--verbose', '-v', is_flag=True, help="Output detailed logs")

# Main function in order to apply the OCR to the input file
def applyOcr(input, output, verbose):

	if verbose:
		log.info("Starting to parse the input parameters")

		# log input parameters
		log.info("Input parameters are parsed")
		log.info("input path: " + input)
		log.info("output path: " + output)
		log.info("verbose mode: " + str(verbose))

	txt = ""
	if input[-4:] == ".pdf":
		finalTxt = ""
		# convert pdf file to the image
		pages = convert_from_path(input, 500)
		# run through the each image
		for page in pages:
			# temporary file
			imageName = "temp.jpg"  
			# save each page as image
			page.save(imageName, "JPEG")
			# apply ocr to the current image
			txt = ocr(imageName)
			finalTxt += txt
		txt = finalTxt
	else:
		# apply ocr to the input file
		txt = ocr(input)

	if verbose:
		log.info("recognised text: \n" + str(txt))

	if verbose:
		log.info("Post processing to the recognised text is started: \n" + str(txt))
		txt = postProcessing(txt)
		log.info("After post processing: \n" + str(txt))

	if verbose:
		log.info("Starting to write to the file")

	# write output to the file
	writeToFile(txt, output)

	if verbose:
		log.info("Writing to the " + output + " is finished")

# OCR with pytesseract
def ocr(inputFile):

	img = cv2.imread(inputFile)
	img = imagePreProcessing(img)

	txt = pytesseract.image_to_string(img)

	return txt

# function for writing recognised text to the file
def writeToFile(txt, outputFile):

	f = open(outputFile, "w")
	f.write(str(txt))
	f.close()

	return txt

# Image preprocessing function which applies bilateral filter
def imagePreProcessing(img):

	# noise removal
	img = cv2.bilateralFilter(img, 25, 75, 75)
	return img

def postProcessing(txt):
	# initializing bad_chars_list
	bad_chars = [';', ':', '!', "*", '@', '#', '^']
	 
	# using replace() 
	for i in bad_chars :
		txt = txt.replace(i, '')

	return txt

if __name__ == "__main__":
	applyOcr()