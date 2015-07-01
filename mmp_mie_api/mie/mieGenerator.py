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

from datetime import datetime
from multiprocessing import Pool

import h5py as h5
import numpy as np
import pandas as pd

from . import scatteringTools as st
from .bhmie_herbert_kaiser_july2012 import bhmie


def calculateMie(data):
    # Extract data
    (p, w, n_p, n_medium, th, n_theta, x_rv) = data
    # Size parameter
    # x      - size parameter = k*radius = 2pi/lambda * radius
    #          (lambda is the wavelength in the medium around the scatterers)
    x = np.pi * p / (w / n_medium)
    # Mie parameters
    (S1, S2, Qext, Qsca, Qback, gsca) = bhmie(x, n_p / n_medium, n_theta)
    # Phase function
    P = (np.absolute(S1) ** 2.0 + np.absolute(S2) ** 2.0) / \
        (Qsca * x ** 2.0)
    # Cumulative distribution
    cP = st.cumulativeDistributionTheta(P, th)
    # Normalize
    cP /= cP[-1]

    # Inverse cumulative distribution for random variable picking
    cPinv = st.invertNiceFunction(np.degrees(th), cP, x_rv)

    pD = {}
    pD['particleDiameter'] = p
    pD['sizeParameter'] = x
    pD['wavelength'] = w
    pD['crossSections'] = Qext * np.pi * (p / 2.0) ** 2.0
    pD['inverseCDF'] = cPinv
    pD['phaseFunction'] = P
    pD['cumulativePhaseFunction'] = cP

    # Return generated data
    return pD


def generateMieData(wavelengths, number_of_rvs, number_of_theta_angles,
                    n_particle, n_silicone, p_diameters):
    '''
    Mie generator

    Remember to use the same units in wavelengths and p_diameters
    '''
    print("#########################################")
    print("Calculating Mie data...")
    print("Wavelengths %.1f - %.1f (%d)" %
          (wavelengths[0], wavelengths[-1], len(wavelengths)))
    print("Particle diams %.1f - %.1f, (%d)" %
          (p_diameters[0], p_diameters[-1], len(p_diameters)))
    print("n_host %f, n_particle %s" %
          (n_silicone, n_particle.__format__('.2f')))
    print("Number of RVs: %d" % number_of_rvs)
    print("Number of Theta angles: %d" % number_of_theta_angles)
    startTime = datetime.now()
    x_rv = np.linspace(0, 1, number_of_rvs)

    n_tht = number_of_theta_angles
    th = np.linspace(0, np.pi, 2 * n_tht - 1)

    # Make data for mie calculation queues
    pData = []
    for p in p_diameters:
        for wave in wavelengths:
            pData.extend([(p, wave, n_particle, n_silicone, th, n_tht, x_rv)])

    # Start pool
    pool = Pool(processes=10)
    # Start calculating
    result = pool.map(calculateMie, pData)

    # Make data into DataFrame
    df = pd.DataFrame(result.get())

    print()
    print('Calculation took:')
    print(str(datetime.now() - startTime).split('.', 2)[0])
    print("#########################################")

    return(df)


def generateMieDataEffective(wavelengths, number_of_theta_angles,
                             n_particle, n_silicone, p_diameters,
                             p_normed_weights_dict,
                             number_of_rvs=1001):
    '''
    Mie generator

    Remember to use the same units in wavelengths and p_diameters
    '''
    print("#########################################")
    print("Calculating Mie data...")
    startTime = datetime.now()
    x_rv = np.linspace(0, 1, number_of_rvs)

    n_tht = number_of_theta_angles
    th = np.linspace(0, np.pi, 2 * n_tht - 1)

    # Make data for mie calculation queues
    pData = []
    for p in p_diameters:
        for wave in wavelengths:
            pData.extend([(p, wave, n_particle, n_silicone, th, n_tht, x_rv)])

    # Start pool
    pool = Pool(processes=10)
    # Start calculating
    result = pool.map_async(calculateMie, pData)

    print('Calculating effective data...')

    # Make data into DataFrame
    df = pd.DataFrame(result.get())
    df['weight'] = df['particleDiameter'].apply(
        lambda x: p_normed_weights_dict[x])

    # Calculate effective data
    df['particleDiameter'] = df['particleDiameter'] * df.weight
    df['crossSections'] = df['crossSections'] * df.weight
    df['inverseCDF'] = df['inverseCDF'] * df.weight
    g = df.groupby('wavelength')

    dd = g.agg({'particleDiameter': 'sum',
                'crossSections': 'sum',
                'inverseCDF': lambda x: list(np.sum(list(x.values), axis=0))})
    dd['particleDiameter'] = dd['particleDiameter'].mean()

    print()
    print('Calculation took alltogether:')
    print(str(datetime.now() - startTime).split('.', 2)[0])
    print("#########################################")

    return(dd.reset_index())


def saveMieDataToHDF5(df_list,
                      particle_diameters,
                      wavelengths,
                      out_fname):
    print("Saving Mie-data...")

    # print(df.info())

    # Create file for saving data
    f = h5.File(out_fname, "w")

    # Save each particle diameter
    f.create_dataset("particleDiameter",
                     data=particle_diameters)
    f.create_dataset("wavelengths",
                     data=wavelengths)

    # Group values for each particle type.
    pDataG = f.create_group("particleData")
    p_id = 0
    for df in df_list:
        # print(df['crossSections'])
        groups = df.groupby('particleDiameter')

        for name, g in groups:
            grp = pDataG.create_group(str(p_id))
            g = g.sort('wavelength')
            # Save each inverseCDF.
            # Column = wavelength
            # Row = inverseCDF
            grp.create_dataset("inverseCDF",
                               data=np.vstack(g['inverseCDF'].values).T)
            # Save crosssections for each wavelength
            grp.create_dataset("crossSections",
                               data=g['crossSections'].values)
            p_id += 1

    # Save identifier for each particle size
    f.create_dataset("particleID",
                     data=np.arange(p_id))

    f.close()
    print("Saved!")
