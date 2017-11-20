zooboss
=======

This is an application to organize all the malwares in a unorganized collection. With zooboss you will not need a web server or another type of running daemon, just run the zooboss and drink a coffee while it did his job.

# Parameters

`--origin` : The path to be scanned

`--destiny` : The destiny path to store files

`--move` : Determines that the origin file must be moved

`--filetype` : Determines that the destiny will use the file type

`--threads` : The number of threads

# Examples

The example bellow will scan the `/tmp/downloaded_files` using 10 threads to move the files to the samples directory inside the `$HOME` directory.

```
$ python zooboss.py --origin /tmp/downloaded_files --destiny ~/samples -threads 10 --move
```

To create a copy (not move) don't use the `--move` parameter

```
$ python zooboss.py --origin /tmp/downloaded_files --destiny ~/samples -threads 10
```

To organize files and separating using the file type use the parameter `--filetype` :

```
$ python zooboss.py --origin /tmp/downloaded_files --destiny ~/samples -threads 10 --move --filetype
```