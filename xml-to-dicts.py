#!/usr/bin/env python
#
# Parse an XBRL file and store the interesting data to data structures.
#
# Todo: capture CashAndCashEquivalentsAtCarryingValue
#
import pprint
import psycopg2
import sys
from datetime import datetime
import xml.etree.ElementTree as ET

gVerbose = False


class DateContext:
    def __init__(self, periodStart, periodEnd):
        # Note that periodStart may be None if the context's date range is "instant"
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


class XBRLParser:

    def __init__(self, filename):
        self.inputFilename = filename


    def extractNamespace(self, key, namespaceDict):
        nsValue = namespaceDict[key]
        if nsValue == None:
            print("Missing US GAAP namespace from : "+usGAAPns)
        return nsValue


    toDateStr = lambda self,d : d.strftime("%Y-%m-%d")


    def parseFiling(self):
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

        for event, elem in ET.iterparse(self.inputFilename, events):
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
                    usGAAPns = self.extractNamespace('us-gaap', namespaceDict)

                    # Document and Entity Information
                    DEIns = self.extractNamespace('dei', namespaceDict)

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
                            verbose("Found central index key " + DEItext + " converted to int " + str(CIK))
                        elif DEIterm == "DocumentPeriodEndDate":
                            EndDate = datetime.strptime(DEItext, "%Y-%m-%d")
                            print("Found document period end date " + self.toDateStr(EndDate))
                        else:
                            if len(DEItext) > 100:
                                DEItext = DEItext[0:100] + "...\n"
                            verbose("DEI term " + DEIterm + " " + DEItext)
                    else:
                        print(DEIterm + " has no text")
                elif "context" in tag:
                    verbose("Found context end "+tag)
                    isValidPeriod = False
                    isValidInstant = False
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
                                elif "instant" in periodElement.tag:
                                    # Filing data for the balance sheet all use an "instant" context with
                                    # the text containing the dei:DocumentPeriodEndDate
                                    instantDateString = periodElement.text
                                    endDate = datetime.strptime(instantDateString, "%Y-%m-%d")
                                    verbose("\tFound instant string " + instantDateString + " for context " + contextID)
                                    if endDate:
                                        isValidInstant = True
                        if "entity" in contextElement.tag:
                            verbose("    Iterating over entity elements")
                            identityIter = contextElement.iter()
                            for identityElement in identityIter:
                                verbose("\tFound identity element " + str(identityElement))
                                if "identifier" in identityElement.tag:
                                    contextCIK = int(identityElement.text)
                                    verbose("\tFound CIK " + str(contextCIK))

                    if contextCIK == CIK and isValidPeriod:
                        verbose("Adding context for period " + self.toDateStr(startDate) + " to " + self.toDateStr(endDate))
                        c = DateContext(startDate, endDate)
                        # Add an entry for this context ID and time period
                        DateContextDict[contextID] = c
                    elif contextCIK == CIK and isValidInstant:
                        if contextID == "eol_PE2035----1510-K0012_STD_0_20150926_0":
                            print("This should be the balance sheet context")
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
                        verbose(OtherTerm + " has no text")
                        pass"""

        # For now, log the contents of the DEI dictionary
        pp = pprint.PrettyPrinter(indent = 2)
        print("DEI dictionary has:")
        pp.pprint(DEIDict)

        # Here's where you can log the contents of all the US GAAP dictionaries as a function of their context ref
        print("Context dict of data dicts has "+str(len(ContextDataDict))+" dictionaries")
        # pp.pprint(ContextDataDict)

        InterestingContexts = []

        for Context, ContextDict in ContextDataDict.items():
            if ContextDict.get('NetIncomeLoss') != None or ContextDict.get('CashAndCashEquivalentsAtCarryingValue') != None:
                InterestingContexts.append(Context)

        docEndDateStr = DEIDict['DocumentPeriodEndDate']
        print("Statement period end date " + docEndDateStr)

        docType = DEIDict['DocumentType']
        print("Statement type " + docType)

        periodMin = 0
        periodMax = 0
        if docType == '10-K':
            periodMin = 360
            periodMax = 369
        elif docType == '10-Q':
            periodMin = 89
            periodMax = 96
        else:
            print('What the what with document type ' + docType)

        # The income and cash flow data use a date range, while the balance sheet
        # data use the instant of the end date of the statement. Save the relevant
        # dictionaries for each
        DateRangeContextData = None
        InstantContextData = None

        for ic in InterestingContexts:
            dateContext = DateContextDict[ic]
            dateStr = self.toDateStr(dateContext.periodEnd)
            verbose("Context containing an interesting entry: " + ic + " " + dateStr)
            if ic == "eol_PE2035----1510-K0012_STD_0_20150926_0":
                print("This should be the balance sheet context")
            if dateStr == docEndDateStr:
                verbose("\tThe period of this context ends on the same date as the statement.")
                # Handle contexts with a date range:
                if dateContext.periodStart != None:
                    periodLength = dateContext.periodEnd - dateContext.periodStart
                    verbose("\tPeriod of this context is " + str(periodLength.days) + " days")
                    dataDict = ContextDataDict[ic]
                    if len(dataDict) > 15  and periodLength.days >= periodMin and periodLength.days <= periodMax:
                        print("\tThis range data dictionary has " + str(len(dataDict)) + " entries")
                        if DateRangeContextData:
                            print("*** We have already seen an interesting date range context")
                        DateRangeContextData = dataDict
                        print("Most interesting date range context:")
                        pp.pprint(dataDict)
                else:
                    dataDict = ContextDataDict[ic]
                    if dataDict.get('CashAndCashEquivalentsAtCarryingValue') != None:
                        # the start date is None, and the dictionary appears to have
                        # balance sheet data, so save it
                        if len(dataDict) > 15:
                            if InstantContextData:
                                print("*** We have already seen an interesting instant context")

                            InstantContextData = dataDict
                            print("\tMost instant data dictionary has " + str(len(dataDict)) + " entries")
                            pp.pprint(InstantContextData)

        print('\nProcessing complete\n')

        return InstantContextData, DateRangeContextData


def main():
    if len(sys.argv) < 2:
        print("Usage: "+sys.argv[0]+" <XML file name>")
        sys.exit(-1)

    inputFilename = sys.argv[1]

    # conn = psycopg2.connect(database="stocks_us", user="postgres", password="v3gBdD#VI")
    # cur = conn.cursor()

    xbrlParser = XBRLParser(inputFilename)

    balanceDict, incomeDict = xbrlParser.parseFiling()

    # cur.close()
    # conn.close()


if __name__ == "__main__":
    main()
