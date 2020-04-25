# backup-folder
A simple and easy to use backup solution based on rsync for folders and files. 

# Example

The following snippet creates an incremental backup of the source path ```a/source``` in to the target folder of ```a/target```. In target folder there will be maximum of 4 version of data.
```
python3 -u incremental-backup.py -s a/source -t a/target -r 4
```

# Requirements

Rsync and Python 3.x have to be installed and runnable using only their names.