import pandas
from collections import defaultdict
import glob
import re
from pathlib import Path

def flattenDictionary(d):
    flat_dict = {}
    for key,val in d.items():
        if len(val) != 1 and isinstance(val,list):
            flat_dict.update({f'{key}_{i+1}':v for i,v in enumerate(val)})
        else:
            flat_dict[key] = val
    return flat_dict

def normaltest(dataFromFile):
    for i in dataFromFile:
        try:
            Platformname = re.search(r'(?<=Platform: )(.*)', i, flags=re.IGNORECASE).group()
        except:
            pass
        try:
            DAUname = re.search(r'(?<=DAU SN: )(.*)', i, flags=re.IGNORECASE).group()
        except:
            pass
        try:
            x = re.search(r'(?<=Test.: )(.*?)(?= ...:)', i, flags=re.IGNORECASE).group() + ' ' + re.search(r'Cmd: (.*?)(?= )', i, flags=re.IGNORECASE).group()  #this will be the keys for the dictionary, the test names
        except:
            continue
        templist = i.partition("Cmd: ") # couldn't find elegant solution, gave up and made a temporary size 3 tuple and used re.search because it will only find the first occurrence
        y = re.search(r'(?<=Actual: )(.*?)(?= )', templist[2]).group() #this will be the values
        dataDict[x].append(y)

    if not dataDict:
        raise SystemExit("File contained no appropriate data.")

    ColumnLabel = DAUname + ' ' + Platformname
    LabelDict = {'Test#' : ColumnLabel}
    pdReadyDict = LabelDict
    for d in dataDict: pdReadyDict.update(dataDict)
    flatpdreadydict = flattenDictionary(pdReadyDict)
    return flatpdreadydict

def SandBoxTest(dataFromFile):
    for i in dataFromFile:
        try:
            SerialNumber = re.search(r'UUT Serial Number: (.*?)[\s]', i, flags=re.IGNORECASE).group()
        except:
            pass
        try:
            TestSettings = re.search(r'Tester Loads = (.*),', i, flags=re.IGNORECASE).group() + ' ' + re.search(r'Configuration = (.*)', i, flags=re.IGNORECASE).group().strip() + ' '
        except:
            pass
        try:
            StateTolerance = re.search(r'State Tolerance(.*?)V', i, flags=re.IGNORECASE).group().strip() + ' '
        except:
            pass
        try:
            Digital = ' '.join(re.search(r'DOUT(.*)tive', i, flags=re.IGNORECASE).group().split())
            x = TestSettings + StateTolerance + Digital
            y = re.search(r'(?<=<  )(.*?)(?=<)', i, flags=re.IGNORECASE).group().strip()
        except:
            try:
                x = re.search(r'A0(.*?)V', i, flags=re.IGNORECASE).group().strip()
                y = re.search(r'(?<=V )(.*?)V', i, flags=re.IGNORECASE).group().strip()
            except:
                continue
        dataDict[x].append(y)

    ColumnLabel = SerialNumber
    LabelDict = {'Testing' : ColumnLabel}
    pdReadyDict = LabelDict
    for d in dataDict: pdReadyDict.update(dataDict)
    
    if not dataDict:
        raise SystemExit("File contained no appropriate data.")
    return pdReadyDict

WantBatch = None
while WantBatch is None:
    Test = input('If you want to use the whole folder method instead of single file, type True. Otherwise, just hit enter ')
    if Test == "True" or Test == "true":
        WantBatch = True
    else: 
        WantBatch = False

if WantBatch:
    inputfilepath = input('Type the filepath to the folder you want to execute on: ')
    files = glob.glob(f'{inputfilepath}\\*')
    dataoutput = input('Type the filepath to the EMPTY(easier to find relevant files) folder you want the output files: ')

else:
    datafilepath = input("Input the filepath of the test data: ")   #when testing, gotta compensate for '\' escape characters.  input() function returns the exact input without allowing those
    dataFile = open(datafilepath, "r")
    dataoutput = input("Input the desired output filepath: ")
    dataDict = defaultdict(list)



if WantBatch:

    for file in files:
        datafilepath = file
        outputfilepath = dataoutput + file.removeprefix(inputfilepath).removesuffix('.txt') + '_converted.csv'
        dataFile = open(datafilepath, "r")
        data = dataFile.read()
        data = data.split("\n")
        dataDict = defaultdict(list)
        if "SandBox" in datafilepath:
            pdready = SandBoxTest(data)
        else:
            pdready = normaltest(data)
        PandasFrame = pandas.DataFrame({k: pandas.Series(v) for k,v in pdready.items()})
        excelReadyPandasFrame = PandasFrame.transpose(copy=True)
        excelReadyPandasFrame.to_csv(outputfilepath)
    
    raise SystemExit("Finished")

else:
    data = dataFile.read()
    data = data.split("\n") #Text file, but tests are on various lines, so that's the natural delimiter

    if "SandBox" in datafilepath:
        pdready = SandBoxTest(data)
    else:
        pdready = normaltest(data)

    #PandasFrame = pandas.DataFrame.from_dict(dataDict)  Dataframe won't take varying lengths like this
    PandasFrame = pandas.DataFrame({k: pandas.Series(v) for k,v in pdready.items()}) #series are just arrays, in this we're taking key/values and putting them into an array, and mushing them together
    excelReadyPandasFrame = PandasFrame.transpose(copy=True)
    excelReadyPandasFrame.to_csv(dataoutput)
