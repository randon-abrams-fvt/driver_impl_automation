#ifndef __eBTM_H_
#define __eBTM_H_

#include <can_service.h>
#include <stddef.h>
#include "J1939/

namespace driver_lib
{
class eBTM
{
  class EbtmStatus3 : public common_lib::CanRxMessage
  {
      friend class eBTM;
      
    public:
      EbtmStatus3(
        const uint32_t &_can_id,
        const uint8_t &_channel,
        const uint8_t &_frame_type,
        const uint32_t &_cycle_time);
      
      ~EbtmStatus3();

      virtual void receive_handler(const common_lib::can_word_t *data) override;
    
    private:
      struct ebtmstatus3_t
      {
        uint32_t  POWER_CONS_HVH : 16;
        uint32_t  POWER_CONS_HYPER : 16;
        uint32_t  POWER_LIMIT_CALC : 16;
      } data_;
   };

  class EbtmStatus2 : public common_lib::CanRxMessage
  {
      friend class eBTM;
      
    public:
      EbtmStatus2(
        const uint32_t &_can_id,
        const uint8_t &_channel,
        const uint8_t &_frame_type,
        const uint32_t &_cycle_time);
      
      ~EbtmStatus2();

      virtual void receive_handler(const common_lib::can_word_t *data) override;
    
    private:
      struct ebtmstatus2_t
      {
        uint32_t  EBTM_STM : 4;
        uint32_t  DETECTED_CONFIGURATION : 2;
        uint32_t  COOLING_AVAILBLE : 1;
        uint32_t  HEATING_AVAILBLE : 1;
        uint32_t  DETECTED_CAN_PROTOCOL : 1;
        uint32_t  FAN_1_SPEED : 8;
        uint32_t  FAN_2_SPEED : 8;
        uint32_t  PUMP_EXTERNAL_SPEED : 8;
        uint32_t  PUMP_INTERNAL_SPEED : 8;
        uint32_t  COOLANT_TEMP : 8;
      } data_;
   };

  class EbtmStatus1 : public common_lib::CanRxMessage
  {
      friend class eBTM;
      
    public:
      EbtmStatus1(
        const uint32_t &_can_id,
        const uint8_t &_channel,
        const uint8_t &_frame_type,
        const uint32_t &_cycle_time);
      
      ~EbtmStatus1();

      virtual void receive_handler(const common_lib::can_word_t *data) override;
    
    private:
      struct ebtmstatus1_t
      {
        uint32_t  eBTM_Hyper_Status : 3;
        uint32_t  eBTM_CAN_Hyper_Timeout : 1;
        uint32_t  eBTM_DCDC_Status : 2;
        uint32_t  eBTM_CAN_DCDC_Timeout : 1;
        uint32_t  eBTM_WP_INT_Status : 2;
        uint32_t  eBTM_LIN_WP_INT_Timeout : 1;
        uint32_t  eBTM_WP_EXT_Status : 2;
        uint32_t  eBTM_CAN_WP_EXT_Timeout : 1;
        uint32_t  eBTM_HVH_Status : 2;
        uint32_t  eBTM_LIN_HVH_Timeout : 1;
        uint32_t  eBTM_FAN1_Status : 2;
        uint32_t  eBTM_LIN_FAN1_Timeout : 1;
        uint32_t  eBTM_FAN2_Status : 2;
        uint32_t  eBTM_LIN_FAN2_Timeout : 1;
        uint32_t  eBTM_HV_UnderVoltage : 1;
        uint32_t  eBTM_HV_OverVoltage : 1;
        uint32_t  eBTM_LV_UnderVoltage : 1;
        uint32_t  eBTM_LV_OverVoltage : 1;
        uint32_t  eBTM_VDD12_UnderVoltage : 1;
        uint32_t  eBTM_VDD12_OverVoltage : 1;
        uint32_t  Coolant_Level_Status : 1;
        uint32_t  STC_sensor_status : 1;
        uint32_t  eBTM_ECU_Error : 1;
      } data_;
   };

  class TmsCommand : public common_lib::CanTxMessage
  {
      friend class eBTM;
      
    public:
      TmsCommand(
        const uint32_t &_can_id,
        const uint8_t &_channel,
        const uint8_t &_frame_type,
        const uin32_t &_cycle_time);
      
      ~TmsCommand();

      virtual void set_data() override;
    
    private:
      struct TmsCommand
      {
      uint32_t  ThermSysStrtReq1_J1993 : 2;
      uint32_t  PackNameThermReq1_J1993 : 5;
      uint32_t  EnaCoolgHeatgBatFlag_J1993 : 2;
      uint32_t  TAct_J1993 : 11;
      uint32_t  TSetPoint_J1993 : 11;
     } data_;
  };

  class TmsStatus : public common_lib::CanRxMessage
  {
      friend class eBTM;
      
    public:
      TmsStatus(
        const uint32_t &_can_id,
        const uint8_t &_channel,
        const uint8_t &_frame_type,
        const uint32_t &_cycle_time);
      
      ~TmsStatus();

      virtual void receive_handler(const common_lib::can_word_t *data) override;
    
    private:
      struct tmsstatus_t
      {
        uint32_t  ThermMngtSysSLIInpPwr : 16;
        uint32_t  ThermMngtSysHv : 16;
        uint32_t  ThermMngtSysCmpr : 8;
        uint32_t  ThermMngtSysRel : 8;
        uint32_t  ThermMngtSysHeatrSts : 2;
        uint32_t  ThermMngtSysHVILSts : 2;
        uint32_t  ThermMngtSysMode : 4;
        uint32_t  ThermMngtSysCooltLvl : 2;
      } data_;
   };

