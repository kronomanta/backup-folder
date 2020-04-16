backup-local-folder.py
import argparse
from datetime import datetime
import os
import shutil 

def parse_input():
	parser = argparse.ArgumentParser()
	parser.add_argument("-s", "--source", help="source folder path", required=True)
	parser.add_argument("-t", "--destination", help="destination folder path", required=True)
	parser.add_argument("-r", "--rotation", help="max instance to keep", type=int)
	
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
		#rsync_result = os.system("rsync -avhW " + args.source + " " + actual_destination_version_folder)
		rsync_result = os.system("cp -av {} {} > {} 2>{}".format(args.source, actual_destination_version_folder, log_file, log_file))
		if rsync_result != 0:
			raise Exception("rsync failed: " + str(rsync_result))
		
		print("List available versions in " + destination_folder)
		all_versions = []
		for elem_name in os.listdir(destination_folder):
			full_elem_path = os.path.join(destination_folder, elem_name)
			if os.path.isdir(full_elem_path):
				all_versions.append(full_elem_path)
				
		print("Deleting old versions")
		for i in range(0, len(all_versions) - args.rotation):
			print(all_versions[i])
			shutil.rmtree(all_versions[i])

		print('### Finished successfully ###')		
			
	except OSError as e:
		print('### ERROR ###')
		print('Directory not copied. Error: %s' % e)
		sys.exit(1)
		
