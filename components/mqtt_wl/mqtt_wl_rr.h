#pragma once

#include "esphome.h"
#include <Preferences.h>
#include <vector>

namespace esphome {
namespace bthome_receiver_base {

struct WhitelistEntry {
    std::string desc;
    std::string mac;
    std::string type;
};

class mqtt_wl_rr : public Component, public mqtt::MQTTClientComponent {
public:
    void setup() override;
    void dump_config() override;
    void on_mqtt_message(const std::string &topic, const std::string &payload) override;

    void set_component_name(const std::string &component_name) { component_name_ = component_name; }
    void set_mqtt_topic(const std::string &mqtt_topic) { mqtt_topic_ = mqtt_topic; }

private:
    std::vector<WhitelistEntry> whitelist_;
    std::string component_name_;
    std::string mqtt_topic_;
    Preferences preferences_;

    void save_whitelist();
    void load_whitelist();
    void parse_whitelist_json(const std::string &json_str);
};

}  // namespace bthome_receiver_base
}  // namespace esphome
