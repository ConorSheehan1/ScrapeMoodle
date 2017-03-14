import requests
import re
from bs4 import BeautifulSoup, SoupStrainer
import colorama
from colorama import Fore
import os
import time

try:
	from secret import Secret
except ImportError:
	print("Please run setup.py or follow the instructions in the readme to create secret.py")


class Moodle:
	def __init__(self, login_url, username, password, details=True, parser="lxml", download=True, overwrite=False):
		'''
		:param details: print what's happening to the console
		:param parser: parse for beautiful soup (lxml by default)
		:param download: actually download pdfs
		:param download: overwrite pdfs if they already exist
		:return:
		'''
		# setup color console
		colorama.init()

		# place holder for saving pdfs to correct folder
		self.folder = ""
		self.base_folder = "moodle_download/"

		if not os.path.exists(self.base_folder):
			os.mkdir(self.base_folder)

		self.details = details
		self.parser = parser
		self.download = download
		self.overwrite = overwrite

		self.visited = []
		self.failed = {}
		self.successful = 0
		self.unsuccessful = 0
		self.session_requests = requests.session()
		payload = {
			"username": username,
			"password": password
		}
		# log in to site
		self.login_result = self.session_requests.post(
			login_url,
			data=payload,
			headers=dict(referer=login_url)
		)

		# print(self.login_result.content)
		if self.login_result.ok:
			if "Invalid login, please try again" in str(self.login_result.content):
				print(Fore.RED + "Incorrect login credentials. Run setup.py", self.login_result.status_code)
			else:
				print(Fore.GREEN + "Login successful", self.login_result.status_code)
		else:
			print(Fore.RED + "Login unsuccessful", self.login_result.status_code)

		# start timing
		self.start_time = time.clock()

	def __repr__(self):
		return Fore.GREEN + "\n\n\tSuccessfully downloaded\t {0:8} pdfs\n".format(self.successful) + Fore.RED\
			   + "\tFailed to download\t {0:8} pdfs\n".format(self.unsuccessful)\
			   + Fore.WHITE + "\tTime elapsed: {:.2f} seconds".format(time.clock()-self.start_time)

	def show_failed(self):
		for val in self.failed:
			print(self.failed[val], val)

	@staticmethod
	def parse_link(url):
		# links usually end with = and some number
		# parse from href= until =[some_number(s)]
		try:
			# todo: fix to stop as soon as =[num] is found
			# link = re.findall(r'(?<=href=").+=[0-9]+', url)[0]
			# math up until quote
			link = re.findall(r'(?<=href=")[^"]*', url)[0]
		except IndexError:
			link = re.findall(r'(?<=href=").+(\.pdf)', url)[0]
		return link

	@staticmethod
	def parse_title(url):
		try:
			# try getting last text between instancename> and <span, if that fails get last piece of text outside of tags
			title = re.findall(r'(?<=instancename">).+(?=<span)', url)[-1]
		except IndexError:
			title = re.findall(r'(?<=>)[a-zA-Z0-9\s._\-,]+(?=<)', url)[-1]
		return title

	def download_pdf(self, title, url):
		if not title.endswith(".pdf"):
			title += ".pdf"

		title = re.sub(r"[^\w\s\-\._]*", "", title)

		# if the file doesn't exist or overwrite is set to true, download the file
		if not os.path.exists(self.base_folder + self.folder + title) or self.overwrite:
			r = self.session_requests.get(url)
			with open(self.base_folder + self.folder + title, "wb") as pdffile:
				pdffile.write(r.content)

			if self.details:
				print(Fore.GREEN + "downloaded", title, "\n" + url)
			# if file was downloaded return 1
			return 1
		# otherwise return 0
		return 0

	def find_pdfs(self, url):
		'''

		:param url: address to scrape pdfs from
		:param visited: list of folders visited
		:return:
		'''

		# if url has been visited or links to external site, exit
		if url in self.visited or "https://csmoodle" not in url:
			return
		else:
			# add current link to visited
			self.visited.append(url)

		# keep list of sub-links to visit (folders, assignments)
		to_visit = set()

		result = self.session_requests.get(url, headers=dict(referer=url))
		for link in BeautifulSoup(result.content, self.parser, parse_only=SoupStrainer('a')):
			current = str(link)
			if "pdf" in current:
				try:
					error = "url"
					pdf_url = self.parse_link(current)
					error = "title"
					title = self.parse_title(current)
					if self.download:
						self.successful += self.download_pdf(title, pdf_url)

				# if regex fails to parse pdf link
				except IndexError:
					self.unsuccessful += 1
					self.failed[current] = error
					if self.details:
						print(Fore.RED + "error parsing", error, current)

			elif "folder" in current or "assign" in current:
				try:
					new_link = self.parse_link(current)

				# if regex fails, skip iteration in loop
				except IndexError:
					if self.details:
						print(Fore.RED + "error parsing folder", current)
					continue

				# if parsed folder link is not the url the method was called on
				if new_link not in self.visited:
					to_visit.add(new_link)

		# patch problem with ampersands continuing link
		# todo: update regex in parse_link?
		to_visit = set(map(lambda n: n.split("&")[0], to_visit))

		# visit subfolders
		for sub_link in to_visit:
			if self.details:
				print(Fore.YELLOW + "visiting folder", sub_link)
			self.find_pdfs(sub_link)

	def get_comp_modules(self):
		# get all the links to other COMP courses you're enrolled in from the home page
		for link in BeautifulSoup(self.login_result.content, self.parser, parse_only=SoupStrainer('a')):
			current = str(link)
			if 'title="COMP' in current:
				# match after title=" and accept anything other than a quote, remove spaces
				# set current folder to name of module code
				self.folder = re.findall(r'(?<=title=")[^"]*', current)[0].replace(" ", "") + "/"
				href = self.parse_link(current)

				if not os.path.exists(self.base_folder + self.folder) and self.download:
					os.mkdir(self.base_folder + self.folder)

				if self.details:
					print(Fore.WHITE + self.folder, href)

				self.find_pdfs(href)

if __name__ == "__main__":
	m = Moodle("https://csmoodle.ucd.ie/moodle/login/index.php", Secret.username, Secret.password, overwrite=True)
	m.get_comp_modules()
	print(m)
	m.show_failed()
