#!/usr/bin/env python
#
# Parse an XBRL file and store the interesting data to data structures.
#
import pprint
import psycopg2
import sys
from datetime import datetime
import xml.etree.ElementTree as ET

gVerbose = False


class DateContext:
    def __init__(self, periodStart, periodEnd):
        self.periodStart = periodStart
        self.periodEnd = periodEnd


class Form10Data:
    """This class holds the parsed data from a form 10 filing."""
    FilingData = {}

    def __init__(self, periodStart, periodEnd, CIK):
        self.periodStart = periodStart
        self.periodEnd = periodEnd
        self.CIK = CIK

    def setData(data):
        self.FilingData = data


def verbose(text):
    if gVerbose:
        print(text)


def extractNamespace(key, namespaceDict):
    nsValue = namespaceDict[key]

    if nsValue == None:
        print("Missing US GAAP namespace from : "+usGAAPns)

    return nsValue


toDateStr = lambda d : d.strftime("%Y-%m-%d")

def parseFiling(inputFilename):
    CIK = 0
    contextID = None

    # ContextDataDict should have keys of type context ID and values that are themselves
    # dictionaries with keys matching GAAP XBLR terms and values of type string containing
    # the value for the GAAP term
    ContextDataDict = {}

    # DateContextDict should have keys of type context ID and values of type DateContext
    DateContextDict = {}

    # DEIDict should have keys of type string that are the tag names and values of type string that are the text of the tag.
    DEIDict = {}

    # The end date is the DEI namespace end date. Use this to filter for current period data
    EndDate = None

    events = "start", "start-ns", "end", "end-ns"
    XBRLroot = None

    # namespaceDict should have keys of type string that are namespace names and values
    # of type string that are the URI's for the corresponding name
    namespaceDict = {}

    usGAAPns = None
    DEIns = None

    for event, elem in ET.iterparse(inputFilename, events):
        if event == "start-ns":
            if elem[0] in namespaceDict and namespaceDict[elem[0]] != elem[1]:
                # NOTE: It is perfectly valid to have the same prefix refer
                #     to different URI namespaces in different parts of the
                #     document. This exception serves as a reminder that this
                #     solution is not robust.    Use at your own peril.
                # raise KeyError("Duplicate prefix with different URI found.")
                print("Found definition for " + elem[0] + " when it's already defined as " + namespaceDict[elem[0]])

            if len(elem[0]) > 0:
                namespaceDict[elem[0]] = elem[1]
        elif event == "end-ns":
            verbose("Got end-ns element "+str(elem))
            pass
        elif event == "start":
            tag = elem.tag

            if XBRLroot is None:
                XBRLroot = elem

                pp = pprint.PrettyPrinter(indent = 4)
                print("Got XBRLroot "+str(XBRLroot)+"\nNamespaces:")
                pp.pprint(namespaceDict)

                # Generally Accepted Accounting Practices
                usGAAPns = extractNamespace('us-gaap', namespaceDict)

                # Document and Entity Information
                DEIns = extractNamespace('dei', namespaceDict)

            if "context" in tag:
                contextID = elem.get('id')
                verbose("Found context start "+tag+" id "+contextID)

        elif event == "end":
            tag = elem.tag

            if not usGAAPns:
                verbose("Pre-namespace tag is "+tag)
            if usGAAPns in tag:
                GAAPterm = tag.replace('{'+usGAAPns+'}', '', 1)
                GAAPtext = elem.text
                if GAAPtext != None:
                    if len(GAAPtext) > 100:
                       GAAPtext = GAAPtext[0:100] + "..."
                    GAAPContextRef = elem.attrib.get('contextRef')
                    dataDict = None
                    if GAAPContextRef in ContextDataDict:
                        dataDict = ContextDataDict[GAAPContextRef]
                    else:
                        dataDict = {}
                        ContextDataDict[GAAPContextRef] = dataDict
                    verbose("GAAP term " + GAAPterm + " " + GAAPtext)
                    dataDict[GAAPterm] = GAAPtext
                else:
                    verbose(GAAPterm + " has no text")
            elif DEIns in tag:
                DEIterm = tag.replace('{'+DEIns+'}', '', 1)
                DEItext = elem.text
                if DEItext != None:
                    DEIDict[DEIterm] = DEItext
                    if DEIterm == "EntityCentralIndexKey":
                        CIK = int(DEItext)
                        print("Found central index key " + DEItext + " converted to int " + str(CIK))
                    elif DEIterm == "DocumentPeriodEndDate":
                        EndDate = datetime.strptime(DEItext, "%Y-%m-%d")
                        print("Found document period end date " + toDateStr(EndDate))
                    else:
                        if len(DEItext) > 100:
                            DEItext = DEItext[0:100] + "...\n"
                        verbose("DEI term " + DEIterm + " " + DEItext)
                else:
                    print(DEIterm + " has no text")
            elif "context" in tag:
                verbose("Found context end "+tag)
                isValidPeriod = False
                startDate = None
                endDate = None

                contextIter = elem.iter()
                verbose("    Iterating over context elements")
                for contextElement in contextIter:
                    verbose("\tFound context element " + str(contextElement))
                    if "period" in contextElement.tag:
                        verbose("    Iterating over period elements")
                        periodIter = contextElement.iter()
                        for periodElement in periodIter:
                            verbose("\tFound period element " + str(periodElement))
                            if "startDate" in periodElement.tag:
                                startDateString = periodElement.text
                                startDate = datetime.strptime(startDateString, "%Y-%m-%d")
                                verbose("\tFound start date string " + startDateString + " converted to time.struct_time")
                            elif "endDate" in periodElement.tag:
                                endDateString = periodElement.text
                                endDate = datetime.strptime(endDateString, "%Y-%m-%d")
                                verbose("\tFound end date string " + endDateString + " converted to time.struct_time")
                                if startDate:
                                    isValidPeriod = True
                    if "entity" in contextElement.tag:
                        verbose("    Iterating over entity elements")
                        identityIter = contextElement.iter()
                        for identityElement in identityIter:
                            verbose("\tFound identity element " + str(identityElement))
                            if "identifier" in identityElement.tag:
                                contextCIK = int(identityElement.text)
                                verbose("\tFound CIK " + str(contextCIK))

                if contextCIK == CIK and isValidPeriod:
                    verbose("Adding context for period " + toDateStr(startDate) + " to " + toDateStr(endDate))
                    c = DateContext(startDate, endDate)
                    # Add an entry for this context ID and time period
                    DateContextDict[contextID] = c
                else:
                    verbose("Skipping totes bogus context")
                contextID = None
            else:
                OtherTerm = tag
                OtherText = elem.text or ""
                OtherText = OtherText.strip()
                """if len(OtherText) > 0:
                    if len(OtherText) > 100:
                       OtherText = OtherText[0:100] + "..."
                    verbose("Other term " + OtherTerm + " text '" + OtherText + "'")
                else:
                    print(OtherTerm + " has no text")
                    pass"""

    pp = pprint.PrettyPrinter(indent = 2)
    print("DEI dictionary has:")
    pp.pprint(DEIDict)
    print("Context dict of data dicts has "+str(len(ContextDataDict))+" dictionaries")
    # pp.pprint(ContextDataDict)

    InterestingContexts = []

    for Context, ContextDict in ContextDataDict.items():
        try:
            if ContextDict['NetIncomeLoss'] != None:
                InterestingContexts.append(Context)
        except KeyError:
            pass

    docEndDateStr = DEIDict['DocumentPeriodEndDate']
    print("Statement period end date " + docEndDateStr)

    isVeryInteresting = False
    for ic in InterestingContexts:
        isVeryInteresting = False
        dateStr = toDateStr(DateContextDict[ic].periodEnd)
        print("Interesting context: " + ic + " " + dateStr)
        if dateStr == docEndDateStr:
            isVeryInteresting = True
            print("\t(This one is especially interesting.)")
        periodLength = DateContextDict[ic].periodEnd - DateContextDict[ic].periodStart
        print("\tPeriod of this context is " + str(periodLength.days) + " days")
        if isVeryInteresting and periodLength.days == 90:
            print("Most interesting context:")
            pp.pprint(ContextDataDict[ic])


def main():
    if len(sys.argv) < 2:
        print("Usage: "+sys.argv[0]+" <XML file name>")
        sys.exit(-1)

    inputFilename = sys.argv[1]

    # conn = psycopg2.connect(database="stocks_us", user="postgres", password="v3gBdD#VI")
    # cur = conn.cursor()

    parseFiling(inputFilename)


    # cur.close()
    # conn.close()


if __name__ == "__main__":
    main()
