#include "mqtt_wl_rr.h"
#include "esphome.h"
#include "ArduinoJson.h"

namespace esphome {
namespace mqtt_wl_rr {

void MQTTWLRRComponent::setup() {
  ESP_LOGI("mqtt_wl_rr", "Setting up MQTTWLRRComponent...");

  // Load whitelist from NVS
  load_whitelist_from_nvs();

  // Set up MQTT subscription for whitelist updates
  mqtt::MQTTClientComponent::subscribe(mqtt_topic_, [this](const std::string &topic, const std::string &payload) {
    on_mqtt_message(topic, payload);
  });
}

void MQTTWLRRComponent::loop() {
  // Periodically check or handle tasks related to the MAC address whitelist
}

void MQTTWLRRComponent::add_mac_address(const std::string &mac_address) {
  mac_addresses_.push_back(mac_address);
}

void MQTTWLRRComponent::save_whitelist_to_nvs() {
  preferences_.begin("mac_prefs", false);
  preferences_.putUInt("num_mac", mac_addresses_.size());
  for (size_t i = 0; i < mac_addresses_.size(); ++i) {
    preferences_.putString("mac_" + String(i), mac_addresses_[i].c_str());
  }
  preferences_.end();
}

void MQTTWLRRComponent::load_whitelist_from_nvs() {
  preferences_.begin("mac_prefs", true);
  size_t num_mac = preferences_.getUInt("num_mac", 0);
  mac_addresses_.clear();
  for (size_t i = 0; i < num_mac; ++i) {
    mac_addresses_.push_back(preferences_.getString("mac_" + String(i), ""));
  }
  preferences_.end();
}

void MQTTWLRRComponent::on_mqtt_message(const std::string &topic, const std::string &payload) {
  ESP_LOGI("mqtt_wl_rr", "Received MQTT message: %s", payload.c_str());
  parse_json(payload);
}

void MQTTWLRRComponent::parse_json(const std::string &json_str) {
  StaticJsonDocument<1024> doc;
  DeserializationError error = deserializeJson(doc, json_str);
  if (error) {
    ESP_LOGE("mqtt_wl_rr", "Failed to parse JSON: %s", error.c_str());
    return;
  }

  if (!doc.containsKey("ble") || !doc["ble"].containsKey("wl")) {
    ESP_LOGE("mqtt_wl_rr", "Invalid JSON format");
    return;
  }

  auto wl = doc["ble"]["wl"];
  mac_addresses_.clear();
  for (JsonObject obj : wl.as<JsonArray>()) {
    mac_addresses_.push_back(obj["mac"].as<const char*>());
  }

  save_whitelist_to_nvs();
}

}  // namespace mqtt_wl_rr
}  // namespace esphome
