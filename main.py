from bparser import BParser
from interpreterv2 import Interpreter

def main():
  # all programs will be provided to your interpreter as a list of 
  # python strings, just as shown here.
  program_source = ['(class person (field string name "jane") (method void set_name ((string n)) (set name n)) (method string get_name () (return name)) ) (class student inherits person (field int beers 3) (method void set_beers ((int g)) (set beers g)) (method int get_beers () (return beers)) ) (class main (field person s null) (method void main () (begin (set s (new student)) (print (call s get_name) " has " (call s get_beers) " beers") ) ) )']
  
  itrptr = Interpreter()
  itrptr.run(program_source)

if __name__ == "__main__":
	main() # could be named anything
