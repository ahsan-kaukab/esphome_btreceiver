import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import mqtt
from esphome.const import CONF_ID, CONF_NAME

DEPENDENCIES = ['mqtt']
AUTO_LOAD = ['mqtt']

CONF_MAC_ADDRESS = 'mac_address'
CONF_MQTT_TOPIC = 'mqtt_topic'
CONF_COMPONENT_NAME = 'component_name'

mqtt_wl_rr_ns = cg.esphome_ns.namespace('mqtt_wl_rr')
MQTTWLRRComponent = mqtt_wl_rr_ns.class_('MQTTWLRRComponent', cg.Component, mqtt.MQTTClientComponent)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(MQTTWLRRComponent),
    cv.Required(CONF_COMPONENT_NAME): cv.string,
    cv.Required(CONF_MQTT_TOPIC): cv.string,
    cv.Optional(CONF_MAC_ADDRESS): cv.All(cv.ensure_list(cv.string), cv.Length(min=1)),
}).extend(cv.COMPONENT_SCHEMA)

def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    cg.add(var.set_component_name(config[CONF_COMPONENT_NAME]))
    cg.add(var.set_mqtt_topic(config[CONF_MQTT_TOPIC]))
    if CONF_MAC_ADDRESS in config:
        for mac in config[CONF_MAC_ADDRESS]:
            cg.add(var.add_mac_address(mac))
    yield cg.register_component(var, config)
    yield mqtt.register_mqtt_component(var, config)
