#include "mqtt_wl_rr.h"
#include "esphome/core/log.h"

namespace esphome {
namespace mqtt_wl_rr {

static const char *TAG = "mqtt_wl_rr";

void MQTTWLRRComponent::setup() {
  ESP_LOGD(TAG, "Setting up MQTTWLRRComponent...");
  this->subscribe(this->mqtt_topic_, &MQTTWLRRComponent::on_mqtt_message);
  this->load_whitelist();
}

void MQTTWLRRComponent::loop() {
  // Add any recurring functionality here
}

void MQTTWLRRComponent::on_mqtt_message(const std::string &topic, const std::string &payload) {
  ESP_LOGD(TAG, "Received MQTT message on topic %s: %s", topic.c_str(), payload.c_str());

  // Parse JSON payload
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, payload);
  if (error) {
    ESP_LOGE(TAG, "Failed to parse JSON: %s", error.c_str());
    return;
  }

  // Clear existing whitelist and populate new one
  this->mac_addresses_.clear();
  for (JsonVariant item : doc["ble"]["wl"].as<JsonArray>()) {
    std::string mac = item["mac"].as<std::string>();
    this->mac_addresses_.push_back(mac);
  }

  // Save new whitelist to NVS
  this->save_whitelist();
}

void MQTTWLRRComponent::load_whitelist() {
  // Implement NVS load logic here
  ESP_LOGD(TAG, "Loading whitelist from NVS...");
  // Placeholder: Simulate loading
  this->mac_addresses_ = {"00:11:22:33:44:55"};
}

void MQTTWLRRComponent::save_whitelist() {
  // Implement NVS save logic here
  ESP_LOGD(TAG, "Saving whitelist to NVS...");
  // Placeholder: Simulate saving
}

}  // namespace mqtt_wl_rr
}  // namespace esphome
