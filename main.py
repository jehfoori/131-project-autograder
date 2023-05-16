from bparser import BParser
from interpreterv2 import Interpreter

def main():
  # all programs will be provided to your interpreter as a list of 
  # python strings, just as shown here.
  program_source = ['(class person (field string name "jeffrey") (method void print_name () (print name) ) ) (class person2 (field string name "jeffrey") (method void print_name () (print name) ) ) (class main (field person pf null) (field person pf2 null) (method void main () (begin (set pf (new person)) (set pf2 pf) (call pf print_name) (print (== pf2 null)) ) ) )']
  
  itrptr = Interpreter()
  itrptr.run(program_source)

if __name__ == "__main__":
	main() # could be named anything
