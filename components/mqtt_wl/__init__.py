import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import mqtt
from esphome.const import CONF_ID

DEPENDENCIES = ['mqtt']
AUTO_LOAD = ['mqtt']

CONF_MAC_ADDRESS = 'mac_address'
CONF_MQTT_TOPIC = 'mqtt_topic'
CONF_COMPONENT_NAME = 'component_name'

bthome_mqtt_wl_ns = cg.esphome_ns.namespace('bthome_mqtt_wl')
mqtt_wl_rr = bthome_mqtt_wl_ns.class_('mqtt_wl_rr', cg.Component)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(mqtt_wl_rr),
    cv.Required(CONF_COMPONENT_NAME): cv.string,
    cv.Optional(CONF_MQTT_TOPIC, default=''): cv.string,
}).extend(cv.COMPONENT_SCHEMA)

def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    cg.add(var.set_component_name(config[CONF_COMPONENT_NAME]))
    if config[CONF_MQTT_TOPIC]:
        cg.add(var.set_mqtt_topic(config[CONF_MQTT_TOPIC]))
    yield cg.register_component(var, config)
