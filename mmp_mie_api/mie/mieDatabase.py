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

import os
import sqlite3

from scipy.stats import lognorm

import numpy as np
import mieGenerator as mie


fname = 'mie_database.db'
baseDir = 'MieDataFiles'


class MieDatabase():

    def __init__(self):
        pass
        # os.remove(fname)
        if not os.path.isdir(baseDir):
            os.mkdir(baseDir)
        if not os.path.isfile(fname):
            self.conn = sqlite3.connect(fname)
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                '''create table data(n_particle_r,n_particle_j,n_host,
                particle_mu,particle_sigma,effective_model,wavelen_n,
                wavelen_max,wavelen_min,particle_n,particle_max,
                particle_min,filename)''')
        else:
            self.conn = sqlite3.connect(fname)
            self.cursor = self.conn.cursor()

    def mieParameters(self,
                      n_particle,
                      n_host,
                      particle_mu,
                      particle_sigma,
                      force_new=False,
                      effective_model=True,
                      wavelen_n=1000,
                      wavelen_max=1100.0,
                      wavelen_min=100.0,
                      particle_n=20,
                      particle_max=20.0,
                      particle_min=1.0):
        '''
        Mie parameters for Log-normally distributed particles.

        Returns a filename to the mie parameter-hdf5 file in database. If no
        file is present for given combination a new one is generated (can
        take a lot of time). The database of already calculated files is kept
        in sqlite3 database file mie_database.db. Actual files are
        in MieDataFiles-folder inside the same directory.

        Particle refractive index can be complex (1.83 + 2j) for example.
        The host material must have real refractive index.

        You can define particles by sizes max-min-n and lognorm parameters
        sigma and mu. The wavelength range can also be defined here max-min-n.

        If you want to use effective model, only one particle type is created

        WAVELENGTH in nm!!!
        Particle diameters in um!!!

        '''
        n_r = np.real(n_particle)
        n_j = np.imag(n_particle)
        print(n_r, n_j)
        selectStr = ('select filename from data where ' +
                     'n_particle_r = ? AND n_particle_j = ? AND n_host = ? ' +
                     'AND particle_mu=? ' +
                     'AND particle_sigma=? ' +
                     'AND effective_model=? ' +
                     'AND wavelen_n=? AND wavelen_max=? ' +
                     'AND wavelen_min=? AND particle_n=? ' +
                     'AND particle_max=? AND particle_min=?')
        self.cursor.execute(selectStr, [np.real([n_particle])[0],
                                        np.imag([n_particle])[0],
                                        n_host,
                                        particle_mu,
                                        particle_sigma,
                                        effective_model,
                                        wavelen_n,
                                        wavelen_max,
                                        wavelen_min,
                                        particle_n,
                                        particle_max,
                                        particle_min])
        data = self.cursor.fetchall()

        if not data or force_new:
            print('Generating new mie data')
            if(not effective_model):
                filename = self.__generateMie(n_particle,
                                              n_host,
                                              particle_mu,
                                              particle_sigma,
                                              effective_model,
                                              wavelen_n,
                                              wavelen_max,
                                              wavelen_min,
                                              particle_n,
                                              particle_max,
                                              particle_min)
            else:
                filename = self.__generateMieEffective(n_particle,
                                                       n_host,
                                                       particle_mu,
                                                       particle_sigma,
                                                       effective_model,
                                                       wavelen_n,
                                                       wavelen_max,
                                                       wavelen_min,
                                                       particle_n,
                                                       particle_max,
                                                       particle_min)
            if not force_new:
                self.__addMieFile(filename, n_particle, n_host, particle_mu,
                                  particle_sigma, effective_model, wavelen_n,
                                  wavelen_max, wavelen_min, particle_n,
                                  particle_max, particle_min)
        else:
            filename = data[0][0]
        return(filename)

    def mieParametersArbitrary(self,
                               n_particle,
                               n_host,
                               id_1,
                               id_2,
                               particle_distribution,
                               force_new=False,
                               effective_model=True,
                               wavelen_n=1000,
                               wavelen_max=1100.0,
                               wavelen_min=100.0,
                               particle_n=20,
                               particle_max=20.0,
                               particle_min=1.0):
        '''
        Mie parameters for arbitrarily distributed particles.

        id_1 and id_2 are parameters (pick your own) that
        separate the distribution from others.(like mu and sigma in lognorm)
        These are only for cataloging purposes.

        Returns a filename to the mie parameter-hdf5 file in database. If no
        file is present for given combination a new one is generated (can
        take a lot of time). The database of already calculated files is kept
        in sqlite3 database file mie_database.db. Actual files are
        in MieDataFiles-folder inside the same directory.

        Particle refractive index can be complex (1.83 + 2j) for example.
        The host material must have real refractive index.

        You can define particles by sizes max-min-n and particle distribution.
        The wavelength range can also be defined here max-min-n.

        If you want to use effective model, only one particle type is created

        WAVELENGTH in nm!!!
        Particle diameters in um!!!

        '''
        n_r = np.real(n_particle)
        n_j = np.imag(n_particle)
        print(n_r, n_j)
        selectStr = ('select filename from data where ' +
                     'n_particle_r = ? AND n_particle_j = ? AND n_host = ? ' +
                     'AND particle_mu=? ' +
                     'AND particle_sigma=? ' +
                     'AND effective_model=? ' +
                     'AND wavelen_n=? AND wavelen_max=? ' +
                     'AND wavelen_min=? AND particle_n=? ' +
                     'AND particle_max=? AND particle_min=?')
        self.cursor.execute(selectStr, [np.real([n_particle])[0],
                                        np.imag([n_particle])[0],
                                        n_host,
                                        id_1,
                                        id_2,
                                        effective_model,
                                        wavelen_n,
                                        wavelen_max,
                                        wavelen_min,
                                        particle_n,
                                        particle_max,
                                        particle_min])
        data = self.cursor.fetchall()

        if not data or force_new:
            print('Generating new mie data')
            if(not effective_model):
                filename = self.__generateMie(n_particle,
                                              n_host,
                                              id_1,
                                              id_2,
                                              effective_model,
                                              wavelen_n,
                                              wavelen_max,
                                              wavelen_min,
                                              particle_n,
                                              particle_max,
                                              particle_min)
            else:
                filename = self.__generateMieEffectiveArbitrary(n_particle,
                                                                n_host,
                                                                particle_distribution,
                                                                effective_model,
                                                                wavelen_n,
                                                                wavelen_max,
                                                                wavelen_min,
                                                                particle_n,
                                                                particle_max,
                                                                particle_min)
            if not force_new:
                self.__addMieFile(filename, n_particle, n_host, id_1,
                                  id_2, effective_model, wavelen_n,
                                  wavelen_max, wavelen_min, particle_n,
                                  particle_max, particle_min)
        else:
            filename = data[0][0]
        return(filename)

    def __addMieFile(self,
                     filename,
                     n_particle,
                     n_host,
                     particle_mu,
                     particle_sigma,
                     effective_model=True,
                     wavelen_n=1000,
                     wavelen_max=1100.0,
                     wavelen_min=100.0,
                     particle_n=20,
                     particle_max=20.0,
                     particle_min=1.0):
        '''
        Private function.
        Adds mie data filename to database.
        '''
        self.cursor.execute('''insert into data values (?,?,?,?,?,
                            ?,?,?,?,?,?,?,?)''',
                            [np.real([n_particle])[0],
                             np.imag([n_particle])[0],
                             n_host,
                             particle_mu,
                             particle_sigma,
                             effective_model,
                             wavelen_n,
                             wavelen_max,
                             wavelen_min,
                             particle_n,
                             particle_max,
                             particle_min,
                             filename])
        self.conn.commit()

    def __generateMie(self,
                      n_particle,
                      n_host,
                      particle_mu,
                      particle_sigma,
                      effective_model=True,
                      wavelen_n=1000,
                      wavelen_max=1100.0,
                      wavelen_min=100.0,
                      particle_n=20,
                      particle_max=20.0,
                      particle_min=1.0):
        '''
        Private function.
        Generates new mie-data file for the database.
        '''
        n_x_rv = 1000
        n_tht = 90
        wavelengths = np.linspace(wavelen_min, wavelen_max, wavelen_n) / 1000.0
        p_diameters = np.linspace(particle_min, particle_max, particle_n)

        o_f = ("mie_p-%dum-%dum-%d_" % (particle_min,
                                        particle_max,
                                        particle_n) +
               'np-%s_nh-%.2f_' % (n_particle.__format__('.2f'),
                                   n_host) +
               'wave-%.1fnm-%.1fnm-%d' % (wavelen_min,
                                          wavelen_max,
                                          wavelen_n) +
               '.hdf5')
        o_f = baseDir + '/' + o_f

        df = mie.generateMieData(wavelengths,
                                 number_of_rvs=n_x_rv,
                                 number_of_theta_angles=n_tht,
                                 n_particle=n_particle,
                                 n_silicone=n_host,
                                 p_diameters=p_diameters)
        mie.saveMieDataToHDF5([df],
                              particle_diameters=p_diameters,
                              out_fname=o_f,
                              wavelengths=wavelengths * 1000.0)

        return(o_f)

    def __generateMieEffective(self,
                               n_particle,
                               n_host,
                               particle_mu,
                               particle_sigma,
                               effective_model=True,
                               wavelen_n=1000,
                               wavelen_max=1100.0,
                               wavelen_min=100.0,
                               particle_n=20,
                               particle_max=20.0,
                               particle_min=1.0):
        '''
        Private function.
        Generates new effective mie-data file for the database.
        '''

        if particle_n < 10:
            print(
                "Too few particles to calculate \
                effective model: particle_n < 10")
            exit()
        n_x_rv = 10000
        n_tht = 91
        wavelengths = np.linspace(wavelen_min, wavelen_max, wavelen_n) / 1000.0
        p_diameters = np.linspace(particle_min, particle_max, particle_n)

        o_f = ("mie_eff_p-%dum-%dum-%d_" % (particle_min,
                                            particle_max,
                                            particle_n) +
               'np-%s_nh-%.2f_' % (n_particle.__format__('.2f'),
                                   n_host) +
               'wave-%.1fnm-%.1fnm-%d' % (wavelen_min,
                                          wavelen_max,
                                          wavelen_n) +
               '.hdf5')
        o_f = baseDir + '/' + o_f
        # Calculate particle distribution
        N = lognorm(particle_sigma, scale=np.exp(particle_mu))
        # Weight factors of each particle size
        pdf = N.pdf(p_diameters)
        pdf /= pdf.sum()

        weight = dict(zip(p_diameters, pdf))

        df = 0
        df = mie.generateMieDataEffective(wavelengths,
                                          p_normed_weights_dict=weight,
                                          number_of_rvs=n_x_rv,
                                          number_of_theta_angles=n_tht,
                                          n_particle=n_particle,
                                          n_silicone=n_host,
                                          p_diameters=p_diameters)
        print(df.info())
        mie.saveMieDataToHDF5([df],
                              particle_diameters=[p_diameters.mean()],
                              out_fname=o_f,
                              wavelengths=wavelengths * 1000.0)

        return(o_f)

    def __generateMieEffectiveArbitrary(self,
                                        n_particle,
                                        n_host,
                                        particle_distribution,
                                        effective_model=True,
                                        wavelen_n=1000,
                                        wavelen_max=1100.0,
                                        wavelen_min=100.0,
                                        particle_n=20,
                                        particle_max=20.0,
                                        particle_min=1.0):
        '''
        Private function.
        Generates new effective mie-data file for the database.
        '''

        if particle_n < 10:
            print(
                "Too few particles to calculate \
                effective model: particle_n < 10")
            exit()
        n_x_rv = 10000
        n_tht = 91
        wavelengths = np.linspace(wavelen_min, wavelen_max, wavelen_n) / 1000.0
        p_diameters = np.linspace(particle_min, particle_max, particle_n)

        o_f = ("mie_eff_p-%dum-%dum-%d_" % (particle_min,
                                            particle_max,
                                            particle_n) +
               'np-%s_nh-%.2f_' % (n_particle.__format__('.2f'),
                                   n_host) +
               'wave-%.1fnm-%.1fnm-%d' % (wavelen_min,
                                          wavelen_max,
                                          wavelen_n) +
               '.hdf5')
        o_f = baseDir + '/' + o_f

        # Weight factors of each particle size
        pdf = particle_distribution
        pdf /= pdf.sum()

        weight = dict(zip(p_diameters, pdf))

        df = 0
        df = mie.generateMieDataEffective(wavelengths,
                                          p_normed_weights_dict=weight,
                                          number_of_rvs=n_x_rv,
                                          number_of_theta_angles=n_tht,
                                          n_particle=n_particle,
                                          n_silicone=n_host,
                                          p_diameters=p_diameters)
        print(df.info())
        mie.saveMieDataToHDF5([df],
                              particle_diameters=[p_diameters.mean()],
                              out_fname=o_f,
                              wavelengths=wavelengths * 1000.0)

        return(o_f)

if __name__ == '__main__':
    d = MieDatabase()

    ff = d.mieParameters(n_particle=(1.83 + 0j),
                         n_host=1.55,
                         particle_mu= 2.4849,
                         particle_sigma=0.3878,
                         force_new=True,
                         effective_model=True,
                         wavelen_n=10,
                         wavelen_max=1100,
                         wavelen_min=100,
                         particle_n=20,
                         particle_max=20,
                         particle_min=1)
    print(ff)
