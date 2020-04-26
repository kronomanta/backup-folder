import argparse
import os, subprocess
import shutil 

import traceback
import sys

import logging

__version_info__ = (1, 1, 0)
__version__ = '.'.join(str(c) for c in __version_info__)



class BackupManager:
  def __init__(self, args):
    self.rotation = args.rotation
    self.source = args.source.rstrip("/")
	
    self.destination_folder = os.path.join(args.destination, os.path.basename(self.source))
    if not os.path.exists(self.destination_folder):
      os.makedirs(self.destination_folder)
	
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
      logging.info("create first backup folder")
      new_version_path = os.path.join(self.destination_folder, "0") 
      os.makedirs(new_version_path)
      all_versions.append(new_version_path)
    elif (version_count < self.rotation):
      logging.info("create a folder for older version")
      latest_version = int(os.path.basename(all_versions[version_count-1]))
      new_version_path = os.path.join(self.destination_folder, str(latest_version + 1))
      os.makedirs(new_version_path)
      all_versions.append(new_version_path)
    else:
      # delete too old versions
      for i in range(self.rotation, version_count):
        logging.info("delete old version: " + all_versions[i])
        shutil.rmtree(all_versions[i])
      all_versions = all_versions[: self.rotation]  
    return all_versions

  # iterate from the element before the last one to the first one, so we shift the backups one day older
  def shiftVersions(self, all_versions):
    logging.info("make previous backups older")
    if len(all_versions) > 1:
      for i in range(len(all_versions) - 2, -1, -1):
        logging.info("{} -> {}\n\n".format(all_versions[i], all_versions[i+1]))
        rsync_result = subprocess.run(["rsync", "-avh", "--delete", all_versions[i] + "/", all_versions[i+1] + "/"])
        if rsync_result.returncode != 0:
          raise Exception("exit result: {}".format(rsync_result))
  
  # backup live data
  def backupLiveData(self, target_folder):
    logging.info("backup live data: {} -> {}\n\n".format(self.source, target_folder))
    rsync_result = subprocess.run(["rsync", "-avh", "--delete", self.source + "/", target_folder + "/"])
    if rsync_result.returncode != 0:
      raise Exception(" exit result {}".format(rsync_result))

	
  def backup(self):
    logging.info('### Start backup of ' + self.source +' ####')
    
    #get all existing folder containing older versions
    all_versions = self.handleVersionFolders(self.getVersions())
    
    self.shiftVersions(all_versions)
    self.backupLiveData(all_versions[0])
      

def parse_input():
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--source", help="source folder path", required=True)
  parser.add_argument("-t", "--destination", help="destination folder path", required=True)
  parser.add_argument("-r", "--rotation", help="max instance to keep", type=int, required=True)

  return parser.parse_args()
  
if __name__ == '__main__':
  try:  
    logging.basicConfig(
      format='%(asctime)s %(levelname)-8s %(message)s',
      level=logging.INFO,
      datefmt='%Y.%m.%d %H:%M:%S')

    args = parse_input()

    BackupManager(args).backup()
    logging.info('### Finished successfully ###')
  except: # catch *all* exceptions
    logging.error('### ERROR ###')
    logging.error('Directory not copied. Error: {}'.format(traceback.format_exc()))
    sys.exit(1)
