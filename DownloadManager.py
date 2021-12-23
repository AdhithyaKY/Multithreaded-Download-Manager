import getopt, sys, requests, re, threading, time

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

def downloadChunk(url, start, end, filename):
    print(start)
    print(end)
    #header to pass in with get request containing the start and end byte of chunk
    headers = {'Range': 'bytes=%d-%d' % (int(start), int(end))}

    r = requests.get(url, headers=headers, stream=True)

    with open(filename, "r+b") as f:
        f.seek(int(start))
        currPosition = f.tell()
        f.write(r.content)

def main():
    startTime = time.time()

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

    isDownloadable = checkIfDownloadable(url)
    header = retrieveHeader(url)
    filename = retrieveFilename(url)
    fileSize = int(header.get('content-length'))
    if not fileSize:
        print("URL does not support content-length in header.")
        return
    
    if not filename:
        filename = "DownloadedFile"

    print(header)
    print(fileSize)
    chunkSize = int(fileSize) / 3
    outputFile = open(filename, "wb")
    outputFile.close()

    for i in range(3):
        start = chunkSize * i
        end = start + chunkSize

        thread = threading.Thread(target=downloadChunk, args=(url, start, end, filename))
        thread.start()

    mainThread = threading.current_thread()

    for thread in threading.enumerate():
        if thread is mainThread:
            continue
        thread.join()

    print("Downloaded " + url)
    print(time.time()-startTime)

main()
