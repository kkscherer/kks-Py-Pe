import re, string, sys 

if len(sys.argv) < 2:
	greeting = "Hello"
else:
	greeting = sys.argv[1]
if len(sys.argv) < 3:
	addressee = "World"
else:
	addressee = sys.argv[2] 
if len(sys.argv) < 4:
	punctuation = "."
else:
	punctuation = sys.argv[3]
	
class Felicitations(object):
     def __init__(self):
         self.felicitations = [ ]
     def addon(self, word):
          self.felicitations.append(word)
     def printme(self):
          greeting = string.join(self.felicitations[0:], "")
          print greeting 
     def prints(self, string):
         string.printme()
         return 
     def hello(i):
         string = "hell" + i
         return string
     def caps(self, word):
         value = string.capitalize(word)
         return value

def main():
     salut = Felicitations()
     if greeting != "Hello":
          cap_greeting = salut.caps(greeting)
     else:
          cap_greeting = greeting
     salut.addon(cap_greeting)
     salut.addon(", ")
     cap_addressee = salut.caps(addressee)
     lastpart = cap_addressee + punctuation
     salut.addon(lastpart)
     salut.prints(salut)

if __name__ == '__main__':
     main() 

