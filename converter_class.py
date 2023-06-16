import os
import cantools
import sys

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
        self.header_output_fp = open(f"{self.driver_name.lower()}.h","w")
      except:
        print("Unable to create output header file")

      try:
        self.source_output_fp = open(f"{self.driver_name.lower()}.cpp","w")
      except:
        print("Unable to create output source file")
    
  def header_add_driver_header(self):
    self.header_output_fp.write(
  f"""\
#ifndef __{self.driver_name}_H_
#define __{self.driver_name}_H_

#include <can_service.h>
#include <stddef.h>
#include "J1939/

namespace driver_lib
{{
class {self.driver_name}
{{
"""
  )

  def header_add_driver_footer(self):
    self.header_output_fp.write(
f"""\
  {self.driver_name}(const uint8_t &_channel);
  ~{self.driver_name}();
  
  //====================================================  
  // Setters
""")
  
    for message in self.message_list:
      if (len(message.signals) == 0) or ("FVT_ECU" not in message.senders):
        continue
      else:
        for signal in message.signals:
          self.header_output_fp.write(f"  void set_{signal.name}(const {self.var_enum_list[signal.dbc.attributes['CG_VarType'].value]} &value);\n")


    self.header_output_fp.write(
f"""
  private:
""")

    for message in self.message_list:
      if (len(message.signals) == 0) or ("FVT_ECU" not in message.senders):
        continue
      else:
          self.header_output_fp.write(f"    {message.name} {message.name.lower()}_;\n")

    for message in self.message_list:
      if (len(message.signals) == 0) or ("FVT_ECU" not in message.receivers):
        continue
      else:
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
          const uin32_t &_cycle_time);
        
        ~{message.name}();

        virtual void set_data() override;
      
      private:
        struct {message.name}
        {{
""")
     
    for signal in message.signals:
      self.header_output_fp.write(f"        uint32_t  {signal.name} : {signal.length};\n")
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
      self.header_output_fp.write(f"          uint32_t  {signal.name} : {signal.length};\n")
    self.header_output_fp.write(f"        }} data_;\n    }};\n\n") 

  def create_header_file(self):
    self.header_add_driver_header()    

    # Add all TX messages
    for message in self.message_list:
      if len(message.signals) == 0:
        continue
      else:
        if "FVT_ECU" in message.senders:
          self.header_add_tx_message(message)   
        else:
          continue

    # Add all RX messages
    for message in self.message_list:
      if len(message.signals) == 0:
        continue
      else:
        if "FVT_ECU" in message.receivers:
          self.header_add_rx_message(message)
        else:
          continue
    
    self.header_add_driver_footer()

  def create_source_file(self):
    # Add TX constructors
    self.source_output_fp.write("""\
// =====================================================
// TX Constructors
""")
    for message in self.message_list:
      if "FVT_ECU" in message.senders:
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
    # Add TX destructors
    self.source_output_fp.write("""\
// =====================================================
// TX Destructors 
""")
    for message in self.message_list:
      if "FVT_ECU" in message.senders:
        self.source_output_fp.write(f"""\
{self.driver_name}::{message.name}::~{message.name}()
{{
}}
        
""")             
    # Add Transmit handler
    self.source_output_fp.write("""\
// =====================================================
// Transmit Handlers 
""")
    for message in self.message_list:
      if "FVT_ECU" in message.senders:
        self.source_output_fp.write(f"""\
{self.driver_name}::{message.name}::set_data()
{{
    {message.name.lower()}_t buffer = data_;
    memcpy(can_fram.data, &buffer, sizeof({message.name.lower()}_t));
}}
        
""")             

    # Add RX constructors
    self.source_output_fp.write("""\
// =====================================================
// RX Constructors
""")
    for message in self.message_list:
      if "FVT_ECU" in message.receivers:
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
    # Add RX destructors
    # Add Receive handler

    # Add device contructor
    # Add device destructor

    # Add setters 
    # Add getters
