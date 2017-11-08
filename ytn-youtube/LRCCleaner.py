import os
import os.path
from datetime import timedelta
from datetime import datetime

for file_name in os.listdir('.'):
  if file_name.endswith('.lrc'):
    file = open(file_name, mode='r', encoding="utf-8")
    lines = file.read().splitlines()
    file.close()
    
    file = open('./output/' + file_name, mode='w', encoding='utf-8')
    file.write(lines[0] + '\n')
    file.write(lines[1] + '\n')
    time_begin = datetime.strptime('00:00.00', '%H:%M.%S')
    td = timedelta(seconds = 0.1)
    for i in range(3, len(lines), 4):
      time_string = lines[i].split('[', 1)[1].split(']')[0]
      time = datetime.strptime(time_string, '%M:%S.%f')
      time = time - td
      if time < time_begin:
        time = time_begin
      time_string = time.strftime('[%M:%S.%f]')
      file.write(time_string)
      file.write(lines[i][10:len(lines)] + '\n')
      if (i + 4 > len(lines)): #last line
        break
    file.write('\n')
    file.close()