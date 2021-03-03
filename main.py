import os
import csv

EOF = '9999999999999999'

def sorter(a):
  return a[0]

def getHeader(line, dates):
  meta, _ = line.split()
  meta = meta.split('|')
  plant = meta[2]
  extras = ["Firm", "1 TEN", "2 TEN", "3 TEN",	"4 TEN", "5 TEN", "2M",	"3M",	"4M"]
  return ["Part NO", "PLANT " + plant, ''] + dates + extras 

def getSumheader(header):
  extras = ["Firm", "1 TEN", "2 TEN", "3 TEN",	"4 TEN", "5 TEN", "2M",	"3M",	"4M"]
  return ["No", "Part NO", "Plant", "Add"] + list(filter( lambda x: type(x) == int, header)) + extras


def processLine(line, mainDates=None):
  meta, data = line.split()
  meta = meta.split('|')
  data = data.split('|')[1:-1]
  plant = meta[2]
  part = filterPart(meta[4], plant)
  flag_1 = False # keep iterating until find first non-0 value
  flag_1a = False # keep iterating until the third row
  flag_2 = True # keep iterating until month data ends
  counter_1 = 0
  dates = []
  values = []
  preDates = []
  preValues = []
  otherInfo = []
  for idx, _datum in enumerate(data):
    # find first instance of a number
    # assumption 1: first 3 data is 
    datum = int(_datum)
    if(idx == 3*2):
      flag_1a = True
    if(not flag_1):
      if int(datum) == 0:
        continue
      else:
        flag_1 = True
    if(flag_2):
      if(counter_1 % 2 == 0):
        if(int(datum) == 0):
          flag_2 = False
        else:
          dates.append(datum) if flag_1a else preDates.append(datum)
      else:
        values.append(datum) if flag_1a else preValues.append(datum)
      counter_1 += 1
    else:
      if idx > (len(data)-10): otherInfo.append(datum)
  # preInfo = [item for sublist in zip(preDates, preValues) for item in sublist]
  # info = [item for sublist in zip(dates, values) for item in sublist]
  dataDict = {}
  for a,b in zip(dates,values):
    dataDict[a] = b
  constructedValues = []
  if mainDates:
    for i in mainDates:
      if i in dataDict:
        constructedValues.append(dataDict[i])
      else:
        constructedValues.append(0)
    values = constructedValues
  l = ''
  for x,y in zip(preDates, preValues): l = l + str(x) + "/" + str(y) + ", "
  returnInfo = [part] + [plant] + [l] + values + otherInfo
  # if returnInfo[1] != 'B':
  #   print(mainDates)
  #   print(dates)
  return returnInfo, dates

def processFile(f, name, header = None, mainDates = None):
  line = f.readline()
  main_data = []
  data, dates = processLine(line, mainDates)
  if not header:
    header = getHeader(line, dates)
  if(name[0] == 'D'): # this assumes that everytime we run into the D/F factory case, the file starts with a D
    f_data = []
    headerF = header[:]
    headerF[1] = 'PLANT F'
    f_data.append(headerF)
    d_data = []
    headerD = header[:]
    headerD[1] = 'PLANT D'
    d_data.append(headerD)
    f_data.append(data) if header[1] == 'PLANT F' else d_data.append(data)
    while line:
      line = f.readline()
      if EOF in line: break
      data, _ = processLine(line, mainDates)
      altHeader = getHeader(line, dates)
      if altHeader[1] == 'PLANT F':
        f_data.append(data)
      if altHeader[1] == 'PLANT D':
        d_data.append(data)
    main_data = [headerD] + sumFile(d_data) + [headerF] + sumFile(f_data)
  else:
    main_data.append(data)
    while line:
      line = f.readline()
      if EOF in line: break
      data, _ = processLine(line, mainDates)
      main_data.append(data)
    main_data = [header] + sumFile(main_data)
  if not mainDates : mainDates = dates
  return main_data, header, mainDates

def sumFile(DATA):
  PART_DICT = {}
  for datum in DATA:
    partName = datum[0]
    if 'Part NO' == partName or 'PLANT ' in partName: continue
    if partName in PART_DICT:
      oldData = PART_DICT[partName]
      if(len(oldData) > len(datum)):
        datum += [0]*(len(oldData) - len(datum))
      if(len(oldData) < len(datum)):
        oldData += [0]*(len(datum) - len(oldData))
      newData = [partName] + [x + y for x, y in zip(datum[1:], oldData[1:])]
      newData[1] = ''.join(list(set(list(newData[1]))))
      PART_DICT[datum[0]] = newData
    else:
      PART_DICT[datum[0]] = datum  
  return list(PART_DICT.values()) 

def filterPart(part, plant):
  if (plant == 'G' and part.endswith('G')):
    return part[:-1]
  else:
    return part

FILE_NAMES = ['BDB097','DDB097','GDB097','HDB097']
# FILE_NAMES = ['BDB097','DDB097']
files = filter(lambda x: not x.endswith('.py'), os.listdir('./'))
# assert(len(files) == 5)
# for name in files:
# assert(name in FILE_NAMES)
BIG_DATA = []
header = None
mainDates = None
for NAME in FILE_NAMES:
  with open(NAME) as f:
    temp_data, header, mainDates = processFile(f, NAME, header, mainDates)
    BIG_DATA +=  temp_data

with open('DATA.csv', 'w', newline='') as f:
  writer = csv.writer(f)
  writer.writerows(BIG_DATA)
SUM_DATA = sumFile(BIG_DATA)
SUM_DATA.sort(key=sorter) 
NEW_SUM_DATA = [getSumheader(BIG_DATA[0])] + [[a+1] + b for a,b, in enumerate(SUM_DATA)]

with open('SUM-TENDAY.csv', 'w', newline='') as g:
  writer = csv.writer(g)
  writer.writerows(NEW_SUM_DATA)

FORECAST_DATA = [['Part NO']] + [[a[0]] + [sum(a[-9:-6])] + [sum(a[-6:-3])] + a[-3:] for a in SUM_DATA]


with open('FORECAST.csv', 'w', newline='') as h:
  writer = csv.writer(h)
  writer.writerows(FORECAST_DATA)
    




          
