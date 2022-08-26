daisy-creator-book
==================

Moved to Codeberg!

Create digital talking books for blind people in the daisy 2.02 standard


Basics
------
The workflow is as follows:
- Record your book with a digital recorder or pc
- Edit your files and save one per capitel in this syntax: Number_Level_Title.mp3 (see filename-example)
- Mount the recordet media-card to your PC
- Now start the daisy-creator-book-application to create the daisy-fileset

If finished, you will find in the destinationfolder your audiofiles
and the daisy-structure for your daisy-player. 

General work steps
------------------
1. Choose the folder of your edited audiofiles as "Source-Folder"
2. Choose the folder for your dtb as "Destination-Folder"
3. Select the options if necessary (see options-section)
4. Run "Copy"
5. Select tab two
6. Control and edit your metadata if necessary
7. Select tab three
8. Edit options if necessary 
9. Run "Daisy"
Done! 


Options-Section on tab one
--------------------------
Here, you can select:
1. Change bitrate
This check the bitrate of each audiofile and changes it to the choosen rate on the "Preferences-Tab"
2. Delete ID3-Tags
3. Bitrate of mp3 audio files
Some Audioeditors write ID3-Version 2 Tags. This will not correspond to dtb 2.02


filename-example
-----------
1001_1_Title_of_the_book.mp3
1002_2_About_this_book.mp3
1003_1_Capitel_one.mp3


Remark
------
The daisy_creator_book is written by Joerg Sorge for KOM-IN-Netzwerk e.V. www.kom-in.de


