import coloredlogs
import logging
import os
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas
from subprocess import call
from tkinter import *
from tkinter import messagebox 

''' 
This program uses tkinter GUI to prompt for user input, generates a PDF (lanscape A4 format, 2-by-3 tablej) 6 wavecards which will be used for the Vantage printer
'''

 
## Initializing logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


## Setup document format || TODO: Translate document inch to mm
A4_landscape_height, A4_landscape_width = A4
width = 296
height = 200
canvas_width = 97
canvas_height = 105
pdf_output_filename = "wavecard.pdf"


## Reportlab PDF creation with canvas
class PDFGenerator:
    def __init__(self, afgifteNr, sorteerplanNr, pocketNr):
        ## Init input values
        self.afgifteNr = afgifteNr
        self.sorteerplanNr = sorteerplanNr
        self.pocketNr = pocketNr

        ## Init a canvas to draw on
        self.canv = canvas.Canvas(pdf_output_filename,
                            pagesize=landscape(A4))

    
    def drawNaamVanKlant(self, x_pos, y_pos):
        self.canv.setFont('Helvetica', 10)
        self.canv.drawString(
            (x_pos * mm) + (5 * mm),
            y_pos * mm,
            "Naam van de klant:"
        )
        self.canv.setFont('Helvetica-Bold', 14)
        self.canv.drawString(
            (x_pos * mm) + (5 * mm),
            y_pos * mm - (5 * mm),
            "Postalia"
        )
        self.canv.drawString(
            (x_pos * mm) + (5 * mm),
            y_pos * mm - (10 * mm),
            "Belgium"
        )

    def drawAfgifteNummer(self, x_pos, y_pos):
        self.canv.setFont('Helvetica', 10)
        self.canv.drawRightString(
            x_pos * mm,
            y_pos * mm,
            "Afgiftenummer:"
        )
        self.canv.setFont('Helvetica-Bold', 10)
        self.canv.drawRightString(
            x_pos * mm,
            y_pos * mm - (5 * mm),
            self.afgifteNr
        )

    def drawNummerSorteerplan(self, x_pos, y_pos):
        self.canv.setFont('Helvetica', 10)
        self.canv.drawCentredString(
            x_pos * mm,
            y_pos * mm,
            "Nummer sorteerplan:"
        )
        self.canv.setFont('Helvetica-Bold', 18)
        self.canv.drawCentredString(
            x_pos * mm,
            y_pos * mm - (8*mm),
            self.sorteerplanNr
        )

    def drawSorteerplan(self, x_pos, y_pos):
        self.canv.setFont('Helvetica', 10)
        self.canv.drawString(
            (x_pos * mm) + (5*mm),
            y_pos * mm,
            "Sorteerplan:"
        )
        self.canv.setFont('Helvetica-Bold', 14)
        self.canv.drawString(
            (x_pos * mm) + (5*mm),
            y_pos * mm - (5*mm),
            "Easypost_V3.0"
        )

    def drawNummerpocket(self, x_pos, y_pos):
        self.canv.setFont('Times-Roman', 10)
        self.canv.drawRightString(
            x_pos * mm,
            y_pos * mm,
            "Nummer pocket:"
        )
        self.canv.setFont('Helvetica-Bold', 18)
        self.canv.drawRightString(
            (x_pos * mm),
            y_pos * mm - (8 * mm),
            self.pocketNr
        )

    
    def createCard(self):
        self.canv.saveState()
        ## Create an array that holds absolute positions for each container
        container_positions = [ (0, 0), (canvas_width, 0), (canvas_width * 2, 0), (0, canvas_height), (canvas_width, canvas_height), (canvas_width * 2, canvas_height) ]

        for container_format in container_positions:
            self.drawNaamVanKlant(container_format[0], 95+container_format[1])
            self.drawAfgifteNummer(90+container_format[0], 95+container_format[1])
            self.drawNummerSorteerplan(canvas_width/2+container_format[0], canvas_height/2+container_format[1])
            self.drawSorteerplan(container_format[0], 10+container_format[1])
            self.drawNummerpocket(90+container_format[0], 13+container_format[1])

        ## Draw container lines
        self.canv.line( 0, canvas_height * mm, width * mm, canvas_height * mm)
        self.canv.line( 0, canvas_height * 2 * mm, width * mm, canvas_height * 2 * mm)
        self.canv.line( canvas_width * mm, 0, canvas_width * mm, canvas_height * 2 * mm)
        self.canv.line( canvas_width * 2 * mm, 0, canvas_width * 2 * mm, canvas_height * 2 * mm)
        self.canv.line( canvas_width * 3 * mm, 0, canvas_width * 3 * mm, canvas_height * 2 * mm)
 
        self.canv.restoreState()
        self.canv.save()

## Tkinter GUI
class CreateGUI:
    def __init__(self, master):
        logger.debug("Initializing GUI")
        # setup 
        self.master = master
        self.master.title("Wavekaarten app")
        self.master.minsize(250, 100)    

        # Input 'afgiftenummer'
        Label(master, text="Afgiftenummer:").grid(row=0, column=1)
        self.afgifteNr = Entry(master)
        self.afgifteNr.grid(row=0, column=2)
        
        # autofocus input prompt
        self.afgifteNr.focus_set()

        # Input 'sorteerplan'
        Label(master, text="Nummer sorteerplan").grid(row=1, column=1)
        self.sorteerplanNr = Entry(master)
        self.sorteerplanNr.grid(row=1, column=2)

        # Input 'pocketnummer'
        Label(master, text="Pocket nummer:").grid(row=2, column=1)
        self.pocketNr = Entry(master)
        self.pocketNr.grid(row=2, column=2)


        # buttons
        self.greet_button = Button(master, text="Generate PDF", command=self.generatePDF, fg='green', height=1, width=10)
        self.greet_button.grid(columnspan=1, column=3, row=0)

        self.preview_button = Button(master, text="Preview", command=self.showPreview, fg='blue', height=1, width=10, state='disabled')
        self.preview_button.grid(columnspan=1, column=3, row=1)

        # self.print_button = Button(master, text="Print", command=self.printPDF, fg='red', height=1, width=10, state='disabled')
        # self.print_button.grid(columnspan=1, column=3, row=2)

        # self.close_button = Button(master, text="Close", command=self.closeApp, fg='red')
        # self.close_button.grid(columnspan=1, column=0, row=4, sticky=W)

    def generatePDF(self):
        # TODO: Validate user input
        if len(self.afgifteNr.get()) <= 0 or len(self.sorteerplanNr.get()) <= 0 or len(self.pocketNr.get()) <= 0:
            logging.warning('invalid input')        
            return
        

        logging.debug('Generating PDF...')
        pdfGen = PDFGenerator(self.afgifteNr.get(), self.sorteerplanNr.get(), self.pocketNr.get())

        ## Make buttons clickable when the pdf is generated
        self.preview_button['state'] = 'normal'

        pdfGen.createCard()

    # Use acrobat to view/print pdf
    def showPreview(self):
        logging.debug('Preparing preview...')
        os.startfile(pdf_output_filename)

    
    def printPDF(self):
        logging.debug('Preparing to print PDF...')                
        messagebox.showinfo("HOW TO", "To print a pdf, simply use the Preview button -> file -> print")


    def closeApp(self):
        logging.debug('Program terminating...')        
        self.master.quit()
        


if __name__ == "__main__":
    # Create GUI for user input and run program
    root = Tk()
    my_gui = CreateGUI(root)
    root.mainloop()



