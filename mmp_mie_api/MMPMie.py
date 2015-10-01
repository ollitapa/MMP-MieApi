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

import socket
import sys
import threading
import os

import Pyro4
import h5py
from mupif import APIError
from mupif import Property, Field
from mupif import PropertyID, FunctionID, FieldID
from mupif import ValueType
from mupif.Application import Application
from .mie import mieDatabase

import pandas as pd
import initialConfiguration as initConf
import objID

from MieFunctions import FunctionWithData
import logging
import logging.config
from pkg_resources import resource_filename

# create logger
logging.config.fileConfig(resource_filename(__name__, 'logging.conf'),
                          disable_existing_loggers=False)
logger = logging.getLogger('mmpMIE')
#logger.debug('messages will be logged')
#logger.info('messages will be logged')
#logger.warn('messages will be logged')
#logger.error('messages will be logged')
#logger.critical('messages will be logged')


sys.excepthook = Pyro4.util.excepthook
Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle', 'serpent', 'json']
Pyro4.config.SERIALIZER = 'pickle'


### FID and PID definitions untill implemented at mupif###
PropertyID.PID_RefractiveIndex = 22
PropertyID.PID_NumberOfRays = 23
PropertyID.PID_LEDSpectrum = 24
PropertyID.PID_ParticleNumberDensity = 25
PropertyID.PID_ParticleRefractiveIndex = 26

FieldID.FID_HeatSourceVol = 33
##########################################################

### Function IDs until implemented at mupif ###
FunctionID.FuncID_ScatteringCrossSections = 55
FunctionID.FuncID_ScatteringInvCumulDist = 56
###############################################


class MMPMie(Application):

    """

    Micro model providing particle scattering functions
    by the mie-theory.

    """

    def __init__(self, file, workdir="."):
        """
        Constructor. Initializes the application.

        :param str file: Name of file
        """
        super(MMPMie, self).__init__(file, workdir)  # call base
        os.chdir(workdir)

        # Containers
        # Properties
        # Key should be in form of tuple (propertyID, objectID, tstep)
        idx = pd.MultiIndex.from_tuples(
            [(1.0, 1.0, 1.0)], names=['propertyID', 'objectID', 'tstep'])
        self.properties = pd.Series(index=idx, dtype=Property.Property)

        # Fields
        # Key should be in form of tuple (fieldID, tstep)
        idxf = pd.MultiIndex.from_tuples(
            [(1.0, 1.0)], names=['fieldID', 'tstep'])
        self.fields = pd.Series(index=idxf, dtype=Field.Field)

        self.mieThread = None
        self.wavelengths = None
        self.crossSections = None
        self.invCDF = None

        #############################
        # Initial values
        self._scatCrossFunc = FunctionWithData(
            funcID=FunctionID.FuncID_ScatteringCrossSections,
            objectID=0)

        self._invPhaseFunc = FunctionWithData(
            funcID=FunctionID.FuncID_ScatteringInvCumulDist,
            objectID=0)
        # Empty old properties
        self.properties.drop(self.properties.index, inplace=True)
        # Empty old fields
        self.fields.drop(self.fields.index, inplace=True)

        # Refractive index of particle
        v = 1.83
        nr = Property.Property(value=v,
                               propID=PropertyID.PID_ParticleRefractiveIndex,
                               valueType=ValueType.Scalar,
                               time=0.0,
                               units=None,
                               objectID=objID.OBJ_PARTICLE_TYPE_1)

        key = (nr.getPropertyID(), nr.getObjectID(), 0)
        self.properties.loc[key] = nr

        #############################

    def getField(self, fieldID, time):
        """
        Returns the requested field at given time. Field is identified
        by fieldID.

        :param FieldID fieldID: Identifier of the field
        :param float time: Target time

        :return: Returns requested field.
        :rtype: Field
        """
        # TODO: Interpolation between timesteps.

    def setField(self, field):
        """
        Registers the given (remote) field in application.

        :param Field field: Remote field to be registered by the application
        """
        # Set the new property to container
        key = (field.getPropertyID(), field.time)
        self.fields.set_value(key, field)

    def getProperty(self, propID, time, objectID=0):
        """
        Returns property identified by its ID evaluated at given time.

        :param PropertyID propID: property ID
        :param float time: Time when property should to be evaluated
        :param int objectID: Identifies object/submesh on which property is
        evaluated (optional, default 0)

        :return: Returns representation of requested property
        :rtype: Property
        """
        key = (propID, objectID, time)
        if key not in self.properties.index:
            # TODO: Implement property initialization
            print("NOT IMPLEMENTED")
            raise APIError.APIError('Unknown property ID')

        prop = self.properties[key]
        # Chek if object is registered to Pyro
        if hasattr(self, '_pyroDaemon') and not hasattr(prop, '_PyroURI'):
            uri = self._pyroDaemon.register(prop)
            prop._PyroURI = uri

        # TODO: Interpolation between timesteps.
        return(prop)

    def setProperty(self, newProp, objectID=0):
        """
        Register given property in the application

        :param Property property: Setting property
        :param int objectID: Identifies object/submesh on which property is
               evaluated (optional, default 0)
        """

        # Set the new property to container
        key = (newProp.getPropertyID(), objectID, newProp.time)
        self.properties[key] = newProp

    def getFunction(self, funcID, objectID=0):
        """
        Returns function identified by its ID

        :param FunctionID funcID: function ID
        :param int objectID: Identifies optional object/submesh on
        which property is evaluated (optional, default 0)

        :return: Returns requested function
        :rtype: Function
        """

        if (funcID == FunctionID.FuncID_ScatteringCrossSections):
            # Check for pyro
            f = self._scatCrossFunc
        elif(funcID == FunctionID.FuncID_ScatteringInvCumulDist):
            # Check for pyro
            f = self._invPhaseFunc
        else:
            raise APIError.APIError('Unknown function ID')

        # Check pyro registering if applicaple
        if hasattr(self, '_pyroDaemon') and not hasattr(f, '_PyroURI'):
            uri = self._pyroDaemon.register(f)
            f._PyroURI = uri

        return(f)

    def getMesh(self, tstep):
        """
        Returns the computational mesh for given solution step.

        :param TimeStep tstep: Solution step
        :return: Returns the representation of mesh
        :rtype: Mesh
        """
        return None

    def solveStep(self, tstep, stageID=0, runInBackground=False):
        """
        Solves the problem for given time step.

        Proceeds the solution from actual state to given time.
        The actual state should not be updated at the end, as this method
        could be
        called multiple times for the same solution step until the global
        convergence
        is reached. When global convergence is reached, finishStep is called
        and then
        the actual state has to be updated.
        Solution can be split into individual stages identified by optional
        stageID parameter.
        In between the stages the additional data exchange can be performed.
        See also wait and isSolved services.

        :param TimeStep tstep: Solution step
        :param int stageID: optional argument identifying solution stage
         (default 0)
        :param bool runInBackground: optional argument, defualt False. If True,
        the solution will run in background (in separate thread or remotely).

        """
        if self.mieThread:
            if self.mieThread.is_alive():
                return

        # Check params and fields
        initConf.checkRequiredParameters(self.properties, PropertyID)

        p_max = 35.0
        p_min = 3.0
        p_num = 10

        w_max = 1100.0
        w_min = 100.0
        w_num = 10

        #waves = np.linspace(w_min, w_max, w_num)

        n_p = 1.83
        n_s = 1.55
        # log mean in microns
        mu = 3
        # log standard deviation in microns
        sigma = 0.6

        params = {'n_particle': n_p,
                  'n_host': n_s,
                  'particle_mu': mu,
                  'particle_sigma': sigma,
                  'force_new': False,
                  'effective_model': True,
                  'wavelen_n': w_num,
                  'wavelen_max': w_max,
                  'wavelen_min': w_min,
                  'particle_n': p_num,
                  'particle_max': p_max,
                  'particle_min': p_min
                  }

        # Start thread to start Mie calculation
        self.mieThread = threading.Thread(target=self._startMieProcess,
                                          kwargs=params,
                                          group=None)
        self.mieThread.start()

        # Wait for process if applicaple
        if not runInBackground:
            self.mieThread.join()

    def wait(self):
        """
        Wait until solve is completed when executed in background.
        """
        if self.mieThread:
            self.mieThread.join()

    def isSolved(self):
        """
        :return: Returns true or false depending whether
                 solve has completed when executed in background.
        :rtype: bool
        """
        return(not self.mieThread.isAlive())

    def finishStep(self, tstep):
        """
        Called after a global convergence within a time step is achieved.

        :param TimeStep tstep: Solution step
        """

    def getCriticalTimeStep(self):
        """
        :return: Returns the actual (related to current state) critical time
         step increment
        :rtype: float
        """

    def getAssemblyTime(self, tstep):
        """
        Returns the assembly time related to given time step.
        The registered fields (inputs) should be evaluated in this time.

        :param TimeStep tstep: Solution step
        :return: Assembly time
        :rtype: float, TimeStep
        """

    def storeState(self, tstep):
        """
        Store the solution state of an application.

        :param TimeStep tstep: Solution step
        """

    def restoreState(self, tstep):
        """
        Restore the saved state of an application.
        :param TimeStep tstep: Solution step
        """

    def getApplicationSignature(self):
        """
        :return: Returns the application identification
        :rtype: str
        """
        return("MMP-Mie@" + socket.gethostbyaddr(socket.gethostname())[0]
               + " version 0.1")

    def terminate(self):
        """
        Terminates the application.
        """
        if self.pyroDaemon:
            self.pyroDaemon.shutdown()

    def _startMieProcess(self, **kwargs):
        # Mie database
        mieDB = mieDatabase.MieDatabase()
        # Get parameters
        fname = mieDB.mieParameters(**kwargs)
        # Reload parameters to file
        f = h5py.File(fname, 'r')
        self.wavelengths = f['wavelengths'][:]
        self.crossSections = f['particleData']['0']['crossSections'][:]
        self.invCDF = f['particleData']['0']['inverseCDF'][:]

        self._scatCrossFunc.setData(self.crossSections)
        self._invPhaseFunc.setData(self.invCDF)
