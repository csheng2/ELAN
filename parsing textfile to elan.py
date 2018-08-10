#count how many lines are in the file
import sys
lineCounter = 0
fileName = sys.argv[1]
readingFile = open(fileName, "rt")
  
while(readingFile.readline()):
    lineCounter += 1

lineCounter -= 1 #subtract the top line of the file as it is irrelevant

readingFile.close()

#checking the action column
readingFile = open(fileName, "rt")
readingFile.readline() #skipping the top line
action = [] #array of actions: moving or not moving

for x in range(lineCounter):
    theLine = list(readingFile.readline().split(" "))
    if str(theLine[0]) == "Not":
        action.insert(x, "Not Moving")
    else:
        action.insert(x, theLine[0])

readingFile.close()

#checking the first time slot column
readingFile = open(fileName, "rt")
readingFile.readline()
timeSlot1 = []

for x in range(lineCounter):
    theLine = list(readingFile.readline().split(" "))
    if str(theLine[0]) == "Not":
        changeToInt = float(theLine[3]) * 1000
        changeToInt = int(changeToInt)
        timeSlot1.insert(x, changeToInt)
    else:
        changeToInt = float(theLine[2]) * 1000
        changeToInt = int(changeToInt)
        timeSlot1.insert(x, changeToInt)

readingFile.close()

#checking the second time slot column
readingFile = open(fileName, "rt")
readingFile.readline()
timeSlot2 = []

for x in range(lineCounter):
    theLine = list(readingFile.readline().split(" "))
    if str(theLine[0]) == "Not":
        changeToInt = float(theLine[4]) * 1000
        changeToInt = int(changeToInt)
        timeSlot2.insert(x, changeToInt)
    else:
        changeToInt = float(theLine[3]) * 1000
        changeToInt = int(changeToInt)
        timeSlot2.insert(x, changeToInt)

readingFile.close()

#Comparing actions and merging them
timeSlot1NEW = []
timeSlot2NEW = []
actionNEW = []
lineCounterNEW = 1

actionNEW.append(action[0])
timeSlot1NEW.append(timeSlot1[0])

for x in range (lineCounter - 1):
    if(action[x] != action [x+1]):
        timeSlot2NEW.append(timeSlot2[x])
        timeSlot1NEW.append(timeSlot2[x])
        lineCounterNEW += 1
        actionNEW.append(action[x+1])

timeSlot2NEW.append(timeSlot2[lineCounter-1])


#Starting to write codes to convert data to an eaf file
import xml.etree.ElementTree as et

#CREATING ROOT
root = et.Element("ANNOTATION_DOCUMENT", AUTHOR="", DATE="2018-07-05T14:15:03-07:00", FORMAT="3.0", VERSION="3.0");
attribute = "xmlns:xsi"; # python doesn't allow : in arguments, so had to define it manually
root.set(attribute, "http://www.w3.org/2001/XMLSchema-instance"); # sets a new attribute to the root tag
attribute = "xsi:noNamespaceSchemaLocation";
root.set(attribute, "http://www.mpi.nl/tools/elan/EAFv3.0.xsd");

#ADDING SUB ELEMENTS

header = et.SubElement(root, "HEADER", MEDIA_FILE="", TIME_UNITS="milliseconds")

media_descriptor = et.SubElement(header, "MEDIA_DESCRIPTOR", MEDIA_URL="file:///C:/Users/celina/Desktop/videos/a244.mp4", MIME_TYPE="video/mp4", RELATIVE_MEDIA_URL="./a244.mp4")
propertySub = et.SubElement(header, "PROPERTY", NAME="URN")
attribute = "urn:nl-mpi-tools-elan-eaf:bbf24d30-835b-46f7-b69e-b5038c7684f7"
propertySub = et.SubElement(header, "PROPERTY", NAME="lastUsedAnnotationId")

time_order = et.SubElement(root, "TIME_ORDER")

integer = 1
for x in range(lineCounterNEW):
    tsString = "ts" + str(integer)

    time_slot = et.SubElement(time_order, "TIME_SLOT", TIME_SLOT_ID=str(tsString), TIME_VALUE=str(timeSlot1NEW[x]))
    integer += 1

    tsString = "ts" + str(integer)

    time_slot = et.SubElement(time_order, "TIME_SLOT", TIME_SLOT_ID=str(tsString), TIME_VALUE=str(timeSlot2NEW[x]))
    integer += 1
    

tier = et.SubElement(root, "TIER", LINGUISTIC_TYPE_REF="default-lt", TIER_ID="default")
tier = et.SubElement(root, "TIER", ANNOTATOR="Celina", LINGUISTIC_TYPE_REF="English", PARTICIPANT="The Person", TIER_ID="action")


#Annotations
annotation = et.SubElement(tier, "ANNOTATION")

tsInteger = 1
aInteger = 1
for x in range(lineCounterNEW):
    aString = "a" + str(aInteger)
    FIRSTtsString = "ts" + str(tsInteger)
    tsInteger += 1
    SECONDtsString = "ts" + str(tsInteger)
    
    alignable_annotation = et.SubElement(annotation, "ALIGNABLE_ANNOTATION", ANNOTATION_ID=str(aString), TIME_SLOT_REF1=str(FIRSTtsString), TIME_SLOT_REF2=str(SECONDtsString))
    annotation_value = et.SubElement(alignable_annotation, "ANNOTATION_VALUE")

    annotation_value.text = str(actionNEW[x])

#    if(x % 2 == 0):
#        annotation_value.text = "Not Moving"
#    else:
#        annotation_value.text = "Moving"

    aInteger += 1
    tsInteger += 1

linguistic_type = et.SubElement(root, "LINGUISTIC_TYPE", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="default-lt", TIME_ALIGHNABLE="true")
linguistic_type = et.SubElement(root, "LINGUISTIC_TYPE", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="English", TIME_ALIGHNABLE="true")

constraint = et.SubElement(root, "CONSTRAINT", DESCRIPTION="Time subdivision of parent annotation's time interval, no time gaps allowed within this interval", STEREOTYPE="Time_Subdivision")
constraint = et.SubElement(root, "CONSTRAINT", DESCRIPTION="Symbolic subdivision of a parent annotation. Annotations refering to the same parent are ordered", STEREOTYPE="Symbolic_Subdivision")
constraint = et.SubElement(root, "CONSTRAINT", DESCRIPTION="1-1 association with a parent annotation", STEREOTYPE="Symbolic_Association")
constraint = et.SubElement(root, "CONSTRAINT", DESCRIPTION="Time alignable annotations within the parent annotation's time interval, gaps are allowed", STEREOTYPE="Included_In")
                     
#wrap tree
tree = et.ElementTree(root); # create element tree
tree.write(sys.argv[2], encoding='UTF-8', xml_declaration=True); # encoding and xml declaration =true add the necessary <?xml version="1.0" encoding="UTF-8"?>
