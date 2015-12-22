#!/usr/bin/env python
#
# Testing the idea from:
# http://stackoverflow.com/questions/17799790/using-xpath-to-extract-data-from-an-xml-column-in-postgres
#
import pprint
import psycopg2
import sys
import xml.etree.ElementTree as ET

# From http://stackoverflow.com/questions/1953761/accessing-xmlns-attribute-with-python-elementree
#
def parse_and_get_ns(file):
    events = "start", "start-ns"
    root = None
    ns = {}
    for event, elem in ET.iterparse(file, events):
        if event == "start-ns":
            # if elem[0] in ns and ns[elem[0]] != elem[1]:
            # NOTE: It is perfectly valid to have the same prefix refer
            #     to different URI namespaces in different parts of the
            #     document. This exception serves as a reminder that this
            #     solution is not robust.    Use at your own peril.
            # raise KeyError("Duplicate prefix with different URI found.")
            if len(elem[0]) > 0:
                ns[elem[0]] = "%s" % elem[1]
        elif event == "start":
            if root is None:
                root = elem
    return ET.ElementTree(root), ns


def extractNamespace(key, namespaceDict):
    nsValue = namespaceDict[key]

    if nsValue == None:
        print("Missing US GAAP namespace from : "+usGAAPns)

    return nsValue

def parseFiling(inputFilename, namespaceDict):

    # Generally Accepted Accounting Practices
    usGAAPns = extractNamespace('us-gaap', namespaceDict)

    # Document and Entity Information
    DEIns = extractNamespace('dei', namespaceDict)

    for event, elem in ET.iterparse(inputFilename):
        tag = elem.tag
        if usGAAPns in tag:
            GAAPterm = tag.replace('{'+usGAAPns+'}', '', 1)
            GAAPtext = elem.text
            if GAAPtext != None:
                if len(GAAPtext) > 100:
                   GAAPtext = GAAPtext[0:100] + "..."
                print("GAAP term " + GAAPterm + " " + GAAPtext + " contextRef " + elem.attrib.get('contextRef'))
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
            print("Found context "+tag)
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

def main():
    if len(sys.argv) < 2:
        print("Usage: "+sys.argv[0]+" <XML file name>")
        sys.exit(-1)

    inputFilename = sys.argv[1]

    XBRLroot, namespaces = parse_and_get_ns(inputFilename)

    pp = pprint.PrettyPrinter(indent = 4)
    print("Got XBRLroot "+str(XBRLroot)+"\nNamespaces:")
    pp.pprint(namespaces)

    # conn = psycopg2.connect(database="stocks_us", user="postgres", password="v3gBdD#VI")
    # cur = conn.cursor()

    # for prefix in namespaces:
    #     print("Registering "+prefix + " : " + namespaces[prefix])
    #     ET.register_namespace(prefix, namespaces[prefix])

    parseFiling(inputFilename, namespaces)


    # cur.close()
    # conn.close()


if __name__ == "__main__":
    main()
