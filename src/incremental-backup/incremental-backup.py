import argparse
from datetime import datetime
import os
import shutil 

def parse_input():
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--source", help="source folder path", required=True)
  parser.add_argument("-t", "--destination", help="destination folder path", required=True)
  parser.add_argument("-r", "--rotation", help="max instance to keep", type=int, required=True)
	
  return parser.parse_args()
  
if __name__ == '__main__':
  try:
    args = parse_input()
    print('### Start backup of ' + args.source +' ####')
    
    date_postfix = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination_folder = os.path.join(args.destination, os.path.basename(args.source))
    
    if not os.path.exists(destination_folder):
      os.makedirs(destination_folder)
      
    actual_destination_version_folder = os.path.join(destination_folder, date_postfix)
    print("Creating destination directory: " + actual_destination_version_folder)
    
    log_folder = os.path.join(destination_folder, "logs")
    if not os.path.exists(log_folder):
      os.makedirs(log_folder)
    log_file = os.path.join(log_folder, date_postfix)
    
    #os.makedirs(actual_destination_version_folder)
    
    #get all existing folder containing older versions
    all_versions = []
    for elem_name in os.listdir(destination_folder):
      full_elem_path = os.path.join(destination_folder, elem_name)
      if os.path.isdir(full_elem_path):
        all_versions.append(full_elem_path)
        
    
    version_count = len(all_versions)
    if (version_count == 0):
      # create first backup folder
      new_version_path = os.path.join(destination_folder, "0") 
      os.makedirs(new_version_path)
      all_versions.append(new_version_path)
    elif (version_count < args.rotation):
      # create a folder for older version
      latest_version = int(os.path.dirname(all_versions[version_count-1]))
      new_version_path = os.path.join(destination_folder, str(latest_version + 1))
      os.makedirs(new_version_path)
      all_versions.append(new_version_path)
    else:
      # delete too old versions
      for i in range(args.rotation, version_count):
        print("delete old version: " + all_versions[i])
        shutil.rmtree(all_versions[i])
       
    rsync_result = -1
    
    # iterate from the element before the last one to the first one, so we shift the backups one day older
    for i in range(len(all_versions) - 2, 0):
      print(all_versions[i])
      rsync_result = os.system("rsync -avhW {} {} > {} 2>{}".format(all_versions[i - 1], all_versions[i], log_file, log_file))
      if rsync_result != 0:
        raise Exception("rsync failed: {}, source: {}, target: {}".format(str(rsync_result), all_versions[i - 1], all_versions[i]))
    
    # backup live data
    rsync_result = os.system("rsync -avhW {} {} > {} 2>{}".format(args.source, all_versions[0], log_file, log_file))
    if rsync_result != 0:
      raise Exception("rsync failed: {}, source: {}, target: {}".format(str(rsync_result), args.source, all_versions[0]))
    
    
    print('### Finished successfully ###')	
  except OSError as e:
    print('### ERROR ###')
    print('Directory not copied. Error: %s' % e)
    sys.exit(1)
