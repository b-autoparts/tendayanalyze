import os
import csv

EOF = '9999999999999999'

def getHeader(line, dates):
  meta, _ = line.split()
  meta = meta.split('|')
  plant = meta[2]
  extras = ["Firm", "1 TEN", "2 TEN", "3 TEN",	"4 TEN", "5 TEN", "2M",	"3M",	"4M"]
  return ["PLANT " + plant, ''] + dates + extras 




def processLine(line):
  meta, data = line.split()
  meta = meta.split('|')
  data = data.split('|')[1:-1]
  part = meta[4]
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
  preInfo = [item for sublist in zip(preDates, preValues) for item in sublist]
  # info = [item for sublist in zip(dates, values) for item in sublist]
  l = ''
  for x,y in zip(preDates, preValues): l = l + str(x) + "/" + str(y) + ", "
  returnInfo = [part] + [l] + values + otherInfo
  return returnInfo, dates

def processFile(f, name):
  line = f.readline()
  main_data = []
  data, dates = processLine(line)
  header = getHeader(line, dates)
  if(name[0] == 'D'): # this assumes that everytime we run into the D/F factory case, the file starts with a D
    f_data = []
    headerF = header[:]
    headerF[0] = 'PLANT F'
    f_data.append(headerF)

    d_data = []
    headerD = header[:]
    headerD[0] = 'PLANT D'
    d_data.append(headerD)

    f_data.append(data) if header[0] == 'PLANT F' else d_data.append(data)
    while line:
      line = f.readline()
      if EOF in line: break
      data, _ = processLine(line)
      header = getHeader(line, dates)
      if header[0] == 'PLANT F':
        f_data.append(data)
      if header[0] == 'PLANT D':
        d_data.append(data)
    main_data = d_data + f_data

  else:
    main_data.append(header)
    main_data.append(data)
    while line:
      line = f.readline()
      if EOF in line: break
      data, _ = processLine(line)
      main_data.append(data)
  return main_data

def filterPart(part, plant):
  if (plant == 'G' and part.endswith('G')):
    return part[:-1]
  else:
    return part

# FILE_NAMES = ['BDB097','DDB097','GDB097','HDB097']
FILE_NAMES = ['BDB097','DDB097']
files = filter(lambda x: not x.endswith('.py'), os.listdir('./'))
# assert(len(files) == 5)
# for name in files:
# assert(name in FILE_NAMES)
BIG_DATA = []
for NAME in FILE_NAMES:
  with open(NAME) as f:
    BIG_DATA += processFile(f, NAME)

with open('DATA.csv', 'w', newline='') as f:
  writer = csv.writer(f)
  writer.writerows(BIG_DATA)

PART_DICT = {}
for datum in BIG_DATA:
  partName = datum[0]
  if 'PLANT ' in partName: continue
  if partName in PART_DICT:
    oldData = PART_DICT[partName]
    newData = [partName] + [x + y for x, y in zip(datum[1:], oldData[1:])]
    PART_DICT[datum[0]] = newData
  else:
    PART_DICT[datum[0]] = datum

SUM_DATA = list(PART_DICT.values()) 

with open('SUM-TENDAY.csv', 'w', newline='') as g:
  writer = csv.writer(g)
  writer.writerows(SUM_DATA)

    




          