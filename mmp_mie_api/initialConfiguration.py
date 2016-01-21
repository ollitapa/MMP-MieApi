#
# Copyright 2015 VTT Technical Research Center of Finland
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from mupif import FunctionID, ValueType, Property, APIError
from .fieldIDs import FieldID
from .propertyIDs import PropertyID
import objID
import numpy as np


def checkRequiredFields(fields,  fID=FieldID):
    """
    Checks that all relevant fields for the simulation
    are present.
    """


def checkRequiredParameters(props, pID=PropertyID):
    """
    Checks that all relevant parameters for the simulation
    are present.
    """
    # TODO: Check!
    """
        PropertyID.PID_RefractiveIndex = 22
        PropertyID.PID_NumberOfRays = 23
        PropertyID.PID_LEDSpectrum = 24
        PropertyID.PID_ParticleNumberDensity = 25
        PropertyID.PID_ParticleRefractiveIndex = 26
    """
    #print("Property keys:")
    # for key in props.index:
    #        print(key)

    found = True

    if pID.PID_RefractiveIndex not in props.index:
        print("RefractiveIndex not found!")
        found = False
    if pID.PID_ParticleRefractiveIndex not in props.index:
        print("ParticleRefractiveIndex not found!")
        #found = False

    if not found:
        print("not all relevant parameters found!")
        #raise APIError.APIError("not all relevant properties found!")
