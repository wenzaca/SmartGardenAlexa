# -*- coding: utf-8 -*-

import json
# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK.
import logging
from datetime import date

import boto3
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name, get_slot_value
from ask_sdk_core.handler_input import HandlerInput

import phrase_enum

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_readings_from_dynamo():
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.Table('smartgarden_readings')
    startdate = date.today().isoformat()
    response = table.query(KeyConditionExpression='id = :id_smartgarden',
                           ExpressionAttributeValues={
                               ':id_smartgarden': 'id_smartgarden'},
                           ScanIndexForward=False,
                           Limit=1
                           )
    items = response['Items']
    n = 1  # get latest data
    data = items[:n]
    return data


def get_max_data_from_dynamo():
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    table = dynamodb.Table('smartgarden_maxdata')

    response = table.query(KeyConditionExpression='id = :id_smartgarden',
                           ExpressionAttributeValues={
                               ':id_smartgarden': 'id_smartgarden'},
                           ScanIndexForward=False,
                           Limit=1
                           )

    items = response['Items']
    n = 1  # get latest data
    data = items[:n]
    return data[0]


# Built-in Intent Handlers
class WaterPlantsHandler(AbstractRequestHandler):
    """Handler for Skill WaterPlants Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("WaterPlantsIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In WaterPlantsHandler")

        data = get_readings_from_dynamo()
        moisture = data[0]['Items']['moisture1']
        max_data = get_max_data_from_dynamo()
        moisture_max_data = max_data['Items'][0]['moisture']
        logger.info("The max data is {}, the latest measure of moisture was {}".format(moisture_max_data, moisture))
        if moisture > int(moisture_max_data):
            response_alexa = phrase_enum.TOO_WET_TO_WATER + moisture
        else:
            logger.info("M")
            client = boto3.client('iot-data', region_name='eu-west-1')

            # Change topic, qos and payload
            client.publish(
                topic='smartgarden/watering',
                qos=1,
                payload=json.dumps({"action": "ON", "requester": "Alexa"})
            )
            response_alexa = phrase_enum.WATERING_ON + ' <audio src="soundbank://soundlibrary/household/water/pour_water_01"/> '

        handler_input.response_builder.speak(response_alexa)
        return handler_input.response_builder.response


# Built-in Intent Handlers
class SensorReadingHandler(AbstractRequestHandler):
    """Handler for Skill SensorReading Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("SensorReadingIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SensorReadingHandler")

        data = get_readings_from_dynamo()[0]['Items']
        logger.info(data)
        response_alexa = ''
        sensor_slot_value = get_slot_value(handler_input=handler_input, slot_name="AWS.Slot.Sensor")

        if sensor_slot_value:
            slot_value = handler_input.request_envelope.request.intent.slots["AWS.Slot.Sensor"].resolutions.resolutions_per_authority[0].values[0].value.name
            response_alexa += phrase_enum.SENSOR_READING.format(slot_value, str(data[slot_value]))
            if 'temperature' in slot_value:
                response_alexa += '°C.'
            if 'moisture' in slot_value or 'humidity' in slot_value:
                response_alexa += '%.'

        else:
            for key, value in data.items():
                response_alexa += phrase_enum.SENSOR_READING.format(key, str(value))
                if 'temperature' in key:
                    response_alexa += '°C.'
                if 'moisture' in key or 'humidity' in key:
                    response_alexa += '%.'
                response_alexa += ' <break time="300ms"/> '

        handler_input.response_builder.speak(response_alexa)
        return handler_input.response_builder.response


# Built-in Intent Handlers
class ReadingMaxDataHandler(AbstractRequestHandler):
    """Handler for Skill SensorReading Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ReadingMaxDataIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ReadingMaxDataHandler")

        max_data = get_max_data_from_dynamo()
        moisture_max_data = max_data['Items'][0]
        response_alexa = phrase_enum.MAX_SENSOR_READING
        for key, value in moisture_max_data.items():
            response_alexa += phrase_enum.MAX_SENSOR_READING_PER_SENSOR.format(key, str(value))
            if 'temperature' in key:
                response_alexa += '°C.'
            elif 'moisture' or 'humidity' in key:
                response_alexa += '%.'
            response_alexa += ' <break time="300ms"/> '

        handler_input.response_builder.speak(response_alexa)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(phrase_enum.HELP_MESSAGE).ask(
            phrase_enum.HELP_REPROMPT).set_card(SimpleCard(
            phrase_enum.SKILL_NAME, phrase_enum.HELP_MESSAGE))
        return handler_input.response_builder.response


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")
        handler_input.response_builder.speak(phrase_enum.LAUNCH_REQUEST).ask(phrase_enum.LAUNCH_REQUEST)
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        handler_input.response_builder.speak(phrase_enum.STOP_MESSAGE)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent.
    AMAZON.FallbackIntent is only available in en-GB locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        handler_input.response_builder.speak(phrase_enum.FALLBACK_MESSAGE).ask(
            phrase_enum.FALLBACK_REPROMPT)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.info(exception)

        handler_input.response_builder.speak(phrase_enum.EXCEPTION_MESSAGE).ask(
            phrase_enum.HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# This handler acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.
sb = SkillBuilder()
sb.add_request_handler(WaterPlantsHandler())
sb.add_request_handler(SensorReadingHandler())
sb.add_request_handler(ReadingMaxDataHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# TODO: Uncomment the following lines of code for request, response logs.
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

handler = sb.lambda_handler()
