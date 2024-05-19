#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/esp32_ble_tracker/esp32_ble_tracker.h"
#include "esphome/components/bthome_base/bthome_parser.h"

#include "bthome_ble_receiver_hub.h"

#ifdef USE_ESP32

class MACLoader : public Component {
 public:
  void setup() override {
    // Load MAC addresses from NVS and set the global variables
    load_mac_address("mac_address_1", id(mac_address_1));
    load_mac_address("mac_address_2", id(mac_address_2));
    load_mac_address("mac_address_3", id(mac_address_3));
  }

 private:
  void load_mac_address(const char *key, Global<std::string> &mac_global) {
    preferences.begin("mac_prefs", false);
    std::string mac_address = preferences.getString(key, "ff:ff:ff:ff:ff:ff");
    preferences.end();
    mac_global = mac_address;
  }

  Preferences preferences;
};
#endif
