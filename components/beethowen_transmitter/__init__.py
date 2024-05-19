"""
 Beethowen
 BTHome over ESPNow virtual sensors for ESPHome

 Author: Attila Farago
 """

from functools import partial
from esphome.cpp_generator import RawExpression
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.config_validation import hex_int_range, has_at_least_one_key
from esphome import automation
from esphome.components import binary_sensor, sensor
from esphome.const import CONF_ID, CONF_TRIGGER_ID
from esphome.core import CORE, HexInt, coroutine_with_priority
from esphome.components.bthome_base.const import (
    MEASUREMENT_TYPES_NUMERIC_SENSOR,
    MEASUREMENT_TYPES_BINARY_SENSOR,
    MEASUREMENT_TYPES_EVENT_SENSOR
)

CONF_BeethowenTransmitterHub_ID = "BeethowenTransmitterHub_ID"
CONF_MEASUREMENT_TYPE = "measurement_type"
CONF_CONNECT_PERSISTENT = "connect_persistent"
CONF_SENSORS = "sensors"
CONF_AUTO_SEND = "auto_send"
CONF_LOCAL_PASSKEY = "local_passkey"
CONF_EXPECTED_REMOTE_PASSKEY = "expected_remote_passkey"
CONF_SENSOR_SENSOR_ID = "sensor_id"
CONF_ON_SEND_STARTED = "on_send_started"
CONF_ON_SEND_FINISHED = "on_send_finished"
CONF_ON_SEND_FAILED = "on_send_failed"
CONF_RESTORE_FROM_FLASH = "restore_from_flash"
CONF_COMPLETE_ONLY = "complete_only"  # for send action
CONF_HAS_OUTSTANDING_MEASUREMENTS = "has_outstanding_measurements"
CONF_DEVICE_TYPE = "device_type"
CONF_EVENT_TYPE = "event_type"
CONF_DEVICE_EVENT_TYPE = "device_event_type"
CONF_HAS_VALUE = "has_value"
CONF_VALUE = "value"

CODEOWNERS = ["@afarago"]
DEPENDENCIES = []
AUTO_LOAD = ["bthome_base", "beethowen_base",
             "binary_sensor", "sensor", "preferences"]

beethowen_transmitter_ns = cg.esphome_ns.namespace("beethowen_transmitter")
BeethowenTransmitterHub = beethowen_transmitter_ns.class_(
    "BeethowenTransmitterHub", cg.Component
)
BeethowenTransmitterSensor = beethowen_transmitter_ns.class_(
    "BeethowenTransmitterSensor", cg.Component, sensor.Sensor
)
BeethowenTransmitterBinarySensor = beethowen_transmitter_ns.class_(
    "BeethowenTransmitterBinarySensor", cg.Component, binary_sensor.BinarySensor
)
SendStartedTrigger = beethowen_transmitter_ns.class_(
    "SendStartedTrigger", automation.Trigger.template()
)
SendFinishedTrigger = beethowen_transmitter_ns.class_(
    "SendFinishedTrigger", automation.Trigger.template(bool)
)
SendFailedTrigger = beethowen_transmitter_ns.class_(
    "SendFailedTrigger", automation.Trigger.template()
)
SendDataAction = beethowen_transmitter_ns.class_(
    "SendDataAction", automation.Action)
SendEventAction = beethowen_transmitter_ns.class_(
    "SendEventAction", automation.Action)


def validate_proxy_id(value):
    value = cv.string_strict(value)
    value = cv.Length(max=20)(value)
    return value


def create_check_measurement_type_fn(measurement_types):
    def validate_measurement_fn(value):
        if isinstance(value, int):
            return value
        try:
            return int(value)
        except ValueError:
            pass

        if not value in measurement_types:
            raise cv.Invalid(f"Invalid measurement type '{value}'!")

        return measurement_types[value]

    return validate_measurement_fn


validate_sensor_measurement_type = create_check_measurement_type_fn(
    MEASUREMENT_TYPES_NUMERIC_SENSOR
)
validate_binary_sensor_measurement_type = create_check_measurement_type_fn(
    MEASUREMENT_TYPES_BINARY_SENSOR
)

CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(BeethowenTransmitterHub),
            cv.Optional(CONF_CONNECT_PERSISTENT): cv.boolean,
            cv.Optional(CONF_AUTO_SEND): cv.boolean,
            cv.Optional(CONF_RESTORE_FROM_FLASH, default=True): cv.boolean,
            cv.Optional(CONF_LOCAL_PASSKEY): cv.hex_uint16_t,
            cv.Optional(CONF_EXPECTED_REMOTE_PASSKEY): cv.hex_uint16_t,
            cv.Optional(CONF_ON_SEND_STARTED): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(SendStartedTrigger),
                }
            ),
            cv.Optional(CONF_ON_SEND_FINISHED): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(SendFinishedTrigger),
                }
            ),
            cv.Optional(CONF_ON_SEND_FAILED): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(SendFailedTrigger),
                }
            ),
            cv.Optional(CONF_SENSORS): cv.All(
                cv.ensure_list(
                    cv.Any(
                        cv.Schema(
                            {
                                cv.GenerateID(): cv.declare_id(
                                    BeethowenTransmitterSensor
                                ),
                                cv.Required(
                                    CONF_MEASUREMENT_TYPE
                                ): validate_sensor_measurement_type,
                                cv.Required(CONF_SENSOR_SENSOR_ID): cv.use_id(
                                    sensor.Sensor
                                ),
                            }
                        ),
                        cv.Schema(
                            {
                                cv.GenerateID(): cv.declare_id(
                                    BeethowenTransmitterSensor
                                ),
                                cv.Required(
                                    CONF_MEASUREMENT_TYPE
                                ): validate_binary_sensor_measurement_type,
                                cv.Required(CONF_SENSOR_SENSOR_ID): cv.use_id(
                                    binary_sensor.BinarySensor
                                ),
                            }
                        ),
                    )
                )
            ),
        }
    ).extend(cv.COMPONENT_SCHEMA)
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    if CORE.is_esp8266:
        cg.add_library("ESP8266WiFi", None)
    elif CORE.is_esp32 and CORE.using_arduino:
        cg.add_library("WiFi", None)
    else:
        raise cv.Invalid("Beethowen is only supported on ESP cores.")

    if CONF_CONNECT_PERSISTENT in config:
        cg.add(var.set_connect_persistent(config[CONF_CONNECT_PERSISTENT]))
    if CONF_AUTO_SEND in config:
        cg.add(var.set_auto_send(config[CONF_AUTO_SEND]))
    if CONF_RESTORE_FROM_FLASH in config:
        cg.add(var.set_restore_from_flash(config[CONF_RESTORE_FROM_FLASH]))
    if CONF_LOCAL_PASSKEY in config:
        cg.add(var.set_local_passkey(HexInt(config[CONF_LOCAL_PASSKEY])))
    if CONF_EXPECTED_REMOTE_PASSKEY in config:
        cg.add(
            var.set_remote_expected_passkey(
                HexInt(config[CONF_EXPECTED_REMOTE_PASSKEY])
            )
        )

    def get_measurement_type_value_(measurement_type):
        if isinstance(measurement_type, dict):
            measurement_type = measurement_type[CONF_MEASUREMENT_TYPE]
        return measurement_type

    # presort sensors to speed up sending and skip re-sorting every time
    config_sensors = config.get(CONF_SENSORS, [])
    config_sensors.sort(
        key=lambda conf_item: get_measurement_type_value_(
            conf_item[CONF_MEASUREMENT_TYPE]
        )
    )

    # add sensors to config
    for config_item in config_sensors:
        sensor = await cg.get_variable(config_item[CONF_SENSOR_SENSOR_ID])

        measurement_type = get_measurement_type_value_(
            config_item[CONF_MEASUREMENT_TYPE]
        )

        cg.add(var.add_sensor(HexInt(measurement_type), sensor))

    for conf in config.get(CONF_ON_SEND_STARTED, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [], conf)
    for conf in config.get(CONF_ON_SEND_FINISHED, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(
            trigger, [(bool, CONF_HAS_OUTSTANDING_MEASUREMENTS)], conf
        )
    for conf in config.get(CONF_ON_SEND_FAILED, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [], conf)


@automation.register_action(
    "beethowen_transmitter.send",
    SendDataAction,
    cv.Any(
        cv.maybe_simple_value(
            {
                cv.GenerateID(): cv.use_id(BeethowenTransmitterHub),
                cv.Optional(CONF_COMPLETE_ONLY, default=True): cv.templatable(cv.boolean)
            },
            key=CONF_COMPLETE_ONLY),
        automation.maybe_simple_id(
            {
                cv.GenerateID(): cv.use_id(BeethowenTransmitterHub),
                cv.Optional(CONF_COMPLETE_ONLY): cv.templatable(cv.boolean)
            }
        )
    ),
)
async def beethowen_transmitter_send_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, paren)

    if CONF_COMPLETE_ONLY in config:
        cg.add(var.set_complete_only(config[CONF_COMPLETE_ONLY]))

    return var


def validate_device_event_type(config):
    if not isinstance(config, dict):
        raise cv.Invalid(f"Expecting a dictionary")

    if CONF_DEVICE_TYPE in config and CONF_EVENT_TYPE in config:
        lookup_value = config[CONF_DEVICE_TYPE] + "_" + config[CONF_EVENT_TYPE]
    else:
        lookup_value = config[CONF_DEVICE_EVENT_TYPE]

    if not lookup_value in MEASUREMENT_TYPES_EVENT_SENSOR:
        raise cv.Invalid(f"Invalid device event type '{lookup_value}'!")

    value_struct = MEASUREMENT_TYPES_EVENT_SENSOR[lookup_value]
    retval = HexInt(value_struct[CONF_DEVICE_EVENT_TYPE])

    has_value = value_struct[CONF_HAS_VALUE] if CONF_HAS_VALUE in value_struct else False
    if has_value and not CONF_VALUE in config:
        raise cv.Invalid(f"Device type with event type should have a value!")
    elif not has_value and CONF_VALUE in config:
        raise cv.Invalid(
            f"Device type with event type should not have a value!")

    config[CONF_DEVICE_EVENT_TYPE] = retval
    return config


@automation.register_action(
    "beethowen_transmitter.send_event",
    SendEventAction,
    cv.All(
        cv.Any(
            cv.Schema({
                cv.GenerateID(CONF_ID): cv.use_id(BeethowenTransmitterHub),
                cv.Required(CONF_DEVICE_TYPE): cv.string,
                cv.Required(CONF_EVENT_TYPE): cv.string,
                cv.Optional(CONF_VALUE): cv.uint8_t,
            }),
            cv.maybe_simple_value({
                cv.GenerateID(CONF_ID): cv.use_id(BeethowenTransmitterHub),
                cv.Required(CONF_DEVICE_EVENT_TYPE): cv.string,
            }, key=CONF_DEVICE_EVENT_TYPE)
        ),
        validate_device_event_type)
)
async def beethowen_transmitter_send_event_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, paren)

    if CONF_DEVICE_EVENT_TYPE in config:
        cg.add(var.set_device_type(
            HexInt(config[CONF_DEVICE_EVENT_TYPE] >> 8 & 0xff)))
        cg.add(var.set_event_type(
            HexInt(config[CONF_DEVICE_EVENT_TYPE] & 0xff)))
    if CONF_VALUE in config:
        cg.add(var.set_value(config[CONF_VALUE]))

    return var
