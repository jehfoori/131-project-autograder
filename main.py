from bparser import BParser
from interpreterv2 import Interpreter

def main():
  # all programs will be provided to your interpreter as a list of 
  # python strings, just as shown here.
  program_source = ['(class dog (method void main () (return)) ) (class cat (method void main () (return)) ) (class main (field dog d null) (field cat c null) (method void main () (print (== d c)) ) )']
  
  itrptr = Interpreter()
  itrptr.run(program_source)

if __name__ == "__main__":
	main() # could be named anything
