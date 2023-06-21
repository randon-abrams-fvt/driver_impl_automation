import cantools
import os

class ConverterClass:
  def __init__(self, dbc_fp):
    self.db = cantools.database.load_file(dbc_fp)  

    if len(self.db.messages) == 0:
      print("DBC file contains no messages")
      exit()
    else:
      self.message_list = self.db.messages
      try:
        self.var_enum_list = self.message_list[0].signals[0].dbc.attribute_definitions['CG_VarType'].choices 
      except:
        print("Failed to get enum list from signal") 
        exit()

      try:
        self.driver_name = self.db.buses[0].name    
      except:
        print("The DBC has no CAN network definition")
        exit()
      
      try:
        header_file_path = f"inc/{self.driver_name.lower()}.h"
        os.makedirs(os.path.dirname(header_file_path), exist_ok=True)
        self.header_output_fp = open(f"inc/{self.driver_name.lower()}.h","w")
      except:
        print("Unable to create output header file")
        exit()

      try:
        source_file_path = f"src/{self.driver_name.lower()}.cpp"
        os.makedirs(os.path.dirname(source_file_path), exist_ok=True)
        self.source_output_fp = open(source_file_path,"w")
      except:
        print("Unable to create output source file")
        exit()

      self.sender_message_list = []
      self.sender_signal_list = []
      self.receiver_message_list = []
      self.receiver_signal_list = []

      for message in self.message_list:
        if "FVT_ECU" in message.receivers:
          self.receiver_message_list.append(message)
          for signal in message.signals:
            self.receiver_signal_list.append(signal)
        elif "FVT_ECU" in message.senders:
          self.sender_message_list.append(message)
          for signal in message.signals:
            self.sender_signal_list.append(signal)
    
  def header_add_driver_header(self):
    self.header_output_fp.write(
  f"""\
#ifndef __{self.driver_name}_H_
#define __{self.driver_name}_H_

#include <can_service.h>
#include <stddef.h>
#include "J1939/J1939Helper.h"

namespace driver_lib
{{
class {self.driver_name}
{{
"""
  )

  def header_add_driver_footer(self):
    self.header_output_fp.write(f"  public:\n    typedef enum\n    {{\n")
    for message in self.message_list:
      self.header_output_fp.write(f"      {message.name.upper()}_ID = {hex(message.frame_id).upper()},\n") 
    self.header_output_fp.write(f"    }} message_ids;\n\n")
    self.header_output_fp.write(
f"""\
    {self.driver_name}(const uint8_t &_channel);
    ~{self.driver_name}();
  
  //====================================================  
  // Setters
""")
  
    for signal in self.sender_signal_list:
      self.header_output_fp.write(f"    void set_{signal.name}(const {self.var_enum_list[signal.dbc.attributes['CG_VarType'].value]} &value);\n")
    self.header_output_fp.write(
f"""\
  
  //====================================================  
  // Getters
""")
    for signal in self.receiver_signal_list:
      self.header_output_fp.write(f"    {self.var_enum_list[signal.dbc.attributes['CG_VarType'].value]} get_{signal.name}();\n")
    self.header_output_fp.write(
f"""
  private:
""")

    for message in self.sender_message_list:
      self.header_output_fp.write(f"    {message.name} {message.name.lower()}_;\n")

    for message in self.receiver_message_list:
      self.header_output_fp.write(f"    {message.name} {message.name.lower()}_;\n")

    self.header_output_fp.write(f"}};\n}};\n\n#endif") 

  def header_add_tx_message(self, message):
    self.header_output_fp.write(
f"""\
    class {message.name} : public common_lib::CanTxMessage
    {{
        friend class {self.driver_name};
        
      public:
        {message.name}(
          const uint32_t &_can_id,
          const uint8_t &_channel,
          const uint8_t &_frame_type,
          const uint32_t &_cycle_time);

        ~{message.name}();

        virtual void set_data() override;
      
      private:
        struct {message.name.lower()}_t
        {{
""")
     
    for signal in message.signals:
      self.header_output_fp.write(f"          uint32_t  {signal.name} : {signal.length};\n")
    self.header_output_fp.write(f"       }} data_;\n    }};\n\n") 

  def header_add_rx_message(self, message):
    self.header_output_fp.write(
f"""\
    class {message.name} : public common_lib::CanRxMessage
    {{
      friend class {self.driver_name};
        
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
      self.header_output_fp.write(f"           uint32_t {signal.name} : {signal.length};\n")
    self.header_output_fp.write(f"        }} data_;\n    }};\n\n") 

  def create_header_file(self):
    self.header_add_driver_header()    

    # Add all TX messages
    for message in self.sender_message_list:
      self.header_add_tx_message(message)   

    # Add all RX messages
    for message in self.receiver_message_list:
      self.header_add_rx_message(message)   

    self.header_add_driver_footer()  
  
  def source_write_header(self):
     self.source_output_fp.write(
f"""\
#include "../inc/{self.driver_name.lower()}.h"

using namespace std;
using namespace common_lib;
using namespace driver_lib;

""")

  def source_write_tx_contructors(self):
    # Add TX constructors
    self.source_output_fp.write("""\
// =====================================================
// TX Constructors
""")
    for message in self.sender_message_list:
      self.source_output_fp.write(f"""\
{self.driver_name}::{message.name}::{message.name}(
    const uint32_t &_can_id,
    const uint8_t &_channel,
    const uint8_t &_frame_type,
    const uint32_t &_cycle_time)
    : CanTxMessage(_can_id, _channel, _frame_type, _cycle_time) data_{{}}
{{
}}
 
""")             

  def source_write_tx_destructors(self):
    # Add TX destructors
    self.source_output_fp.write("""\
// =====================================================
// TX Destructors 
""")
    for message in self.sender_message_list:
      self.source_output_fp.write(f"""\
{self.driver_name}::{message.name}::~{message.name}()
{{
}}
        
""")             

  def source_write_tx_handlers(self):
    # Add Transmit handler
    self.source_output_fp.write("""\
// =====================================================
// Transmit Handlers 
""")
    for message in self.sender_message_list:
        self.source_output_fp.write(f"""\
{self.driver_name}::{message.name}::set_data()
{{
    {message.name.lower()}_t buffer = data_;
    memcpy(can_fram.data, &buffer, sizeof({message.name.lower()}_t));
}}
        
""")             

  def source_write_rx_constructors(self):
    # Add RX constructors
    self.source_output_fp.write("""\
// =====================================================
// RX Constructors
""")
    for message in self.sender_message_list:
      self.source_output_fp.write(f"""\
{self.driver_name}::{message.name}::{message.name}(
    const uint32_t &_can_id,
    const uint8_t &_channel,
    const uint8_t &_frame_type,
    const uint32_t &_timeout)
    : CanRxMessage(_can_id, _channel, _frame_type, _timeout) data_{{}}
{{
}}
        
""")             

  def source_write_rx_destructors(self):
    self.source_output_fp.write("""\
// =====================================================
// RX Destructors 
""")
    for message in self.sender_message_list:
      self.source_output_fp.write(
f"""\
{self.driver_name}::{message.name}::{message.name}()
{{
}}
        
""")             


  def source_write_rx_handlers(self):
    self.source_output_fp.write("""\
// =====================================================
// RX handlers 
""")
    for message in self.sender_message_list:
      self.source_output_fp.write(
f"""\
void {self.driver_name}::{message.name}::receive_handler(const can_word_t *data)
{{
  memcpy(&data_, data, sizeof({message.name}_t);
}}
        
""")             

  def create_device_constructor(self):
    self.source_output_fp.write(
f"""// =====================================================
// Device constructor 
{self.driver_name}::{self.driver_name}(const uint8_t &_channel):\n""")

    for message in self.sender_message_list:
      self.source_output_fp.write(
f"""      {message.name.lower()}_({message.name.upper()}_ID, _channel, IO_CAN_EXT_FRAME, _TIMEOUT),\n""")
    for message in self.receiver_message_list:
      self.source_output_fp.write(
f"""      {message.name.lower()}_({message.name.upper()}_ID, _channel, IO_CAN_EXT_FRAME, _CYCLE_TIME,\n""")
    self.source_output_fp.write(f"""\
{{
}}

""")

  def create_device_destructor(self):
    self.source_output_fp.write(
f"""// =====================================================
// Device destructor
{self.driver_name}::~{self.driver_name}()\n{{\n}}\n\n""")
  
  def source_write_setters(self):
    self.source_output_fp.write(
f"""// =====================================================
// Setters\n""")
    for message in self.sender_message_list:
      for signal in message.signals:
        self.source_output_fp.write(
f"""void {self.driver_name}::{signal.name}(const {self.var_enum_list[signal.dbc.attributes['CG_VarType'].value]} &value)
{{
  {message.name.lower()}_.data_.{signal.name} = value;
}}

""")

  def source_write_getters(self):
    self.source_output_fp.write(
f"""// =====================================================
// Getters\n""")
    for message in self.receiver_message_list:
      for signal in message.signals:
        self.source_output_fp.write(
f"""{self.var_enum_list[signal.dbc.attributes['CG_VarType'].value]} {self.driver_name}::{signal.name}()
{{
  return {message.name.lower()}.data_.{signal.name};
}}

""")

  def create_source_file(self):
    self.source_write_header()

    self.source_write_tx_contructors()
    self.source_write_tx_destructors()
    self.source_write_tx_handlers()

    self.source_write_rx_constructors()
    self.source_write_rx_destructors()
    self.source_write_rx_handlers()

    self.create_device_constructor()
    self.create_device_destructor()

    self.source_write_setters()
    self.source_write_getters()
