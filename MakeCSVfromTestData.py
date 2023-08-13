import pandas
from collections import defaultdict
import re

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

datafilepath = input("Input the filepath of the test data: ")   #gotta compensate for '\' escape characters,  input() function returns the exact input without allowing those
dataFile = open(datafilepath, "r")

dataoutput = input("Input the desired output filepath: ")

data = dataFile.read()
data = data.split("\n") #Text file, but tests are on various lines, so that's the natural delimiter

dataDict = defaultdict(list) #defaultdict allows you to append multiple values to a key instead of overwriting, without any hassle on my part

if "SandBox" in datafilepath:
    pdready = SandBoxTest(data)
else:
    pdready = normaltest(data)

#PandasFrame = pandas.DataFrame.from_dict(dataDict)  Dataframe won't take varying lengths like this
PandasFrame = pandas.DataFrame({k: pandas.Series(v) for k,v in pdready.items()}) #series are just arrays, in this we're taking key/values and putting them into an array, and mushing them together
excelReadyPandasFrame = PandasFrame.transpose(copy=True)
excelReadyPandasFrame.to_csv(dataoutput)
