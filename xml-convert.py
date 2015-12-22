#!/usr/bin/env python
#
# Testing the idea from:
# http://stackoverflow.com/questions/17799790/using-xpath-to-extract-data-from-an-xml-column-in-postgres
#
import pprint
import psycopg2
import sys
import xml.etree.ElementTree as ET


def extractNamespace(key, namespaceDict):
    nsValue = namespaceDict[key]

    if nsValue == None:
        print("Missing US GAAP namespace from : "+usGAAPns)

    return nsValue


def parseFiling(inputFilename):

    contextID = None
    ContextDataDict = {}
    events = "start", "start-ns", "end", "end-ns"
    XBRLroot = None
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
            print("Got end-ns element "+str(elem))

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
                print("Found context start "+tag+" id "+contextID)

        elif event == "end":
            tag = elem.tag

            if not usGAAPns:
                print("Pre-namespace tag is "+tag)
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
                    print("GAAP term " + GAAPterm + " " + GAAPtext + " contextRef " + GAAPContextRef)
                    dataDict[GAAPterm] = GAAPtext
                else:
                    print(GAAPterm + " has no text")
            elif DEIns in tag:
                DEIterm = tag.replace('{'+DEIns+'}', '', 1)
                DEItext = elem.text
                if DEItext != None:
                    if len(DEItext) > 100:
                       DEItext = DEItext[0:100] + "..."
                    print("DEI term " + DEIterm + " " + DEItext)
                else:
                    print(DEIterm + " has no text")
            elif "context" in tag:
                print("Found context end "+tag)
                contextID = None
            else:
                OtherTerm = tag
                OtherText = elem.text or ""
                OtherText = OtherText.strip()
                if len(OtherText) > 0:
                    if len(OtherText) > 100:
                       OtherText = OtherText[0:100] + "..."
                    print("Other term " + OtherTerm + " text '" + OtherText + "'")
                else:
                    print(OtherTerm + " has no text")
    print("Context dict of data dicts has " + str(ContextDataDict))


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
