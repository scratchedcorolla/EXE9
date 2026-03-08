# **EXE9 OFFICIAL GITHUB REPOSITORY**

**Source Code, Info, and General Recourses regarding the EXE9 Universal Compiler.**
> This README.md was last updated on: 3/7/2026 - when the latest released version of EXE9 was v1.0.0


### **Table Of Contents**

---

* ##### About/What is it?
* ##### Regular Usage
* ##### Source Code Editing
* ##### File Structure
* ##### Legal
* ##### Notes (<-- READ THIS - DO NOT IGNORE)





### **About**

##### ==================

###### **EXE9 is a Universal Compiler that can be used to turn your project's messy, clunky source code into a clean, distributable, easy-to-use executable file.**

**In any regular case, to bring your project to life, it takes time, terminal-work, and experience in app-making. But with EXE9, just drag-and-drop your script, upload any media or data files your code requires, add an icon, and with just the press of a button, in less than a minute you will have a fast, distributable, independent executable file.**



**Currently, only support for Python code to .exe files is possible, but support for more languages and operating systems will be coming *very* soon.**



**EXE9 uses PyInstaller to compile Python scripts. Support and contribute to PyInstaller** [**here!**](https://pyinstaller.org/)



**EXE9 is open-source and written 100% in Python. Feel free to download the source code and edit however you like!**



##### **----------Learn More \& Download EXE9 on our website:** [**exe9.org**](https://exe9.org/)**----------**



**Developed By:**	Milo Pesqueira

**With A Special Thanks to:**		David Cortesi, Giovanni Bajo, and William Caban 

for creating & developing PyInstaller, the heart of EXE9.





### **Regular Usage**

##### ==================

###### **To use EXE9 for compiling scripts follow these steps**:

1. Upload your script to EXE9 by:

2\. Upload an icon file (.ico) to use as the icon of your executable file

3\. Upload a data folder (media or other files that your script depends on, such as the image file for a logo)

 	Use these techniques when uploading a file:

 	 a) Drag-and-Drop your file into the Drop Zone (currently only available for uploading the main script)

 	 b) Click "Browse" and select your script file in the file explorer window

4\. Press the "Generate EXE9" button to start the compilation process. This should take under a minute.

5\. When it shows that the compilation was successful in the terminal, you can find the executable in the "dist" folder inside the same folder your original script was.

NOTE: Press the "Clear" button next to each file upload zone to clear it. Now the zone is open to uploading a file again.



### **Source Code Editing**

##### ==================

###### **EXE9 is an open-source program, editing the script for *PERSONAL* use is 100% allowed.**

All of the app's main scripture is in one file, called EXE9.py, and all of the scripts are written entirely in Python.

Feel free to edit whatever and use whatever method of editing you choose! The possibilities are endless!

Near the top of the main script, there is a config section. This section works by assigning variables to different properties of different elements, this way, it only takes less than 30 seconds and only a few clicks to change
whatever styling you want! For instance, to change the background color to red, you would find the variable in the config menu for the background color, (which, in the main script, is "BG\_COLOR") and you would change the value
from the default "#001130", (which is a dark navy blue) to "#FF0000" (which is pure red).



### **File Structure**

##### ==================

**This is the basic file structure of the source code of EXE9. Please note that, as of 3/8/2026 (Latest Release v1.1.0), You can find the .exe, .app, and Linux binary of EXE9 in the releases on GitHub or on [our website's download page](https://exe9.org/download/). .zip and .tar.gz versions of each release are availible in the releases on GitHub.**



**The Main Parent Folder: "EXE9" holds these three folders:**



**".github", "build", "misc"**



**".github" contains the folder: "workflows". No files natively live in the ".github" folder. the "workflows" folder contains "build.yaml". The script used for building, compiling, and pushing releases.**



**misc contains *any* images, icons, or any other random media that relates to EXE9**



**"build" contains a copy of the latest release's source code, along with any files needed for EXE9 to run independently, such as logos and icons.**

### 

### **Legal**

##### ==================



© 2026 Milo Pesqueira

Developed and Designed by Milo Pesqueira ([milolp.dev](https://milolp.dev/))



All rights reserved. Redistribution or rehosting of EXE9 or it's binaries without permission is prohibited.

To request permission to distribute EXE9, with it's source code edited or unedited, contact Milo Pesqueira at the Email address: **inquires@exe9.org**

If permission is granted to distribute, distribution must follow all terms and guidelines proclaimed and agreed on by both parties during negotiation.

Under the Copyright Act of 1976, it is illegal to reproduce, distribute, or make derivatives of original code without direct permission from the creator.

This includes circumstances when the original source code is changed, edited, or revised by another party.

### 

### **Notes**

##### ==================



-EXE9 can take up to 30 seconds from pressing open to the program actually starting. This is due to the fact that it needs to start all the libraries and compiling scripts in the background. DO NOT SPAM OPEN - THIS WILL CAUSE EXE9 TO OPEN COPIES OF ITSELF AND COULD CAUSE CRASHING OR SYSTEM DAMAGE

-Due to a lack of code signing certificate, as of the last README update, sometimes your operating system will show a warning when you try to run, or your browser may block the download. Downloading the .zip version of EXE9 from the GitHub (/dist/EXE9 vX.X.X folder) can be very effective at mitigating browser blockage.








