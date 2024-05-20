#include "esphome.h"
#include "esphome/components/mqtt/mqtt_client.h"

#define USE_MQTT

namespace esphome {
namespace mqtt_wl_rr {

class MQTTWLRRComponent : public Component, public MQTTClientComponent {
 public:
  void setup() override;
  void loop() override;

  void set_component_name(const std::string &name) { component_name_ = name; }
  void set_mqtt_topic(const std::string &topic) { mqtt_topic_ = topic; }
  void add_mac_address(const std::string &mac_address) { mac_addresses_.push_back(mac_address); }

 protected:
  std::string component_name_;
  std::string mqtt_topic_;
  std::vector<std::string> mac_addresses_;

  void on_mqtt_message(const std::string &topic, const std::string &payload);
  void load_whitelist();
  void save_whitelist();
};

}  // namespace mqtt_wl_rr
}  // namespace esphome
