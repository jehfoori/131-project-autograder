from bparser import BParser
from interpreterv2 import Interpreter

def main():
  # all programs will be provided to your interpreter as a list of 
  # python strings, just as shown here.
  program_source = ['(class main (field main x null) (method void main () (begin (if (== x null) (print "yes")) (if (== null x) (print "yes")) (set x (new main)) (if (!= x null) (print "yes")) ) ) )']
  # '(class main (method fact (n) (if (== n 1) (return 1) (return (* n (call me fact (- n 1)))))) (method main () (print (call me fact 5))))'
  # this is how you use our BParser class to parse a valid 
  # Brewin program into python list format.
  itrptr = Interpreter()
  itrptr.run(program_source)

if __name__ == "__main__":
	main() # could be named anything
