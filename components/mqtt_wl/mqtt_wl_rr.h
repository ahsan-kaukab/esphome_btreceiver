#pragma once

#include "esphome.h"
#include <Preferences.h>

namespace esphome {
namespace mqtt_wl_rr {

class MQTTWLRRComponent : public Component, public mqtt::MQTTClientComponent {
 public:
  void setup() override;
  void loop() override;

  void set_component_name(const std::string &component_name) { component_name_ = component_name; }
  void set_mqtt_topic(const std::string &mqtt_topic) { mqtt_topic_ = mqtt_topic; }

  void add_mac_address(const std::string &mac_address);
  void save_whitelist_to_nvs();
  void load_whitelist_from_nvs();

 private:
  std::string component_name_;
  std::string mqtt_topic_;
  std::vector<std::string> mac_addresses_;
  Preferences preferences_;

  void on_mqtt_message(const std::string &topic, const std::string &payload);
  void parse_json(const std::string &json_str);
};

}  // namespace mqtt_wl_rr
}  // namespace esphome
