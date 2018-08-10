import xml.etree.ElementTree as et
from xml.etree.ElementTree import parse
from xml.etree.ElementTree import Element
import sys

elanFile = sys.argv[1]

tree = parse(elanFile) #opening the file

listOfSubElem = list(tree.getroot()) #putting the tree's elements into a list
    #HEADER, 'TIME_ORDER', 'TIER', 'TIER', 'TIER', 'LINGUISTIC_TYPE', 'LINGUISTIC_TYPE', 'CONSTRAINT', 'CONSTRAINT', 'CONSTRAINT', 'CONSTRAINT'
        #The order of the elements

time_order = list(listOfSubElem[1])
#print(len(time_order)) #------- 288 lines

numberOfAnno_MyTier = len(list(listOfSubElem[3]))
#print(numberOfAnno_MyTier) #--------- 15 lines

numberOfAnno_NewFilesTier = len(list(listOfSubElem[4]))
#print(numberOfAnno_NewFilesTier) #------- 129 lines


#retrieving ts values
ts = []
for x in range(len(time_order)): #the ts values are ordered ascending in the sublime text file, they are not distinguished by tier
    ts.append(time_order[x].attrib["TIME_VALUE"]) #appending all the millisecond values into the ts array

#retrieving the annotation values
a_MyTier = list(listOfSubElem[3].getchildren()) #list of annotations from the first tier
text_MyTier = [] #list to store text values from MyTier
for x in range(numberOfAnno_MyTier):
    alignableAnnotation = a_MyTier[x].getchildren() # x is the annotation of the list
    text_MyTier.append(str(alignableAnnotation[0].getchildren()[0].text)) # [0] is the default index to get the text value

a_NewFilesTier = list(listOfSubElem[4].getchildren())
text_NewFilesTier = []
for x in range(numberOfAnno_NewFilesTier):
    alignableAnnotation = a_NewFilesTier[x].getchildren()
    text_NewFilesTier.append(str(alignableAnnotation[0].getchildren()[0].text))

#VARIABLES: a_MyTier & a_NewFilesTier = the list of annotation subelements
#           text_MyTier & text_NewFilesTier = the ANNOTATION_VALUE raw text



#function to find ts value
def tsValueFinder(index, a_Tier, reference):    #index = annotation number,  a_Tier = a_MyTier or a_NewFilesTier,  reference = TIME_SLOT_REF1 or TIME_SLOT_REF2
                            #This function is to find the millisecond time value of that particular annotation
    alignableAnnotation = a_Tier[index].getchildren()
    tsString = alignableAnnotation[0].attrib[reference] #finding out which TIME_SLOT_ID is used for the TIME_SLOT_REF in that annotation

    indexOf_timeOrderList = 0
    for x in range(len(time_order)):
        this_tsString = time_order[x].attrib["TIME_SLOT_ID"] #the current ts variable at the index

        if(this_tsString == tsString): #if the loop has reached the variale we are looking for
            indexOf_timeOrderList = x #remember this index and use it to find the millisecond time value through the ts[] list created earlier
            break

    time_value = [ts[indexOf_timeOrderList], tsString]
    return time_value #time_value is a list with two items: the time stamp and the ts number


#creation of new tier
comparisonTier = et.SubElement(tree.getroot(), "TIER", ANNOTATOR="Celina", LINGUISTIC_TYPE_REF="English", PARTICIPANT="The Person", TIER_ID="Comparison Tier")

def createAnnotation(trueOrFalse, annotationNumber, ts1, ts2): #function that adds a new annotation. Takes in whether the section should be labled as true or false
                                                                #ts1 and ts2 are millisecon time values and give the duration/interval of the annotation
    annotation = et.SubElement(comparisonTier, "ANNOTATION")
    alignableAnnotation = et.SubElement(annotation, "ALIGNABLE_ANNOTATION", ANNOTATION_ID="a"+str(annotationNumber), TIME_SLOT_REF1=ts1, TIME_SLOT_REF2=ts2)

    annotation_value = et.SubElement(alignableAnnotation, "ANNOTATION_VALUE")
    annotation_value.text = str(trueOrFalse)


annotationNumber = numberOfAnno_MyTier + numberOfAnno_NewFilesTier #this is the ANNOTATION_ID that the True/False tier will start on

#Comparing the newfile's tier to myTier
annoIndex_NewFilesTier = 0 #starting at the first annotation of each tier
annoIndex_MyTier = 0
trueOrFalse = False
timeCounter = 0

while(timeCounter < 10): #while the true/false annotation hasn't reached the last time value
    ts1_Value_NF = tsValueFinder(annoIndex_NewFilesTier, a_NewFilesTier, "TIME_SLOT_REF1") #obtaining the time value and time slot ID for the start of the interval of the NewFile annotation
    ts2_Value_NF = tsValueFinder(annoIndex_NewFilesTier, a_NewFilesTier, "TIME_SLOT_REF2") #obtaining the end of the interval for NewFile

    ts1_Value_My = tsValueFinder(annoIndex_MyTier, a_MyTier, "TIME_SLOT_REF1")
    ts2_Value_My = tsValueFinder(annoIndex_MyTier, a_MyTier, "TIME_SLOT_REF2")

    
    if(int(ts1_Value_NF[0]) >= int(ts1_Value_My[0]) and int(ts1_Value_NF[0]) < int(ts2_Value_My[0])): #if ts1_Value_NF/the-starting-time-of-the-annotation
                                                                                                        #for the NewFile is within the MyTier annotation interval

        if(int(ts2_Value_NF[0]) <= int(ts2_Value_My[0])): #If the NF annotation ends somewhere within the MyTier annotation, then the NF interval/annotation is completely in the MyTier interval/annotation
            if(text_NewFilesTier[annoIndex_NewFilesTier] == text_MyTier[annoIndex_MyTier]): #comparing the texts: Moving vs Not Moving
                trueOrFalse = True                                                              #determing whether it's true or false
            else:
                trueOrFalse = False

            createAnnotation(trueOrFalse, annotationNumber, ts1_Value_NF[1], ts2_Value_NF[1]) #create the annotation using the NewFile's time intervals
            annotationNumber += 1 #adding annotationNumber for every time ANNOTATION_ID is created

        else: #NF ending interval is longer than the MyTier interval
            if(text_NewFilesTier[annoIndex_NewFilesTier] == text_MyTier[annoIndex_MyTier]):
                trueOrFalse = True
            else:
                trueOrFalse = False
                
            createAnnotation(trueOrFalse, annotationNumber, ts1_Value_NF[1], ts2_Value_My[1]) #from the starting ts of the new file up till the ending ts of MyTier (where the true/false value ends)
            annotationNumber += 1

            ts2checkNext_MyTier = tsValueFinder(annoIndex_MyTier + 1, a_MyTier, "TIME_SLOT_REF2") #check to see if the next MyTier annotation is still shorter than the NewFile annotation

            if(int(ts2checkNext_MyTier[0]) < int(ts2_Value_NF[0])): #if the end of the MyTier interval is shorter than the NewFile interval
                annoIndex_MyTier += 1 #looking at this index now

                while(int(ts2checkNext_MyTier[0]) < int(ts2_Value_NF[0])): #while the next MyTier annotations are within the NewFile annotation
                    trueOrFalse = not trueOrFalse #using the "not" syntax to flip the previous value since it can be either true or false and we're not sure what it is
                    
                    createAnnotation(trueOrFalse, annotationNumber, ts2_Value_My[1], ts2checkNext_MyTier[1]) #new annotation from the end of the last ts2 value in MyTier to the new ts2 value
                    annotationNumber += 1

                    ts2_Value_My = ts2checkNext_MyTier #set checkNext as the current ts2 value

                    ts2checkNext_MyTier = tsValueFinder(annoIndex_MyTier + 1, a_MyTier, "TIME_SLOT_REF2") #check if the next MyTier interval is still shorter than NF

                    if(int(ts2checkNext_MyTier[0]) < int(ts2_Value_NF[0])): #if it is, add one to the index and repeat the loop
                        annoIndex_MyTier += 1

                    else: #otherwise, end this loop and wrap up the interval
                        createAnnotation(not trueOrFalse, annotationNumber, ts2_Value_My[1], ts2_Value_NF[1])
                        annotationNumber += 1
                        break
                
            else: #otherwise, if the end of the NEXT MyTier annotation is longer than the NewFile annotation -- wrap it up
                createAnnotation(not trueOrFalse, annotationNumber, ts2_Value_My[1], ts2_Value_NF[1])
                annotationNumber += 1
                endTime = ts2_Value_NF[0]

    else: #the NewFile annotation is ahead of the MyTier annotation, so we need to look at the next MyTier annotation
        annoIndex_MyTier += 1 #increase the index so we're looking at the next ANNOTATION_ID
        annoIndex_NewFilesTier -= 1 #to act as a "buffer" because the main for loop increases the annotationIndex for the NewFile at the end of the loop,
                                            #and we don't want it to jump ahead
    annoIndex_NewFilesTier += 1
    timeCounter += 1

#wrap tree
tree = et.ElementTree(tree.getroot()); # create element tree
tree.write(sys.argv[2], encoding='UTF-8', xml_declaration=True); # encoding and xml declaration =true add the necessary <?xml version="1.0" encoding="UTF-8"?>
