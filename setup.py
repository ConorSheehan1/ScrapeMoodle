import os
import colorama
from colorama import Fore


def main(user_name, pass_word, path="secret.py"):
    content = "class Secret:\n\tusername = '{0}'\n\tpassword = '{1}'\n".format(user_name, pass_word)

    if os.path.exists(path):
        while True:
            print(Fore.RED + "\n" + path + " already exists\npress y to overwrite it\npress n to exit")
            print(Fore.WHITE)
            choice = input().lower()
            if choice == "y":
                os.remove(path)
                break
            if choice == "n":
                return False

    with open(path, "w") as pythonfile:
        pythonfile.write(content)
    return True

if __name__ == "__main__":
    colorama.init()
    username = input("enter username (student number)\n")
    password = input("\nenter password\n")
    done = main(username, password)
    if done:
        print(Fore.GREEN + "setup successful")
    else:
        print(Fore.RED + "setup unsuccessful, please try again")