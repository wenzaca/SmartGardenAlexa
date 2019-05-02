from enum import Enum


class PhraseEnum(Enum):
    # =========================================================================================================================================
    # The items below this comment need to be edditable.
    # =========================================================================================================================================
    SKILL_NAME = "Smart Garden"
    HELP_MESSAGE = "You can tell me if you are not taking the bus today or tomorrow, " \
                   "or, you can say exit... What can I help you with?"
    HELP_REPROMPT = "What can I help you with?"
    STOP_MESSAGE = "Goodbye!"
    FALLBACK_MESSAGE = "The Smart Garden skill can't help you with that. It is used to" \
                       " take care of your garden. What can I help you with?"
    FALLBACK_REPROMPT = 'What can I help you with?'
    EXCEPTION_MESSAGE = "Sorry. I cannot help you with that."
    WATERING_ON = 'Watering turned on'
    TOO_WET_TO_WATER = 'Soil moisture is too wet, the value is '
    LAUNCH_REQUEST = "Welcome, you can say Hello or Help. Which would you like to try?"
