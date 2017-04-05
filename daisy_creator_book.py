#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Autor: Joerg Sorge
Distributed under the terms of GNU GPL version 2 or later
Copyright (C) Joerg Sorge joergsorge at gooogel
2012-06-20

Dieses Programm
- kopiert mp3-Files fuer die Verarbeitung zu Daisy-Buechern
- erzeugt die noetigen Dateien fuer eine Daisy-Struktur.

Zusatz-Modul benoetigt:
python-mutagen
sudo apt-get install python-mutagen

GUI aktualisieren mit:
pyuic4 daisy_creator_book.ui -o daisy_creator_book_ui.py
"""

from PyQt4 import QtGui, QtCore
import sys
import os
import shutil
import datetime
from datetime import timedelta
import subprocess
import string
import re
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.id3 import ID3NoHeaderError
import ConfigParser
import daisy_creator_book_ui


class DaisyCopy(QtGui.QMainWindow, daisy_creator_book_ui.Ui_DaisyMain):
    """
    mainClass
    The second parent must be 'Ui_<obj. name of main widget class>'.
    """

    def __init__(self, parent=None):
        """init the mainClass"""
        # This is because Python does not automatically
        # call the parent's constructor.
        super(DaisyCopy, self).__init__(parent)
        # Pass this "self" for building widgets and
        # keeping a reference.
        self.setupUi(self)
        # to display debugMessages on console
        self.app_debugMod = "yes"
        # dataPaths
        self.app_bookPfad = QtCore.QDir.homePath()
        self.app_bookPfadMeta = QtCore.QDir.homePath()
        # connect Actions to GUIElements
        # we need ext package lame
        self.app_lame = ""
        self.connectActions()

    def connectActions(self):
        """define Actions"""
        self.toolButtonCopySource.clicked.connect(self.actionOpenCopySource)
        self.toolButtonCopyDest.clicked.connect(self.actionOpenCopyDest)
        self.toolButtonMetaFile.clicked.connect(self.actionOpenMetaFile)
        self.commandLinkButton.clicked.connect(self.actionRunCopy)
        self.commandLinkButtonMeta.clicked.connect(self.metaLoadFile)
        self.commandLinkButtonDaisy.clicked.connect(self.actionRunDaisy)
        self.toolButtonDaisySource.clicked.connect(self.actionOpenDaisySource)
        self.pushButtonClose1.clicked.connect(self.actionQuit)
        self.pushButtonClose2.clicked.connect(self.actionQuit)

    def readConfig(self):
        """read Config from file"""
        fileExist = os.path.isfile("daisy_creator_book.config")
        if fileExist is False:
            self.showDebugMessage(u"File not exists")
            self.textEdit.append(
                "<font color='red'>"
                + "Config-Datei konnte nicht geladen werden: </font>"
                + "daisy_creator_mag.config")
            return

        config = ConfigParser.RawConfigParser()
        config.read("daisy_creator_book.config")
        self.app_bookPath = config.get('Ordner', 'Buch')
        self.app_bookPathMeta = config.get('Ordner', 'Buch-Meta')
        self.app_lame = config.get('Programme', 'LAME')

    def readHelp(self):
        """read Readme from file"""
        fileExist = os.path.isfile("README.md")
        if fileExist is False:
            self.showDebugMessage("File not exists")
            self.textEdit.append(
                "<font color='red'>"
                + "Hilfe-Datei konnte nicht geladen werden: </font>"
                + "README.md")
            return

        fobj = open("README.md")
        for line in fobj:
            self.textEditHelp.append(line)
        # set cursor on top of helpfile
        cursor = self.textEditHelp.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start,
                            QtGui.QTextCursor.MoveAnchor, 0)
        self.textEditHelp.setTextCursor(cursor)
        fobj.close()

    def actionOpenCopySource(self):
        """Source of audios to copy"""
        # QtCore.QDir.homePath()
        dirSource = QtGui.QFileDialog.getExistingDirectory(
                        self,
                        "Quell-Ordner",
                        self.app_bookPath
                    )
        # Don't attempt to open if open dialog
        # was cancelled away.
        if dirSource:
            self.lineEditCopySource.setText(dirSource)
            self.textEdit.append("Quelle:")
            self.textEdit.append(dirSource)

    def actionOpenDaisySource(self):
        """Source for daisyfie audios """
        dirSource = QtGui.QFileDialog.getExistingDirectory(
                        self,
                        "Quell-Ordner",
                        self.app_bookPath
                    )
        # Don't attempt to open if open dialog
        # was cancelled away.
        if dirSource:
            self.lineEditDaisySource.setText(dirSource)
            self.textEdit.append("Quelle:")
            self.textEdit.append(dirSource)

    def actionOpenCopyDest(self):
        """Destination for copying audio"""
        dirDest = QtGui.QFileDialog.getExistingDirectory(
                        self,
                        "Ziel-Ordner",
                        self.app_bookPath
                    )
        # Don't attempt to open if open dialog
        # was cancelled away.
        if dirDest:
            self.lineEditCopyDest.setText(dirDest)
            self.textEdit.append("Ziel:")
            self.textEdit.append(dirDest)

    def actionOpenMetaFile(self):
        """Metafile to load"""
        mfile = QtGui.QFileDialog.getOpenFileName(
                        self,
                        "Daisy_Meta",
                        self.app_bookPathMeta
                    )
        # Don't attempt to open if open dialog
        # was cancelled away.
        if mfile:
            self.lineEditMetaSource.setText(mfile)

    def actionRunCopy(self):
        """MainFunction for copy"""
        if self.lineEditCopySource.text() == "Quell-Ordner":
            errorMessage = u"Quell-Ordner wurde nicht ausgewaehlt.."
            self.showDialogCritical(errorMessage)
            return

        if self.lineEditCopyDest.text() == "Ziel-Ordner":
            errorMessage = u"Ziel-Ordner wurde nicht ausgewaehlt.."
            self.showDialogCritical(errorMessage)
            return

        self.showDebugMessage(self.lineEditCopySource.text())
        self.showDebugMessage(self.lineEditCopyDest.text())

        try:
            dirsSource = os.listdir(self.lineEditCopySource.text())
        except Exception, e:
            logMessage = u"read_files_from_dir Error: %s" % str(e)
            self.showDebugMessage(logMessage)

        self.showDebugMessage(dirsSource)
        self.textEdit.append("<b>Kopieren:</b>")
        z = 0
        zList = len(dirsSource)
        self.showDebugMessage(zList)
        dirsSource.sort()
        for item in dirsSource:
            if item[len(item)-4:len(item)] == ".MP3" or item[len(item)-4:len(item)] == ".mp3":
                fileToCopySource = self.lineEditCopySource.text() + "/" + item
                # pruefen ob file exists
                fileNotExist = None
                try:
                    with open(fileToCopySource) as f: pass
                except IOError as e:
                    self.showDebugMessage(u"File not exists")
                    fileNotExist = "yes"
                    # max Anzahl korrigieren und Progress aktualisieren
                    zList = zList - 1
                    pZ = z * 100 / zList
                    self.progressBarCopy.setValue(pZ)

                self.showDebugMessage(fileToCopySource)

                if fileNotExist is None:
                    # extention lowercase
                    filename = item[0:len(item) - 4] + ".mp3"
                    #fileToCopyDest = self.lineEditCopyDest.text() + "/" + item
                    fileToCopyDest = self.lineEditCopyDest.text() + "/" + filename
                    self.textEdit.append(fileToCopyDest)
                    self.showDebugMessage(fileToCopySource)
                    self.showDebugMessage(fileToCopyDest)

                    # Bitrate checken, eventuell aendern und gleich in Ziel neu encodieren
                    isChangedAndCopy = self.checkChangeBitrateAndCopy(fileToCopySource, fileToCopyDest)
                    # nicht geaendert also kopieren
                    if  isChangedAndCopy is None:
                        self.copyFile(fileToCopySource, fileToCopyDest)

                    self.checkCangeId3(fileToCopyDest)
                    z += 1
                    self.showDebugMessage(z)
                    self.showDebugMessage(zList)
                    pZ = z * 100 / zList
                    self.showDebugMessage(pZ)
                    self.progressBarCopy.setValue(pZ)
                else:
                    self.textEdit.append("<b>Uebersprungen</b>:")
                    self.textEdit.append(fileToCopySource)

        self.showDebugMessage(z)
        # CopyDestination is Source for Daisy
        self.lineEditDaisySource.setText(self.lineEditCopyDest.text())

    def copyFile(self, fileToCopySource, fileToCopyDest):
        """Copy File"""
        try:
            shutil.copy(fileToCopySource, fileToCopyDest)
        except Exception, e:
            logMessage = u"copy_file Error: %s" % str(e)
            self.showDebugMessage(logMessage)
            self.textEdit.append(logMessage + fileToCopyDest)

    def checkCangeId3(self, fileToCopyDest):
        """check id3 Tags, maybe delete it"""
        tag = None
        try:
            audio = ID3(fileToCopyDest)
            tag = "yes"
        except ID3NoHeaderError:
            self.showDebugMessage(u"No ID3 header found; skipping.")

        if tag is not None:
            if self.checkBoxCopyID3Change.isChecked():
                audio.delete()
                self.textEdit.append("<b>ID3 entfernt bei</b>: " + fileToCopyDest)
                self.showDebugMessage(u"ID3 entfernt bei " + fileToCopyDest)
            else:
                self.textEdit.append("<b>ID3 vorhanden, aber NICHT entfernt bei</b>: " + fileToCopyDest)

    def checkChangeBitrateAndCopy(self, fileToCopySource, fileToCopyDest):
        """check Bitrate, maybe change it """
        isChangedAndCopy = None
        audioSource = MP3(fileToCopySource)
        if audioSource.info.bitrate != int(self.comboBoxPrefBitrate.currentText())*1000:
            isEncoded = None
            self.textEdit.append(u"Bitrate Vorgabe: " + str(self.comboBoxPrefBitrate.currentText()))
            self.textEdit.append(u"<b>Bitrate folgender Datei entspricht nicht der Vorgabe:</b> " + str(audioSource.info.bitrate/1000) + " " + fileToCopySource)

            if self.checkBoxCopyBitrateChange.isChecked():
                self.textEdit.append(u"<b>Bitrate aendern bei</b>: " + fileToCopyDest)
                isEncoded = self.encodeFile( fileToCopySource, fileToCopyDest )
                if isEncoded is not None:
                    self.textEdit.append(u"<b>Bitrate geaendert bei</b>: " + fileToCopyDest)
                    isChangedAndCopy = True
            else:
                self.textEdit.append(u"<b>Bitrate wurde NICHT geaendern bei</b>: " + fileToCopyDest)
        return isChangedAndCopy

    def encodeFile(self, fileToCopySource, fileToCopyDest):
        """encode mp3-files """
        self.showDebugMessage(u"encode_file")
        #damit die uebergabe der befehle richtig klappt muessen alle cmds im richtigen zeichensatz als strings encoded sein
        c_lame_encoder = "/usr/bin/lame"
        self.showDebugMessage(u"type c_lame_encoder")
        self.showDebugMessage(type(c_lame_encoder))
        self.showDebugMessage(u"fileToCopySource")
        self.showDebugMessage(type(fileToCopySource))
        self.showDebugMessage(fileToCopyDest)
        self.showDebugMessage(u"type(fileToCopyDest)")
        self.showDebugMessage(type(fileToCopyDest))

        #p = subprocess.Popen([c_lame_encoder, "-b",  "64", "-m",  "m",  fileToCopySource, fileToCopyDest ],  stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(  )
        p = subprocess.Popen([c_lame_encoder, "-b", self.comboBoxPrefBitrate.currentText(), "-m", "m", fileToCopySource, fileToCopyDest ],  stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(  )

        self.showDebugMessage(u"returncode 0")
        self.showDebugMessage(p[0])
        self.showDebugMessage(u"returncode 1")
        self.showDebugMessage(p[1])

        # search for successMessage, if not found: -1
        n_encode_percent = string.find(p[1], "(100%)")
        n_encode_percent_1 = string.find(p[1], "(99%)")
        self.showDebugMessage(n_encode_percent)
        c_complete = "no"

        # with short files, no 100% message appear, now search for 99%
        if n_encode_percent == -1:
            # no 100%
            if n_encode_percent_1 != -1:
                # but 99%
                c_complete = "yes"
        else:
            c_complete = "yes"

        if c_complete == "yes":
            log_message = u"recoded_file: " + fileToCopySource
            self.showDebugMessage(log_message)
            return fileToCopyDest
        else:
            log_message = u"recode_file Error: " + fileToCopySource
            self.showDebugMessage(log_message)
            return None

    def metaLoadFile(self):
        """load file with meta-data"""
        fileExist = os.path.isfile(self.lineEditMetaSource.text())
        if fileExist is False:
            self.showDebugMessage("File not exists")
            self.textEdit.append(
                "<font color='red'>"
                + "Meta-Datei konnte nicht geladen werden</font>: "
                + os.path.basename(str(self.lineEditMetaSource.text())))
            return

        config = ConfigParser.RawConfigParser()

        # change path from QTString to String
        config.read(str(self.lineEditMetaSource.text()))
        self.lineEditMetaProducer.setText(config.get('Daisy_Meta', 'Produzent'))
        self.lineEditMetaAutor.setText(config.get('Daisy_Meta', 'Autor'))
        self.lineEditMetaTitle.setText(config.get('Daisy_Meta', 'Titel'))
        self.lineEditMetaEdition.setText(config.get('Daisy_Meta', 'Edition'))
        self.lineEditMetaNarrator.setText(config.get('Daisy_Meta', 'Sprecher'))
        self.lineEditMetaKeywords.setText(config.get('Daisy_Meta',
                        'Stichworte'))
        self.lineEditMetaRefOrig.setText(config.get('Daisy_Meta',
                        'ISBN/Ref-Nr.Original'))
        self.lineEditMetaPublisher.setText(config.get('Daisy_Meta', 'Verlag'))
        self.lineEditMetaYear.setText(config.get('Daisy_Meta', 'Jahr'))

    def actionRunDaisy(self):
        """write Daisy-Fileset"""
        if self.lineEditDaisySource.text() == "Quell-Ordner":
            errorMessage = u"Quell-Ordner wurde nicht ausgewaehlt.."
            self.showDialogCritical(errorMessage)
            return

        # read Audios
        try:
            dirItems = os.listdir(self.lineEditDaisySource.text())
        except Exception, e:
            logMessage = u"read_files_from_dir Error: %s" % str(e)
            self.showDebugMessage(logMessage)

        self.progressBarDaisy.setValue(10)
        self.showDebugMessage(dirItems)
        self.textEditDaisy.append(u"<b>Folgende Audios werden bearbeitet:</b>")
        zMp3 = 0
        zList = len(dirItems)
        self.showDebugMessage(zList)
        dirAudios = []
        dirItems.sort()
        for item in dirItems:
            if item[len(item)-4:len(item) ] == ".MP3" or item[len(item)-4:len(item)] == ".mp3":
                dirAudios.append(item)
                self.textEditDaisy.append(item)
                zMp3 += 1

        #totalAudioLength = self.calcAudioLengt(dirAudios)
        lTimes = self.calcAudioLengt(dirAudios)
        totalAudioLength = lTimes[0]
        lTotalElapsedTime = lTimes[1]
        lFileTime = lTimes[2]
        print totalAudioLength
        totalTime = timedelta(seconds = totalAudioLength)
        # umwandlung von timedelta in string: minuten und sekunden musten immer zweistllig sein,
        # damit einstellige stunde eine null bekommt :zfill(8)
        lTotalTime = str(totalTime).split(".")
        cTotalTime = lTotalTime[0].zfill(8)
        #str(cTotalTime[0]).zfill(8)
        self.textEditDaisy.append(u"Gesamtlaenge: " + cTotalTime)
        self.writeNCC(cTotalTime, zMp3, dirAudios)
        self.progressBarDaisy.setValue(20)
        self.writeMasterSmil(cTotalTime, dirAudios)
        self.progressBarDaisy.setValue(50)
        self.writeSmil(lTotalElapsedTime, lFileTime, dirAudios)
        self.progressBarDaisy.setValue(100)

    def calcAudioLengt(self, dirAudios):
        """calc duration of audiofiles"""
        totalAudioLength = 0
        lTotalElapsedTime = []
        lTotalElapsedTime.append(0)
        lFileTime = []
        for item in dirAudios:
            fileToCheck = os.path.join(
                str(self.lineEditDaisySource.text()), item)
            audioSource = MP3(fileToCheck)
            self.showDebugMessage(item + " " + str(audioSource.info.length))
            totalAudioLength += audioSource.info.length
            lTotalElapsedTime.append(totalAudioLength)
            lFileTime.append(audioSource.info.length)
            lTimes = []
            lTimes.append(totalAudioLength)
            lTimes.append(lTotalElapsedTime)
            lTimes.append(lFileTime)
        return lTimes

    def checkPackages(self, package):
        """
        check if package is installed
        needs subprocess, os
        http://stackoverflow.com/
        questions/11210104/check-if-a-program-exists-from-a-python-script
        """
        try:
            devnull = open(os.devnull, "w")
            subprocess.Popen([package], stdout=devnull,
                            stderr=devnull).communicate()
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                errorMessage = (u"Es fehlt das Paket:\n " + package
                                + u"\nZur Nutzung des vollen Funktionsumfanges "
                                + "muss es installiert werden!")
                self.showDialogCritical(errorMessage)
                self.textEdit.append(
                    "<font color='red'>Es fehlt das Paket: </font> " + package)

    def writeNCC(self, cTotalTime, zMp3, dirAudios):
        """write NCC-Page"""
        try:
            fOutFile = open(os.path.join(str(self.lineEditDaisySource.text()), "ncc.html"), 'w')
        except IOError as (errno, strerror):
            self.showDebugMessage("I/O error({0}): {1}".format(errno, strerror))
        else:
            self.textEditDaisy.append(u"<b>NCC-Datei schreiben...</b>")
            fOutFile.write('<?xml version="1.0" encoding="utf-8"?>' + '\r\n')
            fOutFile.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'+ '\r\n')
            fOutFile.write('<html xmlns="http://www.w3.org/1999/xhtml">' + '\r\n')
            fOutFile.write('<head>'+ '\r\n')
            fOutFile.write('<meta http-equiv="Content-type" content="text/html; charset=utf-8"/>'+ '\r\n')
            fOutFile.write('<title>' + self.lineEditMetaTitle.text() + '</title>' + '\r\n')

            fOutFile.write('<meta name="ncc:generator" content="KOM-IN-DaisyCreator"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:revision" content="1"/>' + '\r\n')
            today = datetime.date.today()
            fOutFile.write('<meta name="ncc:producedDate" content="' + today.strftime("%Y-%m-%d") + '"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:revisionDate" content="' + today.strftime("%Y-%m-%d") + '"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:tocItems" content="' + str( zMp3 ) + '"/>' + '\r\n')

            fOutFile.write('<meta name="ncc:totalTime" content="' + cTotalTime+ '"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:narrator" content="' + self.lineEditMetaNarrator.text() + '"/>'+ '\r\n')
            fOutFile.write('<meta name="ncc:pageNormal" content="0"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:pageFront" content="0"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:pageSpecial" content="0"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:sidebars" content="0"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:prodNotes" content="0"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:footnotes" content="0"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:depth" content="' + str(self.spinBoxEbenen.value()) + '"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:maxPageNormal" content="' +str(self.spinBoxPages.value()) +'"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:charset" content="utf-8"/>' + '\r\n')
            fOutFile.write('<meta name="ncc:multimediaType" content="audioNcc"/>' + '\r\n')
            #fOutFile.write( '<meta name="ncc:kByteSize" content=" "/>'+ '\r\n')
            fOutFile.write('<meta name="ncc:setInfo" content="1 of 1"/>' + '\r\n')

            fOutFile.write('<meta name="ncc:sourceDate" content="' + self.lineEditMetaYear.text()+ '"/>'+ '\r\n')
            fOutFile.write('<meta name="ncc:sourceEdition" content="' + self.lineEditMetaEdition.text() + '"/>'+ '\r\n')
            fOutFile.write('<meta name="ncc:sourcePublisher" content="' + self.lineEditMetaPublisher.text()+ '"/>'+ '\r\n')

            #Anzahl files = Records 2x + ncc.html + master.smil
            fOutFile.write('<meta name="ncc:files" content="' + str(zMp3 + zMp3 + 2) + '"/>'+ '\r\n')
            #fOutFile.write('<meta name="ncc:format" content="Daisy 2.0"/>'+ '\r\n')

            fOutFile.write('<meta name="ncc:producer" content="' + self.lineEditMetaProducer.text()+ '"/>'+ '\r\n')
            #fOutFile.write('<meta name="ncc:charset" content="ISO-8859-1"/>'+ '\r\n')

            fOutFile.write('<meta name="dc:creator" content="' + self.lineEditMetaAutor.text()+ '"/>'+ '\r\n')
            fOutFile.write('<meta name="dc:date" content="' + today.strftime("%Y-%m-%d")+ '"/>'+ '\r\n')
            fOutFile.write('<meta name="dc:format" content="Daisy 2.02"/>'+ '\r\n')
            fOutFile.write('<meta name="dc:identifier" content="' + self.lineEditMetaRefOrig.text()+ '"/>'+ '\r\n')
            fOutFile.write('<meta name="dc:language" content="de" scheme="ISO 639"/>'+ '\r\n')
            fOutFile.write('<meta name="dc:publisher" content="' + self.lineEditMetaPublisher.text()+ '"/>'+ '\r\n')

            fOutFile.write('<meta name="dc:source" content="' +self.lineEditMetaRefOrig.text()+ '"/>'+ '\r\n')
            #fOutFile.write('<meta name="dc:sourceDate" content="' + self.lineEditMetaYear.text()+ '"/>'+ '\r\n')
            #fOutFile.write('<meta name="dc:sourceEdition" content="' +self.lineEditMetaEdition.text()+ '"/>'+ '\r\n')
            #fOutFile.write('<meta name="dc:sourcePublisher" content="' + self.lineEditMetaPublisher.text()+ '"/>'+ '\r\n')
            fOutFile.write('<meta name="dc:subject" content="' + self.lineEditMetaKeywords.text()+ '"/>'+ '\r\n')
            fOutFile.write('<meta name="dc:title" content="' +self.lineEditMetaTitle.text()+ '"/>'+ '\r\n')
            # Medibus-OK items
            fOutFile.write('<meta name="prod:audioformat" content="wave 44 kHz"/>'+ '\r\n')
            fOutFile.write('<meta name="prod:compression" content="mp3 ' + self.comboBoxPrefBitrate.currentText()  + '/ kb/s"/>'+ '\r\n')
            fOutFile.write('<meta name="prod:localID" content=" "/>' + '\r\n')
            fOutFile.write('</head>' + '\r\n')
            fOutFile.write('<body>' + '\r\n')
            z = 0
            for item in dirAudios:
                z += 1
                if z == 1:
                    fOutFile.write('<h1 class="title" id="cnt_0001"><a href="0001.smil#txt_0001">' + self.lineEditMetaAutor.text()+ ": " + self.lineEditMetaTitle.text() + '</a></h1>'+ '\r\n')
                    continue
                # trennen
                itemSplit = self.splitFilename(item)
                cTitle = self.extractTitle(itemSplit)
                fOutFile.write('<h'+ itemSplit[1]+' id="cnt_'+str(z).zfill(4)+'"><a href="'+str(z).zfill(4)+'.smil#txt_'+str(z).zfill(4)+'">'+ cTitle + '</a></h'+itemSplit[1]+'>'+ '\r\n')

            fOutFile.write("</body>" + '\r\n')
            fOutFile.write("</html>" + '\r\n')
            fOutFile.close
        self.textEditDaisy.append(u"<b>NCC-Datei geschrieben</b>")

    def writeMasterSmil(self, cTotalTime, dirAudios):
        """write MasterSmil-Page"""
        try:
            fOutFile = open(os.path.join(str(self.lineEditDaisySource.text()), "master.smil")  , 'w')
        except IOError as (errno, strerror):
            self.showDebugMessage("I/O error({0}): {1}".format(errno, strerror))
        else:
            self.textEditDaisy.append(u"<b>MasterSmil-Datei schreiben...</b>")
            fOutFile.write('<?xml version="1.0" encoding="utf-8"?>'+ '\r\n' )
            fOutFile.write('<!DOCTYPE smil PUBLIC "-//W3C//DTD SMIL 1.0//EN" "http://www.w3.org/TR/REC-smil/SMIL10.dtd">'+'\r\n')
            fOutFile.write('<smil>' + '\r\n')
            fOutFile.write('<head>' + '\r\n')
            fOutFile.write('<meta name="dc:format" content="Daisy 2.02"/>'+'\r\n')
            fOutFile.write('<meta name="dc:identifier" content="'+ self.lineEditMetaRefOrig.text()+ '"/>'+'\r\n')
            fOutFile.write('<meta name="dc:title" content="' + self.lineEditMetaTitle.text() + '"/>'+'\r\n')
            fOutFile.write('<meta name="ncc:generator" content="KOM-IN-DaisyCreator"/>'+'\r\n')
            fOutFile.write('<meta name="ncc:format" content="Daisy 2.0"/>'+'\r\n')
            fOutFile.write('<meta name="ncc:timeInThisSmil" content="' + cTotalTime +  '" />'+'\r\n')

            fOutFile.write('<layout>' + '\r\n')
            fOutFile.write('<region id="txt-view" />' + '\r\n')
            fOutFile.write('</layout>' + '\r\n')
            fOutFile.write('</head>' + '\r\n')
            fOutFile.write('<body>' + '\r\n')

            #fOutFile.write( '<ref src="0001.smil" title="'+ self.lineEditMetaTitle.text() + '" id="smil_0001"/>'+'\r\n')
            z = 0
            for item in dirAudios:
                z += 1
                # trennen
                itemSplit = self.splitFilename(item)
                cTitle = self.extractTitle(itemSplit)
                fOutFile.write('<ref src="' + str(z).zfill(4) + '.smil" title="' + cTitle + '" id="smil_' + str(z).zfill(4) + '"/>'+'\r\n')

            fOutFile.write('</body>' + '\r\n')
            fOutFile.write('</smil>' + '\r\n')
            fOutFile.close
        self.textEditDaisy.append(u"<b>Master-smil-Datei geschrieben</b>")

    def writeSmil(self, lTotalElapsedTime, lFileTime, dirAudios):
        """write Smil-Pages"""
        self.textEditDaisy.append(u"<b>smil-Dateien schreiben...</b> ")
        z = 0
        for item in dirAudios:
            z += 1

            try:
                filename = str(z).zfill(4) + '.smil'
                fOutFile = open(os.path.join(str(self.lineEditDaisySource.text()), filename), 'w')
            except IOError as (errno, strerror):
                self.showDebugMessage("I/O error({0}): {1}".format(errno, strerror) )
            else:
                self.textEditDaisy.append(str(z).zfill(4) + u".smil - File schreiben")
                # trennen
                itemSplit = self.splitFilename(item)
                cTitle = self.extractTitle(itemSplit)

                fOutFile.write('<?xml version="1.0" encoding="utf-8"?>'+ '\r\n')
                fOutFile.write('<!DOCTYPE smil PUBLIC "-//W3C//DTD SMIL 1.0//EN" "http://www.w3.org/TR/REC-smil/SMIL10.dtd">'+'\r\n')
                fOutFile.write('<smil>' + '\r\n')
                fOutFile.write('<head>' + '\r\n')
                fOutFile.write('<meta name="ncc:generator" content="KOM-IN-DaisyCreator"/>' + '\r\n')
                #fOutFile.write('<meta name="ncc:format" content="Daisy 2.02"/>' + '\r\n')
                totalElapsedTime = timedelta(seconds = lTotalElapsedTime[z-1])
                splittedTtotalElapsedTime = str(totalElapsedTime).split(".")
                self.showDebugMessage(u"splittedTtotalElapsedTime: ")
                self.showDebugMessage(splittedTtotalElapsedTime)
                totalElapsedTimehhmmss = splittedTtotalElapsedTime[0].zfill(8)
                if z == 1:
                    # erster eintrag ergibt nur einen split
                    totalElapsedTimeMilliMicro = "000"
                else:
                    totalElapsedTimeMilliMicro = splittedTtotalElapsedTime[1][0:3]
                #fOutFile.write( '<meta name="ncc:totalElapsedTime" content="' + str(lTotalElapsedTime[z-1] )+ '"/>')
                #fOutFile.write( '<meta name="ncc:totalElapsedTime" content="' + str( totalElapsedTime )+ '"/>'+'\r\n')
                fOutFile.write('<meta name="ncc:totalElapsedTime" content="' +totalElapsedTimehhmmss + "." + totalElapsedTimeMilliMicro +'"/>'+'\r\n')

                fileTime = timedelta(seconds = lFileTime[z - 1])
                self.showDebugMessage(u"filetime: " + str(fileTime))
                splittedFileTime = str(fileTime).split(".")
                FileTimehhmmss = splittedFileTime[0].zfill(8)
                # wenn keine Millisicrosec gibts nur ein Element in der Liste
                if len(splittedFileTime) > 1:
                    if len(splittedFileTime[1]) >= 3:
                        fileTimeMilliMicro = splittedFileTime[1][0:3]
                    elif len(splittedFileTime[1]) == 2:
                        fileTimeMilliMicro = splittedFileTime[1][0:2]
                else:
                    fileTimeMilliMicro = "000"

                #fOutFile.write( '<meta name="ncc:timeInThisSmil" content="' + str(lFileTime[z-1]) + '" />'+'\r\n')

                fOutFile.write('<meta name="ncc:timeInThisSmil" content="' + FileTimehhmmss + "." + fileTimeMilliMicro +'" />'+'\r\n')
                fOutFile.write('<meta name="dc:format" content="Daisy 2.02"/>'+'\r\n')
                fOutFile.write('<meta name="dc:identifier" content="' + self.lineEditMetaRefOrig.text() + '"/>'+'\r\n')
                fOutFile.write('<meta name="dc:title" content="' +  cTitle  + '"/>'+'\r\n')
                fOutFile.write('<layout>' + '\r\n')
                fOutFile.write('<region id="txt-view"/>' + '\r\n')
                fOutFile.write('</layout>' + '\r\n')
                fOutFile.write('</head>' + '\r\n')
                fOutFile.write('<body>' + '\r\n')
                #fOutFile.write( '<seq dur="' + FileTimehhmmss + '.' + fileTimeMilliMicro + 's">'+'\r\n')
                lFileTimeSeconds = str(lFileTime[z-1]).split(".")

                fOutFile.write('<seq dur="' + lFileTimeSeconds[0] + '.' + fileTimeMilliMicro  +'s">'+'\r\n')
                fOutFile.write('<par endsync="last">'+'\r\n')
                fOutFile.write('<text src="ncc.html#cnt_' + str(z).zfill(4) + '" id="txt_' + str(z).zfill(4) + '" />'+'\r\n')
                fOutFile.write('<seq>' + '\r\n')
                if fileTime < timedelta(seconds=45):
                    fOutFile.write('<audio src="' + item + '" clip-begin="npt=0.000s" clip-end="npt=' + lFileTimeSeconds[0] + '.' + fileTimeMilliMicro + 's" id="a_' + str(z).zfill(4)  + '" />'+'\r\n')
                else:
                    fOutFile.write('<audio src="' + item + '" clip-begin="npt=0.000s" clip-end="npt=' + str(15) + '.' + fileTimeMilliMicro + 's" id="a_' + str(z).zfill(4)  + '" />'+'\r\n')
                    zz = z + 1
                    phraseSeconds = 15
                    while phraseSeconds <= lFileTime[z - 1] - 15:
                        fOutFile.write('<audio src="' + item + '" clip-begin="npt='+ str(phraseSeconds)+ '.' + fileTimeMilliMicro + 's" clip-end="npt=' + str(phraseSeconds+15) + '.' + fileTimeMilliMicro + 's" id="a_' + str(zz).zfill(4)  + '" />'+'\r\n')
                        phraseSeconds += 15
                        zz += 1
                    fOutFile.write('<audio src="' + item + '" clip-begin="npt='+ str(phraseSeconds)+ '.' + fileTimeMilliMicro + 's" clip-end="npt=' + lFileTimeSeconds[0] + '.' + fileTimeMilliMicro + 's" id="a_' + str(zz).zfill(4)  + '" />'+'\r\n')

                fOutFile.write('</seq>' + '\r\n')
                fOutFile.write('</par>' + '\r\n')
                fOutFile.write('</seq>' + '\r\n')

                fOutFile.write('</body>' + '\r\n')
                fOutFile.write('</smil>' + '\r\n')
                fOutFile.close
        self.textEditDaisy.append(u"<b>smil-Dateien geschrieben:</b> " + str(z))

    def splitFilename(self, item):
        """split filename into list """
        if self.comboBoxDaisyTrenner.currentText() == "2. Unterstrich":
            itemSplit = item.split("_", 2)
        self.showDebugMessage(itemSplit)
        self.showDebugMessage(len(itemSplit))
        return itemSplit

    def extractTitle(self, itemSplit):
        # letzter teil
        itemLeft = itemSplit[len(itemSplit) - 1]
        # davon file-ext abtrennen
        itemTitle = itemLeft.split(".mp3")
        cTitle = re.sub("_", " ", itemTitle[0])
        return cTitle

    def showDialogCritical(self, errorMessage):
        QtGui.QMessageBox.critical(self, "Achtung", errorMessage)

    def showDebugMessage(self, debugMessage):
        if self.app_debugMod == "yes":
            print debugMessage

    def actionQuit(self):
        QtGui.qApp.quit()

    def main(self):
        """mainFunction"""
        self.showDebugMessage(u"let's rock")
        self.readConfig()
        self.checkPackages(self.app_lame)
        # set msic parameters
        self.progressBarCopy.setValue(0)
        self.progressBarDaisy.setValue(0)
        # Trenner in Combo
        self.comboBoxDaisyTrenner.addItem("2. Unterstrich")
        # Bitrate
        self.comboBoxPrefBitrate.addItem("64")
        self.comboBoxPrefBitrate.addItem("96")
        self.comboBoxPrefBitrate.addItem("128")
        # defaultValue of Checkboxes
        self.checkBoxCopyID3Change.setChecked(True)
        self.checkBoxCopyBitrateChange.setChecked(True)
        # defaultValue of Spinboxes
        self.spinBoxEbenen.setValue(1)
        self.spinBoxPages.setValue(0)
        # Help-Text
        self.readHelp()
        self.show()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dyc = DaisyCopy()
    dyc.main()
    app.exec_()
    # This shows the interface we just created. No logic has been added, yet.
