import os
import cantools
import sys
from converter_class import ConverterClass
  
def check_args():
  if(len(sys.argv) != 2):
    print("Incorrect Arguments")
    print("Expecting the following: (1) dbc file path")
    quit()

  if not os.path.isfile(sys.argv[1]):
    print("Unable to open file path for DBC file")
    quit()
  
def main():
  check_args()  
  db = cantools.database.load_file(sys.argv[1])  
  cc = ConverterClass(sys.argv[1])
  cc.create_header_file() 
  cc.create_source_file() 

if __name__ == "__main__":
    main()