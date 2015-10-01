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

from mupif import Function, FunctionID
import numpy as np


class FunctionWithData(Function.Function):

    '''
    classdocs
    '''

    def __init__(self, funcID, data=None, objectID=0):
        """
        Initializes the function.

        :param FunctionID funcID: function ID, e.g.
        FuncID_ProbabilityDistribution
        :param int objectID: Optional ID of associated subdomain, default 0
        """
        super(Function.Function, self).__init__()  # call base

        self._fID = funcID
        self._objID = objectID
        self._data = data

    def evaluate(self, d):
        """
        Evaluates the function for given parameters packed as a dictionary.

        A dictionary is container type that can store any number of Python objects,
        including other container types. Dictionaries consist of pairs (called items)
        of keys and their corresponding values.

        Example: d={'x':(1,2,3), 't':0.005} initializes dictionary contaning tuple (vector) under 'x' key, double value 0.005 under 't' key. Some common keys: 'x': position vector 't': time

        :param dictionary d: Dictionaty containing function arguments (number and type depends on particular function)
        :return: Function value evaluated at given position and time
        :rtype: int, float, tuple
        """
        if self._data:
            return(self._data)
        else:
            return(np.NaN)

    def getID(self):
        """
        :return: Returns reciver's ID.
        :rtype: int
        """
        return(self._fID)

    def getObjectID(self):
        """
        :return: Returns receiver's object ID
        :rtype: int
        """
        return(self._objID)

    def setData(self, data):
        self._data = data
