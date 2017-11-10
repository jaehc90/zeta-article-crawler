import os
import os.path
import re
from datetime import timedelta
from datetime import datetime
import diff_match_patch as dmp_module

regex_bracket = re.compile(r"\[(.*?)\]")
regex_paren = re.compile(r"\((.*?)\)")
regex_sentence = re.compile(r"[^.!?]+[.!?]")

def use_lrc_file():
  file = open('./crawled/' + file_name, mode='r', encoding="utf-8")
  lines = file.read().splitlines()
  file.close()
  file = open('./crawled/' + file_name + ".converted", mode='w', encoding='utf-8')
  file.write(lines[0] + '\n')
  file.write(lines[1] + '\n')
  time_begin = datetime.strptime('00:00.00', '%H:%M.%S')
  td = timedelta(seconds = 0.1)
  line_caption_lines = []
  time_stamps = []
  for i in range(3, len(lines), 4):
    time_string = lines[i].split('[', 1)[1].split(']')[0]
    time = datetime.strptime(time_string, '%M:%S.%f')
    time = time - td
    if time < time_begin:
      time = time_begin
    time_string = time.strftime('[%M:%S.%f]')
    file.write(time_string)
    new_line = lines[i][10:len(lines)]
    time_stamps.append(time_string)
    line_caption_lines.append(new_line)
    file.write(new_line + '\n')
    if (i + 4 > len(lines)): #last line
      break
  file.write('\n')
  file.close()
  char_time_index = []
  one_line_sub = ''
  for i in range(len(line_caption_lines)):
    for c in line_caption_lines[i]:
      if c != ' ':
        char_time_index.append((c, time_stamps[i]))
        one_line_sub = one_line_sub + c
  return char_time_index, one_line_sub

def use_sub_file():
  file = open('./crawled/' + file_name_without_extension + '.ko.sub', mode='r', encoding="utf-8")
  lines = file.read().splitlines()
  file.close()
  char_time_index = []
  one_line_sub = ''
  for line in lines:
    timestamp, words = line.split('\t')
    time_begin = datetime.strptime(timestamp, '%H:%M:%S.%f')
    time_string = time_begin.strftime('[%M:%S.%f]')
    for c in words:
      if c != ' ':
        char_time_index.append((c, time_string))
        one_line_sub = one_line_sub + c
  return char_time_index, one_line_sub     

for file_name in os.listdir('./crawled'):
  if file_name.endswith('.lrc'):
    # check if the description contain '(중략)'
    print(file_name)
    statinfo = os.stat('./crawled/' + file_name)
    file_size = statinfo.st_size
    if file_size > 100000 or file_size < 1000:
      continue # file too big or small

    file_name_without_extension = file_name[0:len(file_name) - 7]
    file = open('./crawled/' + file_name_without_extension + '.description', mode='r', encoding="utf-8")
    content = file.read()
    file.close()
    if '(중략)' in content:
      os.remove('./crawled/' + file_name_without_extension + '.m4a')
      os.remove('./crawled/' + file_name_without_extension + '.ko.lrc')
      os.remove('./crawled/' + file_name_without_extension + '.ko.vtt')
      os.remove('./crawled/' + file_name_without_extension + '.description')
      continue

    # read description to extract sentences
    file = open('./crawled/' + file_name_without_extension + '.description', mode='r', encoding="utf-8")
    lines = file.readlines()
    file.close()
    new_lines = []
    for line in lines:
      clean_line = line[0:len(line) - 1]
      if clean_line.startswith('▶ 기사 원문'):
        break
      clean_line = regex_bracket.sub('', clean_line)
      clean_line = regex_paren.sub('', clean_line)
      clean_lines = regex_sentence.findall(clean_line)
      for clean_line in clean_lines:
        if clean_line.endswith('?') or clean_line.endswith('!') or clean_line.endswith('.'): 
         new_lines.append(clean_line.strip())

    char_sentence_index = []
    one_line = ''
    for i in range(len(new_lines)):
      for c in new_lines[i]:
        if c != ' ':
          char_sentence_index.append((c, i))
          one_line = one_line + c

    # clean lrc files
    char_time_index, one_line_sub = use_lrc_file()
    # clean sub files
    #try:
    #  if not os.path.isfile('./crawled/' + file_name_without_extension + '.ko.sub'):
    #    continue
    #  else:
    #    char_time_index, one_line_sub = use_sub_file()
    #except:
    #  continue
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(one_line, one_line_sub, checklines=False);
    dmp.diff_cleanupSemantic(diffs)

    i1 = 0
    i2 = 0
    new_lines_times = []
    str_bld = ''
    current_time = char_time_index[0][1]
    complete = False
    for diff in diffs:
      if diff[0] == 0:
        for c in diff[1]:
          if not complete:
            if char_sentence_index[i1][1] < char_sentence_index[i1 + 1][1]:
              str_bld = str_bld + c
              new_lines_times.append((str_bld, current_time))
              str_bld = ''
              current_time = char_time_index[i2 + 1][1]
            else:
              str_bld = str_bld + c
            i1 = i1 + 1
            i2 = i2 + 1
            complete = i1 + 1 >= len(char_sentence_index) or i2 + 1 >= len(char_time_index)
          else:
            str_bld = str_bld + c
            new_lines_times.append((str_bld, current_time))
      elif diff[0] < 0:
        for c in diff[1]:
          if not complete:
            if char_sentence_index[i1][1] < char_sentence_index[i1 + 1][1]:
              str_bld = str_bld + c
              new_lines_times.append((str_bld, current_time))
              str_bld = ''
              current_time = char_time_index[i2][1]
            else:
              str_bld = str_bld + c
            i1 = i1 + 1
            complete = i1 + 1 >= len(char_sentence_index)
          else:
            str_bld = str_bld + c
            new_lines_times.append((str_bld, current_time))
      else:
        if not complete:
          for c in diff[1]:
            i2 = i2 + 1
            complete = i2 + 1 >= len(char_time_index)
    final_pairs = []
    for j in range(len(new_lines)):
      final_pairs.append((new_lines_times[j][1], new_lines[j]))
    file = open('./crawled/output/' + file_name_without_extension + ".lrc", mode='w', encoding='utf-8')
    for pair in final_pairs:
      file.write(pair[0] + pair[1] + '\n')
    file.close()
