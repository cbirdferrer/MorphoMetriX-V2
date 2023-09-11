#usr/bin/env python
import os, sys, csv, traceback, platform
from datetime import date
import numpy as np
import webbrowser
from graphicsview import imwin, resource_path

from PySide6 import QtGui, QtCore
from PySide6.QtWidgets import QSlider ,QColorDialog ,QComboBox, QMainWindow, QApplication,  QWidget, QToolBar, QPushButton, QLabel, QLineEdit, QPlainTextEdit, QGridLayout, QFileDialog, QMessageBox, QInputDialog, QDockWidget, QSizePolicy, QRadioButton
from PySide6.QtGui import QShortcut, QIcon, QUndoCommand
from PySide6.QtCore import Qt

# ------------------------------
#   MorphoMetrix - Developed By:
#       Walter Torres
#       Kevin Bierlich
#       Clara Bird
#       Elliott Chimienti
# ------------------------------
#   Packages (Universal2 Python Install and Wheels for MacOS!):
#   Python 3.10.8
#   PySide6 6.5.1
#   Numpy 1.21.6
#   Scipy 1.9.1
# ------------------------------

class Window(QWidget):

    def __init__(self, iw):
        #init methods runs every time, use for core app stuff)
        super(Window, self).__init__()

        self.setWindowIcon(QIcon(resource_path("icon.PNG")))
        self.setWindowTitle("MorphoMetriX")
        self.iw = iw    # Reference for color picker

        self.label_id = QLabel("Image ID")
        self.id = QLineEdit()
        self.id.setText('0000')

        #Define custom attributes for pixel -> SI conversion
        self.label_foc = QLabel("Focal Length (mm):")
        self.focal = QLineEdit()
        self.focal.setText('25')

        self.label_alt = QLabel("Altitude (m):")
        self.altitude = QLineEdit()
        self.altitude.setText('50')

        self.label_pd = QLabel("Pixel Dimension (mm/pixel)")
        self.pixeldim = QLineEdit()
        self.pixeldim.setText('0.0045')

        self.label_widths = QLabel("# Width Segments:")
        self.numwidths = QLineEdit()
        self.numwidths.setText('10')

        self.label_side = QLabel("Mirror Side:")
        self.side_bias = QComboBox()
        self.side_bias.addItems(["None","Side A", "Side B"])

        self.label_scale = QLabel("Crosshair Size")
        self.scale_slider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.scale_slider.setMaximum(20)
        self.scale_slider.setValue(10)
        self.scale_slider.valueChanged.connect(self.slider_changed)

        self.label_not = QLabel("Notes:")
        self.notes = QPlainTextEdit()

        self.label_color = QLabel("Crosshair Color: ")
        self.button_color = QPushButton()
        self.button_color.setStyleSheet("background-color: red")
        self.button_color.clicked.connect(self.color_changed)

        self.manual = QPushButton("Manual", self)
        self.manual.clicked.connect(lambda: webbrowser.open('https://github.com/ZappyMan/MorphoMetriX/blob/master/MorphoMetriX_v2_manual.pdf'))

        self.exit = QPushButton("Exit", self)
        self.exit.clicked.connect(self.close_application)

        self.grid = QGridLayout()
        self.grid.addWidget(self.label_id, 1, 0)
        self.grid.addWidget(self.id, 1, 1)
        self.grid.addWidget(self.label_foc, 2, 0)
        self.grid.addWidget(self.focal, 2, 1)
        self.grid.addWidget(self.label_alt, 3, 0)
        self.grid.addWidget(self.altitude, 3, 1)
        self.grid.addWidget(self.label_pd, 4, 0)
        self.grid.addWidget(self.pixeldim, 4, 1)
        self.grid.addWidget(self.label_widths, 5, 0)
        self.grid.addWidget(self.numwidths, 5, 1)
        self.grid.addWidget(self.label_side,6,0)
        self.grid.addWidget(self.side_bias,6,1)
        self.grid.addWidget(self.label_scale,7,0)
        self.grid.addWidget(self.scale_slider,7,1)
        self.grid.addWidget(self.label_not, 8, 0)
        self.grid.addWidget(self.notes, 8, 1)
        self.grid.addWidget(self.label_color,9,0)
        self.grid.addWidget(self.button_color,9,1)
        self.grid.addWidget(self.manual, 10, 3)
        self.grid.addWidget(self.exit, 11, 3)
        self.setLayout(self.grid)

    # Function used by color picker button
    # Waits for user color selection, then passes color to imwin function "picked_color"
    def color_changed(self):
        color = QColorDialog().getColor()   # Returns QColor
        self.button_color.setStyleSheet("background-color: "+color.name())
        self.iw.picked_color = color

    # Function called when "crosshair size" slider value changes
    # Passed new size to imwin function "slider_moved"
    def slider_changed(self):
        self.scale_slider.value() # Value grab lags behind actually value?
        self.iw.slider_moved(self.scale_slider.value())

    # Called when user clicks "Exit" button 
    def close_application(self):
        choice = QMessageBox.question(self, 'exit', "Exit program?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if choice == QMessageBox.StandardButton.Yes:
            self.parent().deleteLater()
            self.parent().close()
        else:
            pass

#references:
#https://stackoverflow.com/questions/26901540/arc-in-qgraphicsscene/26903599#26903599
#https://stackoverflow.com/questions/27109629/how-can-i-resize-the-main-window-depending-on-screen-resolution-using-pyqt
class MainWindow(QMainWindow):

    def __init__(self, parent = None):
        super(MainWindow, self).__init__()
        self.setWindowIcon(QIcon(resource_path("icon.PNG")))
        self.setWindowTitle("MorphoMetriX")
        D = self.screen().availableGeometry()
        self.move(0,0)#center.x() + .25*D.width() , center.y() - .5*D.height() )
        self.resize( int(.95*D.width()), int(6*D.height()) )

        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowState.WindowMinimized
                            | QtCore.Qt.WindowState.WindowActive)
        self.activateWindow()

        self.iw = imwin()           # Image window
        self.subWin = Window(self.iw)
        self.setCentralWidget(self.iw)

        #Stacked dock widgets
        docked1 = QDockWidget("", self)
        docked2 = QDockWidget("", self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, docked1)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, docked2)
        docked1.setWidget(self.subWin)
        docked1.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        self.setCorner(QtCore.Qt.Corner.TopLeftCorner, QtCore.Qt.DockWidgetArea.LeftDockWidgetArea)
        self.setCorner(QtCore.Qt.Corner.TopRightCorner, QtCore.Qt.DockWidgetArea.RightDockWidgetArea)
        self.setCorner(QtCore.Qt.Corner.BottomLeftCorner, QtCore.Qt.DockWidgetArea.LeftDockWidgetArea)
        self.setCorner(QtCore.Qt.Corner.BottomRightCorner, QtCore.Qt.DockWidgetArea.RightDockWidgetArea)
        self.resizeDocks( (docked1,docked2), (400,400), QtCore.Qt.Orientation.Horizontal )

        self.exportButton = QPushButton("Export Measurements", self)
        self.exportButton.clicked.connect(self.export_measurements)
        self.exportButton.setEnabled(False)

        self.importImage = QPushButton("New Image", self)
        self.importImage.clicked.connect(self.file_open)

        self.lengthButton = QPushButton("Measure Length", self)
        self.lengthButton.clicked.connect(self.measure_length)
        self.lengthButton.setEnabled(False)
        #self.lengthButton.setCheckable(True)
        self.lengthNames = []

        self.widthsButton = QPushButton("Measure Widths", self)
        self.widthsButton.clicked.connect(self.measure_widths)
        self.widthsButton.setEnabled(False)
        self.widthNames = []

        self.areaButton = QPushButton("Measure Area", self)
        self.areaButton.clicked.connect(self.measure_area)
        self.areaButton.setEnabled(False)
        # self.areaButton.setCheckable(True)
        self.areaNames = []

        self.angleButton = QPushButton("Measure Angle", self)
        self.angleButton.clicked.connect(self.measure_angle)
        self.angleButton.setEnabled(False)
        # self.angleButton.setCheckable(True)
        self.angleNames = []

        shortcut_polyClose = QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Tab), self)
        shortcut_polyClose.activated.connect(self.iw.polyClose)

        self.undoButton = QPushButton("Undo", self)
        self.undoButton.clicked.connect(self.undo)
        self.undoButton.setEnabled(False)

        shortcut_undo = QShortcut(QtGui.QKeySequence('Ctrl+Z'), self)
        shortcut_undo.activated.connect(self.undo)

        self.bezier = QRadioButton("Bezier fit", self)
        self.bezier.setEnabled(True)
        self.bezier.setChecked(True)

        self.piecewise = QRadioButton("Piecewise", self)

        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Select new image to begin')

        self.tb = QToolBar('Toolbar')
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tb.addWidget(spacer)
        self.addToolBar(self.tb)
        self.tb.addWidget(self.importImage)
        self.tb.addWidget(self.exportButton)
        self.tb.addWidget(self.lengthButton)
        self.tb.addWidget(self.widthsButton)
        self.tb.addWidget(self.areaButton)
        self.tb.addWidget(self.angleButton)
        self.tb.addWidget(self.undoButton)
        self.tb.addWidget(self.bezier)
        self.tb.addWidget(self.piecewise)

    # New Project
    # Set all defaults and clear stored values
    def file_open(self):

        self.iw.scene.clear()
        self.image_name = QFileDialog.getOpenFileName(self, 'Open File')
        self.iw.pixmap = QtGui.QPixmap(self.image_name[0])
        self.iw.pixmap = self.iw.pixmap.scaled(
            self.iw.pixmap.width(),
            self.iw.pixmap.height(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation)
        self.iw.scene.addPixmap(self.iw.pixmap)  #add image
        # self.iw.setScene(self.iw.scene)

        #Adjust window size automatically?
        self.iw.fitInView(self.iw.scene.sceneRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.iw.scene.update()
        self.statusbar.showMessage('Select a measurement to make from the toolbar')

        self.lengthButton.setEnabled(True)
        self.areaButton.setEnabled(True)
        self.angleButton.setEnabled(True)
        self.exportButton.setEnabled(True)
        self.undoButton.setEnabled(False)
        self.bezier.setEnabled(True)
        self.bezier.setChecked(True)
        self.widthsButton.setEnabled(True)

    def measure_length(self):
        self.lel = QLineEdit(self)
        self.lel.move(130, 22)
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Length name')

        if ok:
            self.lel.setText(str(text))
            self.lengthNames.append(self.lel.text())

            self.undoButton.setEnabled(True)
            # QApplication.setOverrideCursor(QtCore.Qt.CursorShape.CrossCursor)  #change cursor
            self.iw.push_stack(self.lel.text(),1)
            self.statusbar.showMessage('Click initial point for length measurement')
        else:
            self.lengthButton.setChecked(False)

    def measure_widths(self):
        # self.iw.push_stack(, 3) # 3 = Ellipse item
        self.iw.measure_widths(self.lengthNames[-1])  # Call width function within graphics view

    def measure_angle(self):
        self.lea = QLineEdit(self)
        self.lea.move(130, 22)
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Angle name')

        if ok:
            self.lea.setText(str(text))
            # self.angleNames.append(self.lea.text())
            self.undoButton.setEnabled(True)
            # QApplication.setOverrideCursor(QtCore.Qt.CursorShape.CrossCursor)  #change cursor
            self.bezier.setEnabled(False)
            self.statusbar.showMessage('Click initial point for angle measurement')
            self.iw.push_stack(text,3)
        else:
            self.angleButton.setChecked(False)

    def measure_area(self):

        self.lea = QLineEdit(self)
        self.lea.move(130, 22)
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Area name')

        if ok:
            self.lea.setText(str(text))
            self.areaNames.append(self.lea.text())
            self.undoButton.setEnabled(True)
            self.iw.push_stack(text,2)               # 2 == AREA
            self.statusbar.showMessage('Click initial point for area measurement')
        else:
            self.areaButton.setChecked(False)

    # Create linked list (creation_record) of PyQt objects drawn to screen in order of creation
    # Pop length, angle, area, or width measurement lists depending on pop object in creation_record
    def undo(self):
        self.iw.undo()
        
    def export_measurements(self):
        # Gets largest image dimension and divides it by its on screen dimension?
        fac = max(self.iw.pixmap.width(), self.iw.pixmap.height()) / max(
            self.iw.pixmap_fit.width(),
            self.iw.pixmap_fit.height())  #scale pixel -> m by scaled image
        # Popup to get user save file input
        name = QFileDialog.getSaveFileName(
            self, 'Save File', self.image_name[0].split('.', 1)[0])[0]
        self.pixeldim = float(self.subWin.pixeldim.text())
        self.altitude = float(self.subWin.altitude.text())
        self.focal = float(self.subWin.focal.text())
        #okay in mm https://www.imaging-resource.com/PRODS/sony-a5100/sony-a5100DAT.HTM
        if name:
            #Convert pixels to meters
            areas = self.iw.areaValues * (
                fac * self.pixeldim * self.altitude / self.focal)**2
            values_optical = np.array([
                self.subWin.id.text(), self.image_name[0], self.focal,
                self.altitude, self.pixeldim
            ])

            names_optical = [
                'Image ID', 'Image Path', 'Focal Length', 'Altitude',
                'Pixel Dimension'
            ]

	        #Write .csv file
            print(f"Writing {name} to file")
            with open(name + '.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Object","Value","Value_unit"])  # Define Columns

                # Writes image & flight data
                for (f, g) in zip(names_optical, values_optical):
                    writer.writerow([f, g, "Metadata"])
                writer.writerow(['Mirror Side', self.subWin.side_bias.currentText(), "Metadata"])     # Side Bias (Not implemented yet)
                writer.writerow(['Notes', self.subWin.notes.toPlainText(), "Metadata"])     # Notes

                # Initial output in meters, then pixels
                self.iw.widths.clear() # Clear array for output
                self.iw.calculate_widths(self.subWin.side_bias.currentText())      # Calculate widths of MovingEllipses at export
                # Measurements in meters  \/ \/ \/ --------------------------------------------
                # Make check for first length line
                if self.lengthNames:
                    width_index = 0
                    for k,m in enumerate(self.lengthNames):
                        l = "{0:.2f}".format(self.iw.lengths[k] * fac * self.pixeldim * self.altitude / self.focal)
                        writer.writerow([m,l, "Meters"])  # Writes [Length Name][Length Measurement meters][Length measurement pixels]
                        if width_index < len(self.widthNames) and self.widthNames[width_index] == m: # Check if current length has widths or if width exists
                            # Iterate over width measurements
                            for idx,width in enumerate(self.iw.widths[width_index]):
                                l = "{0:.2f}".format(width * fac * self.pixeldim * self.altitude / self.focal)
                                width_percent = "{0:.1f}".format(((idx+1)/(len(self.iw.widths[width_index])+1))*100)
                                writer.writerow([self.widthNames[width_index]+"_w"+str(width_percent),l,"Meters"])
                            width_index += 1 # Incease index

                # Write angles (Fix output)
                for k, f in enumerate(self.angleNames):
                    line = "{0:.2f}".format(self.iw.angleValues[k])
                    writer.writerow([f,line, "Degrees"])

                # Write Area ()
                for k, f in enumerate(self.areaNames):
                    line = "{0:.2f}".format(areas[k])
                    writer.writerow([f,line,"Square Meters"])

                # Measurements in pixels \/ \/ \/ --------------------------------------------
                # Make check for first length line
                if self.lengthNames:
                    width_index = 0
                    for k,m in enumerate(self.lengthNames):
                        l = "{0:.2f}".format(self.iw.lengths[k])    # Pixels
                        writer.writerow([m,l, "Pixels"])  # Writes [Length Name][Length Measurement meters][Length measurement pixels]
                        if width_index < len(self.widthNames) and self.widthNames[width_index] == m: # Check if current length has widths or if width exists
                            # Iterate over width measurements
                            for idx,width in enumerate(self.iw.widths[width_index]):
                                l = "{0:.2f}".format(width)
                                width_percent = "{0:.1f}".format(((idx+1)/(len(self.iw.widths[width_index])+1))*100)
                                writer.writerow([self.widthNames[width_index]+"_w"+str(width_percent),l,"Pixels"])
                            width_index += 1 # Incease index

                # Write angles
                for k, f in enumerate(self.angleNames):  #write angles
                    line = "{0:.2f}".format(self.iw.angleValues[k])
                    writer.writerow([f, line,"Degrees"])

                # Write Area
                for k, f in enumerate(self.areaNames):
                    line = "{0:.2f}".format(self.iw.areaValues[k])
                    writer.writerow([f,line,"Pixels"])

            #Export image
            self.iw.fitInView(self.iw.scene.sceneRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            pix = QtGui.QPixmap(self.iw.viewport().size())
            self.iw.viewport().render(pix)
            pix.save(name + '-measurements.png')

class angleData():  #actually need separate class from posdata? probably not

    def __init__(self, t):
        self.t = t

    def update(self, add_t):
        self.t = np.append(self.t, add_t)

    def downdate(self):
        self.t = self.t[:-1]


# Crash handler for error logging
def except_hook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setWindowTitle("Error")
    dialog.setText("Error: Crash caught, save details to file.")
    dialog.setDetailedText(tb)
    dialog.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel)
    ret = dialog.exec()   # Show dialog box
    if ret == QMessageBox.StandardButton.Save:
        path = QFileDialog().getExistingDirectory(dialog,'Select a directory')
        if(path):
            path += '/' + str(date.today()) + "_Morphometrix_Crashlog" + ".txt"
            print("saving: ", path)
            with open(path, 'w') as file:
                file.write("System: " + platform.system() + '\n')
                file.write("OS: " + os.name + '\n')
                file.write("Python Version: " + platform.python_version() + '\n')
                file.write("Python Implementation: " + platform.python_implementation() + '\n')
                file.write("Release: " + platform.release() + '\n')
                file.write("Version: " + platform.version() + '\n')
                file.write("Machine: " + platform.machine() + '\n')
                file.write("Processor: " + platform.processor() + '\n' + '\n')
                file.write(tb)

    QApplication.quit() # Quit application

def main():
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    app.exec()
    sys.exit()


if __name__ == "__main__":
    main()
