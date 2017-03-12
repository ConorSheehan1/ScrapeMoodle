## Setup
1. `pip install requirements.txt` 
2. `python setup.py`
3. `python moodle_scraper.py`

## Output
1. Typical output should look something like this
![example.png](/img/example.png)

2. If the program exits successfully you will receive the following message
![success.png](/img/success.png)

## constructor settings
(Moodle.\_\_init\_\_())

1. details (default=True)
	* Will print the files being downloaded and links being visited to the console.  
		If this is set to False only the login and final summary will be printed.  
		This may also reduce runtime
2. parser (default="lxml")
	* Parser to use with beautiful soup. Untested with anything other than lxml
3. download (default=True) (used for debugging)
	* If this is set to false no pdfs will be downloaded by all folders visited and errors will be printed (if details is set to True)
4. overwrite (default=False)
	* If set to True new pdfs will overwrite existing ones

## errors
A typical error when downloading a file is quite large. This is because I decided to leave the entire html as is, in case the error is caused by parsing the html. This way, not matter what went wrong, you get all the html the script was trying to parse.
![typical_error.png](/img/error.png)

If you have an incorrect username or password you should receive the following error
![credential_error.png](/img/credential_error.png)