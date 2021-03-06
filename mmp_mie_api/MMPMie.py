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
from mupif import Field
from mupif import PropertyID, FieldID
from mupif import ValueType
from mupif.Application import Application
from mupif.Property import Property
from .mie import mieDatabase

import pandas as pd
import numpy as np
import initialConfiguration as initConf
import objID

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
            [(PropertyID.PID_RefractiveIndex, 1.0, 1.0)],
            names=['propertyID', 'objectID', 'tstep'])
        self.properties = pd.Series(index=idx, dtype=Property)

        # Fields
        # Key should be in form of tuple (fieldID, tstep)
        idxf = pd.MultiIndex.from_tuples(
            [(FieldID.FID_Thermal_absorption_volume, 1.0)],
            names=['fieldID', 'tstep'])
        self.fields = pd.Series(index=idxf, dtype=Field.Field)

        self.mieThread = None
        self.wavelengths = None
        self.crossSections = None
        self.invCDF = None

        #############################
        # Empty old properties
        self.properties.drop(self.properties.index, inplace=True)
        # Empty old fields
        self.fields.drop(self.fields.index, inplace=True)

        # Initial values

        # User must set these 2 properties for other particle
        # types in top-level
        # simulation script !
        scatCross = Property(value=0,
                             propID=PropertyID.PID_ScatteringCrossSections,
                             valueType=ValueType.Vector,
                             time=0.0,
                             units=None,
                             objectID=objID.OBJ_PARTICLE_TYPE_1)

        invPhase = Property(value=0,
                            propID=PropertyID.PID_InverseCumulativeDist,
                            valueType=ValueType.Vector,
                            time=0.0,
                            units=None,
                            objectID=objID.OBJ_PARTICLE_TYPE_1)
        # Refractive index of particle
        v = 1.83
        nr = Property(value=v,
                      propID=PropertyID.PID_RefractiveIndex,
                      valueType=ValueType.Scalar,
                      time=0.0,
                      units=None,
                      objectID=objID.OBJ_PARTICLE_TYPE_1)

        # Refractive index of host material
        vh = 1.55
        nrh = Property(value=vh,
                      propID=PropertyID.PID_RefractiveIndex,
                      valueType=ValueType.Scalar,
                      time=0.0,
                      units=None,
                      objectID=objID.OBJ_CONE)
        #NEW PROPERTIES FROM MiM: .........
        Mu = 2.35137
        Sigma = 0.627218
        #p_max = 35.0
        #p_min = 1.0
        #p_num = 50
        #w_max = 1100.0
        #w_min = 100.0
        #w_num = 1001
     
        mup = Property(value=Mu, propID=PropertyID.PID_ParticleMu, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

        sigmap = Property(value=Sigma, propID=PropertyID.PID_ParticleSigma, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)
        """
        maxp = Property(value=p_max, propID=PropertyID.PID_Particle_max, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

        minp = Property(value=p_min, propID=PropertyID.PID_Particle_min, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

        nump = Property(value=p_num, propID=PropertyID.PID_Particle_n, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

        maxw = Property(value=w_max, propID=PropertyID.PID_Wavelen_max, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

        minw = Property(value=w_min, propID=PropertyID.PID_Wavelen_min, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)

        numw = Property(value=w_num, propID=PropertyID.PID_Wavelen_n, valueType=ValueType.Scalar, time=0.0, units=None, objectID=objID.OBJ_PARTICLE_TYPE_1)
        """
        key = (mup.getPropertyID(), mup.getObjectID(), 0)
        self.properties.loc[key] = mup
        key = (sigmap.getPropertyID(), sigmap.getObjectID(), 0)
        self.properties.loc[key] = sigmap
        """
        key = (maxp.getPropertyID(), maxp.getObjectID(), 0)
        self.properties.loc[key] = maxp
        key = (minp.getPropertyID(), minp.getObjectID(), 0)
        self.properties.loc[key] = minp
        key = (nump.getPropertyID(), nump.getObjectID(), 0)
        self.properties.loc[key] = nump
        key = (maxw.getPropertyID(), maxw.getObjectID(), 0)
        self.properties.loc[key] = maxw
        key = (minw.getPropertyID(), minw.getObjectID(), 0)
        self.properties.loc[key] = minw
        key = (numw.getPropertyID(), numw.getObjectID(), 0)
        self.properties.loc[key] = numw
        """
        #End of new properties from MiM..............

        key = (nr.getPropertyID(), nr.getObjectID(), 0)
        self.properties.loc[key] = nr
        key = (nrh.getPropertyID(), nrh.getObjectID(), 0)
        self.properties.loc[key] = nrh
        key = (scatCross.getPropertyID(), scatCross.getObjectID(), 0)
        self.properties.loc[key] = scatCross
        key = (invPhase.getPropertyID(), invPhase.getObjectID(), 0)
        self.properties.loc[key] = invPhase
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
        key = (field.getPropertyID(), field.getTime())
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
        if propID not in self.properties.index:
            raise APIError.APIError('Unknown property ID')

        if key not in self.properties.index:
            raise Exception('Not implemented')
        else:
            prop = self.properties[key]

        # Check pyro registering if applicaple
        # if hasattr(self, '_pyroDaemon') and not hasattr(prop, '_PyroURI'):
        #    uri = self._pyroDaemon.register(prop)
        #    prop._PyroURI = uri

        return(prop)

    def setProperty(self, newProp, objectID=0):
        """
        Register given property in the application

        :param Property property: Setting property
        :param int objectID: Identifies object/submesh on which property is
               evaluated (optional, default 0)
        """

        # Set the new property to container
        key = (newProp.getPropertyID(), newProp.getObjectID(), newProp.time)
        self.properties[key] = newProp

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

        # tstep is needed in _startmieProcess to get the Properties
        params = {'tstep': tstep}

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

    def getApplicationSignature(self):
        """
        :return: Returns the application identification
        :rtype: str
        """
        return("MMP-Mie@" + socket.gethostbyaddr(socket.gethostname())[0]
               + " version 0.1")

    def getAPIVersion(self):
        """
        :return: Returns the supported API version
        :rtype: str, int
        """
        # TODO: API version support?? How
        return('1.0', 1)

    def terminate(self):
        """
        Terminates the application.
        """
        if self.pyroDaemon:
            self.pyroDaemon.shutdown()

    def _startMieProcess(self, **kwargs):

        tstep = kwargs['tstep']

        # parameters moved from solveStep() to here: (MiM)
        # p* and w* are constant, make sure mmpraytracer.py has the same w* !
        p_max = 35.0
        p_min = 1.0#3.0
        p_num = 50#10

        w_max = 1100.0
        w_min = 100.0
        w_num = 1001#10
        """
        p_max = self.getProperty(PropertyID.PID_Particle_max, 0, objID.PARTICLE_TYPE_1).getValue()
        p_min = self.getProperty(PropertyID.PID_Particle_min, 0, prop.getObjectID()).getValue()
                    p_num = self.getProperty(PropertyID.PID_Particle_n, 0, prop.getObjectID()).getValue()
                    w_max = self.getProperty(PropertyID.PID_Wavelen_max, 0, prop.getObjectID()).getValue()
                    w_min = self.getProperty(PropertyID.PID_Wavelen_min, 0, prop.getObjectID()).getValue()
                    w_num = self.getProperty(PropertyID.PID_Wavelen_n, 0, prop.getObjectID()).getValue()
        """

        # Host medium refractive index
        #key = (PropertyID.PID_RefractiveIndex, objID.OBJ_CONE, tstep)
        #key = (PropertyID.PID_RefractiveIndex, 0, objID.OBJ_CONE)
        n_s = self.getProperty(PropertyID.PID_RefractiveIndex, 0, objID.OBJ_CONE).getValue()
        #n_s = self.properties[key].getValue()
        #n_s = 1.55

        #waves = np.linspace(w_min, w_max, w_num)

        if PropertyID.PID_RefractiveIndex in\
                self.properties.index.get_level_values('propertyID'):

            pris = self.properties.xs(
                (PropertyID.PID_RefractiveIndex, 0),
                level=('propertyID', 'tstep'))


            for i, prop in pris.iteritems():

                if prop.getObjectID() is not objID.OBJ_CONE:
                    # Particle refractive index
                    #key = (PropertyID.PID_RefractiveIndex,
                           #prop.getObjectID(),
                           #0)#tstep)
                    #n_p = self.properties[key].getValue()
                    n_p = self.getProperty(PropertyID.PID_RefractiveIndex, 0, prop.getObjectID()).getValue()
                    print("n_p, objID: ", n_p, prop.getObjectID())
                    #n_p = 1.83

                    # log mean in microns
                    #mu = 2.35137#3
                    mu = self.getProperty(PropertyID.PID_ParticleMu, 0, prop.getObjectID()).getValue()
                    # log standard deviation in microns
                    #sigma = 0.627218#0.6
                    sigma = self.getProperty(PropertyID.PID_ParticleSigma, 0, prop.getObjectID()).getValue()

                    
       

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

                    ######

                    # Mie database
                    mieDB = mieDatabase.MieDatabase()
                    # Get parameters
                    fname = mieDB.mieParameters(**params)  # **kwargs)
                    # Reload parameters to file
                    f = h5py.File(fname, 'r')
                    self.wavelengths = f['wavelengths'][:]
                    self.crossSections = f['particleData'][
                        '0']['crossSections'][:]
                    self.invCDF = f['particleData']['0']['inverseCDF'][:]

                    key = (PropertyID.PID_ScatteringCrossSections,
                           prop.getObjectID(),
                           0)

                    self.properties[key].value = self.crossSections

                    key = (PropertyID.PID_InverseCumulativeDist,
                           prop.getObjectID(),
                           0)

                    self.properties[key].value = self.invCDF
