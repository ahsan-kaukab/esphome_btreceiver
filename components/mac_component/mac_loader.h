#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/esp32_ble_tracker/esp32_ble_tracker.h"
#include "esphome/components/bthome_base/bthome_parser.h"

#include "bthome_ble_receiver_hub.h"

#ifdef USE_ESP32

class MACLoader : public Component {
 public:
  void setup() override {
    load_mac_address("mac_address_1", mac_address_1_);
    load_mac_address("mac_address_2", mac_address_2_);
    load_mac_address("mac_address_3", mac_address_3_);
  }

  std::string get_mac_address_1() const { return mac_address_1_; }
  std::string get_mac_address_2() const { return mac_address_2_; }
  std::string get_mac_address_3() const { return mac_address_3_; }

 private:
  void load_mac_address(const char *key, std::string &mac_address) {
    preferences.begin("mac_prefs", false);
    mac_address = preferences.getString(key, "ff:ff:ff:ff:ff:ff").c_str();
    preferences.end();
  }

  Preferences preferences;
  std::string mac_address_1_;
  std::string mac_address_2_;
  std::string mac_address_3_;
};
#endif
