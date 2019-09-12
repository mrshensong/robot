# Copyright (c) 2018 Acroname Inc. - All Rights Reserved
#
# This file is part of the BrainStem (tm) package which is released under MIT.
# See file LICENSE or go to https://acroname.com for full license details.

"""
A module that provides defines and constants useful for working with the python
library.

"""

MODEL_USBSTEM = 4                        #: USBStem Model number
MODEL_ETHERSTEM = 5                      #: EtherStem Model number
MODEL_MTM_IOSERIAL = 13                  #: MTM-IO-Serial Model number
MODEL_MTM_PM_1 = 14                      #: MTM-PM-1 Model number
MODEL_MTM_ETHERSTEM = 15                 #: MTM EtherStem Model number
MODEL_MTM_USBSTEM = 16                   #: MTM USBStem Model number
MODEL_USBHUB_2X4 = 17                    #: USBHub 2x4 Model number
MODEL_MTM_RELAY = 18                     #: MTM-Relay Model Number
MODEL_USBHUB_3P = 19                     #: USBHub 3+ Model number
MODEL_MTM_DAQ_1 = 20                     #: MTM-DAQ-1 Model number
MODEL_USB_C_SWITCH = 21                  #: USBC-Switch Model number
MODEL_MTM_DAQ_2 = 22                     #: MTM-DAQ-2 Model number


def model_info(model):
    """ Get Model information.

        args:
            model (int): One of the model numbers, i.e from stem.system.getModel().

        return:
            str: Return a string containing model information.
    """
    if model == MODEL_USBSTEM:
        return "40 Pin USBStem module: Default module address is 2."
    elif model == MODEL_ETHERSTEM:
        return "40 Pin EtherStem module: Default module address is 2."
    elif model == MODEL_MTM_IOSERIAL:
        return "MTM IO Serial module: Default module address is 8."
    elif model == MODEL_MTM_PM_1:
        return "MTM 1 Channel Power module: Default module address is 6."
    elif model == MODEL_MTM_ETHERSTEM:
        return "MTM EtherStem module: Default module address is 4."
    elif model == MODEL_MTM_USBSTEM:
        return "MTM USBStem module: Default module address is 4."
    elif model == MODEL_USBHUB_2X4:
        return "Programmable 4 port USB Hub: Default module address is 6."
    elif model == MODEL_MTM_RELAY:
        return "MTM Relay module: Default module address is 12."
    elif model == MODEL_USBHUB_3P:
        return "Programmable 8+1 port USB 3.0 Hub: Default module address is 6."
    elif model == MODEL_MTM_DAQ_1:
        return "MTM DAQ module: Default module address is 10."
    elif model == MODEL_USB_C_SWITCH:
        return "Programmable USB Type-C Switch module: Default module address is 6."
    elif model == MODEL_MTM_DAQ_2:
        return "MTM DAQ module: Default module address is 14."
    else:
        return "Could not find model matching the value %d" % model


def model_name(model):
    """ Get Model Name.

            args:
                model (int): One of the model numbers, i.e from stem.system.getModel().

            return:
                str: Return a string containing model name.
        """
    if model == MODEL_USBSTEM:
        return "USBStem"
    elif model == MODEL_ETHERSTEM:
        return "EtherStem"
    elif model == MODEL_MTM_IOSERIAL:
        return "MTMIOSerial"
    elif model == MODEL_MTM_PM_1:
        return "MTMPM1"
    elif model == MODEL_MTM_ETHERSTEM:
        return "MTMEtherStem"
    elif model == MODEL_MTM_USBSTEM:
        return "MTMUSBStem"
    elif model == MODEL_USBHUB_2X4:
        return "USBHub2x4"
    elif model == MODEL_MTM_RELAY:
        return "MTMRelay"
    elif model == MODEL_USBHUB_3P:
        return "USBHub3p"
    elif model == MODEL_MTM_DAQ_1:
        return "MTMDAQ1"
    elif model == MODEL_USB_C_SWITCH:
        return "USBCSwitch"
    elif model == MODEL_MTM_DAQ_2:
        return "MTMDAQ2"
    else:
        return "Unknown"
