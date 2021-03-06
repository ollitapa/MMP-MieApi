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


from mupif import FunctionID
import mmp_mie_api as mie
# Function IDs until implemented at mupif ###
FunctionID.FuncID_ScatteringCrossSections = 55
FunctionID.FuncID_ScatteringInvCumulDist = 56
###############################################


if __name__ == '__main__':

    mieApp = mie.MMPMie('/dev/null')
    mieApp.solveStep(1)
    f = mieApp.getFunction(FunctionID.FuncID_ScatteringCrossSections)
    print(f)
