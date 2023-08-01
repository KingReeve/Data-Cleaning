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

datafilepath = input("Input the desired filepath for the text file data.")
dataoutput = input("Input the desired filepath for writing the .csv output")

dataFile = open(datafilepath, "r")

dataFromFile = dataFile.read()
dataFromFile = dataFromFile.split("\n") #Text file, but tests are on various lines, so that's the natural delimiter

dataDict = defaultdict(list) #defaultdict allows you to append multiple values to a key as a list instead of overwriting, without any hassle on my part

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
        continue #skip lines that don't contain the test data.
    templist = i.partition("Cmd: ") #made a temporary partition and used re.search because it will only find the first occurrence.  The data comes after actual, and the important data is after the Cmd value.
    y = re.search(r'(?<=Actual: )(.*?)(?= )', templist[2]).group() #this will be the values
    dataDict[x].append(y)

if not dataDict:
    raise SystemExit("File contained no appropriate data.") #dictionaries are falsy.

ColumnLabel = DAUname + ' ' + Platformname
LabelDict = {'Test#' : ColumnLabel}
pdReadyDict = LabelDict #getting ready to update, could probably just use LabelDict.
for d in dataDict: pdReadyDict.update(dataDict) #just appends the data after the "header"
flatpdreadydict = flattenDictionary(pdReadyDict) #runs the flattening code from earlier.  The data comes with many duplicates without data, but which may have data in the future, so they can't be deleted.

#PandasFrame = pandas.DataFrame.from_dict(dataDict)  Dataframe won't take varying lengths like this
#could actually probably start using dataframe.from_dict() again, since I'm now flattening the data.
PandasFrame = pandas.DataFrame({k: pandas.Series(v) for k,v in flatpdreadydict.items()}) #taking key/values and putting them into an array, and mushing them together
excelReadyPandasFrame = PandasFrame.transpose(copy=True) #want rows to be new data, rather than columns. Eventually, the columns will be merged into one     file to do some data analysis.
excelReadyPandasFrame.to_csv(dataoutput)
