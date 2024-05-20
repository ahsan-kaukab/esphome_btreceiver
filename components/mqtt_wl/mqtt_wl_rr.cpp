#include "mqtt_wl_rr.h"
#include "esphome/core/log.h"
#include "esphome/core/application.h"
#include "esphome/core/helpers.h"
#include <ArduinoJson.h>

namespace esphome {
namespace bthome_receiver_base {

static const char *TAG = "mqtt_wl_rr";

void mqtt_wl_rr::setup() {
    ESP_LOGCONFIG(TAG, "Setting up mqtt_wl_rr...");
    preferences_.begin("ble_wl", false);
    load_whitelist();
}

void mqtt_wl_rr::dump_config() {
    ESP_LOGCONFIG(TAG, "mqtt_wl_rr:");
    ESP_LOGCONFIG(TAG, "  Component Name: %s", component_name_.c_str());
    ESP_LOGCONFIG(TAG, "  MQTT Topic: %s", mqtt_topic_.c_str());

    for (const auto &entry : whitelist_) {
        ESP_LOGCONFIG(TAG, "  Whitelist Entry: %s - %s - %s",
                      entry.desc.c_str(), entry.mac.c_str(), entry.type.c_str());
    }
}

void mqtt_wl_rr::on_mqtt_message(const std::string &topic, const std::string &payload) {
    if (topic == mqtt_topic_) {
        ESP_LOGD(TAG, "Received MQTT message on topic: %s", topic.c_str());
        parse_whitelist_json(payload);
    }
}

void mqtt_wl_rr::save_whitelist() {
    DynamicJsonDocument doc(1024);
    JsonArray wl_array = doc.createNestedArray("wl");
    for (const auto &entry : whitelist_) {
        JsonObject obj = wl_array.createNestedObject();
        obj["desc"] = entry.desc;
        obj["mac"] = entry.mac;
        obj["type"] = entry.type;
    }

    std::string json_str;
    serializeJson(doc, json_str);
    preferences_.putString("whitelist", json_str.c_str());
}

void mqtt_wl_rr::load_whitelist() {
    std::string json_str = preferences_.getString("whitelist", "");
    if (!json_str.empty()) {
        parse_whitelist_json(json_str);
    }
}

void mqtt_wl_rr::parse_whitelist_json(const std::string &json_str) {
    DynamicJsonDocument doc(1024);
    auto error = deserializeJson(doc, json_str);
    if (error) {
        ESP_LOGE(TAG, "Failed to parse JSON: %s", error.c_str());
        return;
    }

    auto wl_array = doc["ble"]["wl"].as<JsonArray>();
    whitelist_.clear();
    for (JsonObject obj : wl_array) {
        WhitelistEntry entry;
        entry.desc = obj["desc"].as<std::string>();
        entry.mac = obj["mac"].as<std::string>();
        entry.type = obj["type"].as<std::string>();
        whitelist_.emplace_back(std::move(entry));
    }

    save_whitelist();
}

}  // namespace bthome_receiver_base
}  // namespace esphome
