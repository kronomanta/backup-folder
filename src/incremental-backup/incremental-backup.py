import argparse
from datetime import datetime
import os
import shutil 
import re

import traceback
import sys



# Context manager that copies stdout and any exceptions to a log file
class Tee(object):
  def __init__(self, filename):
    self.file = open(filename, 'w')
    self.stdout = sys.stdout

  def __enter__(self):
    sys.stdout = self
    return self;

  def __exit__(self, exc_type, exc_value, tb):
    sys.stdout = self.stdout
    if exc_type is not None:
      self.file.write(traceback.format_exc())
    self.file.close()

  def write(self, data):
    self.file.write(data)
    self.stdout.write(data)

  def flush(self):
    self.file.flush()
    self.stdout.flush()


class BackupManager:
  def __init__(self, args):
    self.sync_log_file_count = args.sync_log_file_count
    self.disable_log_files_to_stdout = args.disable_log_files_to_stdout
    self.rotation = args.rotation
    self.source = args.source.rstrip("/")
	
    self.destination_folder = os.path.join(args.destination, os.path.basename(self.source))
    if not os.path.exists(self.destination_folder):
      os.makedirs(self.destination_folder)
    initLog(self)
  
  def initLog(self):
    date_postfix = datetime.now().strftime("%Y%m%d_%H%M%S")
    self.log_folder = os.path.join(destination_folder, "logs")
    if not os.path.exists(log_folder):
      os.makedirs(log_folder)
    self.log_file = os.path.join(log_folder, date_postfix + ".log")
	
    existing_log_files = [ name for name in os.listdir(self.log_folder) if re.match(r"\d{8}_\d{6}\.log", name) and os.path.isfile(os.path.join(self.log_folder, name))]
    logs_to_delete = min(self.sync_log_file_count, len(existing_log_files))
    for i in range(0, logs_to_delete):
      print("remove old log: {}".format(existing_log_files[i]))
      shutil.rmtree(all_versions[i])
	
  #get all existing folder containing older versions
  def getVersions(self):
    all_versions = []
    for elem_name in os.listdir(self.destination_folder):
      if elem_name.isdigit():
        full_elem_path = os.path.join(self.destination_folder, elem_name)
        if os.path.isdir(full_elem_path):
          all_versions.append(full_elem_path)
    return all_versions
	
  def handleVersionFolders(self, all_versions):
    version_count = len(all_versions)
    if (version_count == 0):
      print("create first backup folder")
      new_version_path = os.path.join(destination_folder, "0") 
      os.makedirs(new_version_path)
      all_versions.append(new_version_path)
    elif (version_count < self.rotation):
      print("create a folder for older version")
      latest_version = int(os.path.basename(all_versions[version_count-1]))
      new_version_path = os.path.join(destination_folder, str(latest_version + 1))
      os.makedirs(new_version_path)
      all_versions.append(new_version_path)
    else:
      # delete too old versions
      for i in range(self.rotation, version_count):
        print("delete old version: " + all_versions[i])
        shutil.rmtree(all_versions[i])
      all_versions = all_versions[: self.rotation]  
    return all_versions;

  # iterate from the element before the last one to the first one, so we shift the backups one day older
  def shiftVersions(self, all_versions):
    print("make previous backups older")
    if len(all_versions) > 1:
      for i in range(len(all_versions) - 2, -1, -1):
        print("{} -> {}".format(all_versions[i], all_versions[i+1]))
        rsync_result = os.system(rsync_command_format.format(all_versions[i], all_versions[i+1], log_file, log_file))
        if rsync_result != 0:
          raise Exception(rsync_command_format.format(str(rsync_result), all_versions[i], all_versions[i+1]))
  
  # backup live data
  def backupLiveData(self, target_folder):
    print("backup live data")
    rsync_result = os.system(rsync_command_format.format(source, target_folder, log_file, log_file))
    if rsync_result != 0:
      raise Exception(rsync_command_format.format(str(rsync_result), source, target_folder))

	
  def backup(self):
    with Tee(log_file):
      print('### Start backup of ' + self.source +' ####')
      
      #get all existing folder containing older versions
      all_versions = self.getVersions(self)
      all_versions = self.handleVersionFolders(self, all_versions)
      
      if self.disable_log_files_to_stdout:
        rsync_command_format = r"rsync -avh --delete {}/ {}/ > {} 2>{}"
      else:
        rsync_command_format = r"rsync -avh --delete {}/ {}/"
      
      rsync_result = -1
      
      self.shiftVersions(self)
      self.backupLiveData(self, all_versions[0])
      

def parse_input():
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--source", help="source folder path", required=True)
  parser.add_argument("-t", "--destination", help="destination folder path", required=True)
  parser.add_argument("-r", "--rotation", help="max instance to keep", type=int, required=True)
  parser.add_argument("--disable-log-files-to-stdout", help="Folder path of internal logs.", type=bool, required=False, default=False)
  parser.add_argument("--sync-log-file-count", help="count of internal log files", type=int, required=False, default=3)

  return parser.parse_args()
  
if __name__ == '__main__':
  try:  
    args = parse_input()
    
    BackupManager(args).backup()
	
    print('### Finished successfully ###')	
  except: # catch *all* exceptions
    e = sys.exc_info()[0]
    print('### ERROR ###')
    print('Directory not copied. Error: %s' % e)
    sys.exit(1)
