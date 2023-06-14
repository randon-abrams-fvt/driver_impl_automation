import os
import cantools
import sys

def check_args():
  if(len(sys.argv) != 3):
    print("Incorrect Arguments")
    print("Expecting the following: (1) dbc file path, (2) output file name")
    quit()

  if not os.path.isfile(sys.argv[1]):
    print("Unable to open file path for DBC file")
    quit()
  
  # if os.path.isfile(sys.argv[2]):
  #   print("The output file already exists")
  #   quit()

def add_driver_header(db, output_fp):
  driver_name = db.buses[0].name
  output_fp.write(
f"""\
#ifndef __{driver_name}_H_
#define __{driver_name}_H_

#include <can_service.h>
#include <stddef.h>
#include "J1939/

namespace driver_lib
{{
class {driver_name}
{{
"""
)

# def add_class_footer(message, output_fp):
  
def add_tx_message(message, driver_name, output_fp):
    output_fp.write(
f"""\
  class {message.name} : public common_lib::CanTxMessage
  {{
      friend class {driver_name};
      
    public:
      {message.name}(
        const uint32_t &_can_id,
        const uint8_t &_channel,
        const uint8_t &_frame_type,
        const uin32_t &_cycle_time);
      
      ~{message.name}();

      virtual void set_data() override;
    
    private:
      struct {message.name}
      {{
""")
     
    for signal in message.signals:
      output_fp.write(f"      uint32_t  {signal.name} : {signal.length};\n")
    output_fp.write(f"     }} data_;\n  }};\n\n") 

def add_rx_message(message, driver_name, output_fp):
    output_fp.write(
f"""\
  class {message.name} : public common_lib::CanRxMessage
  {{
      friend class {driver_name};
      
    public:
      {message.name}(
        const uint32_t &_can_id,
        const uint8_t &_channel,
        const uint8_t &_frame_type,
        const uint32_t &_cycle_time);
      
      ~{message.name}();

      virtual void receive_handler(const common_lib::can_word_t *data) override;
    
    private:
      struct {message.name.lower()}_t
      {{
""")
     
    for signal in message.signals:
      output_fp.write(f"        uint32_t  {signal.name} : {signal.length};\n")
    output_fp.write(f"      }} data_;\n   }};\n\n") 


def main():
  check_args()  
  output_fp = open(sys.argv[2], "w")
  db = cantools.database.load_file(sys.argv[1])  
  
  if(len(db.messages) > 0):
    add_driver_header(db, output_fp)    
    for message in db.messages:
      if len(message.signals) == 0:
        continue
      else:
        if "FVT_ECU" in message.senders:
          add_tx_message(message, db.buses[0].name, output_fp)   
        elif "FVT_ECU" in message.receivers:
          add_rx_message(message, db.buses[0].name, output_fp)
        else:
          continue
  else:
    print("DBC file does not contain any messages")

if __name__ == "__main__":
    main()