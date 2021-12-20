import getopt, sys, requests, re

#retrieve header from the response object
def retrieveHeader(url):
    responseObject = requests.head(url, allow_redirects=True)
    header = responseObject.headers
    return header

#retrieve filename from content-disposition header
def retrieveFilename(url):
    header = retrieveHeader(url)
    contentDisposition = header.get('content-disposition')
    #if content-disposition exists as part of the returned header
    if contentDisposition:
        fileName = re.findall('filename=(.+)', contentDisposition)
        #if regex returned a match
        if len(fileName) > 0:
            return fileName[0]
    return None

#retrieve the headers of URL and check if it contains a downloadable resource
def checkIfDownloadable(url):
    header = retrieveHeader(url)
    content_type = header.get('content-type')

    if "text" in content_type.lower() or "html" in content_type.lower():
        return False

    return True

def main():
    #remove 1st argument from list of command line arguments
    listOfArguments = sys.argv[1:]

    #options
    shortOptions = "u:"
    longOptions = ["url="]

    url = ""
    try:
        arguments, values = getopt.getopt(listOfArguments, shortOptions, longOptions)
        for currArgument, currValue in arguments:
            if currArgument in ["--url", "-u"]:
                print("Downloading file from the following url: " + currValue)
                url = currValue
    except getopt.error as error:
        print(str(error))

    print(checkIfDownloadable(url))
    print(retrieveHeader(url))
    print(retrieveFilename(url))

main()
