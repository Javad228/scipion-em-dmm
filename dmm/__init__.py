# **************************************************************************
# *
# * Authors:  Daniel Del Hoyo (ddelhoyo@cnb.csic.es)
# *           Martín Salinas  (martin.salinas@cnb.csic.es)
# *
# * Biocomputing Unit, CNB-CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************
import pwem, os
from .constants import *
from .install_helper import InstallHelper

__version__ = dmm_VERSION
_logo = "dmm_logo.png"
_references = ['genki2021DMM']

class Plugin(pwem.Plugin):
    """
    Definition of class variables. For each package, a variable will be created.
    _<packageNameInLowercase>Home will contain the full path of the package, ending with a folder whose name will be <packageNameFirstLetterLowercase>-<defaultPackageVersion> variable.
        For example: _emap2secHome = "~/Documents/scipion/software/em/emap2sec-1.0"
    
    Inside that package, for each binary, there will also be another variable.
    _<binaryNameInLowercase>Binary will be a folder inside _<packageNameInLowercase>Home and its name will be <binaryName>.
        For example: _emap2secplusBinary = "~/Documents/scipion/software/em/emap2sec-1.0/Emap2secPlus"
    """
    # DMM
    DMMDefaultVersion = DMM_DEFAULT_VERSION
    _DMMHome = os.path.join(pwem.Config.EM_ROOT, 'DMM-' + DMMDefaultVersion)
    _DMMBinary = os.path.join(_DMMHome, 'DMM')


    @classmethod
    def _defineVariables(cls):
        """
        Return and write a home and conda enviroment variable in the config file.
        Each package will have a variable called <packageNameInUppercase>_HOME, and another called <packageNameInUppercase>_ENV
        <packageNameInUppercase>_HOME will contain the path to the package installation. For example: "~/Documents/scipion/software/em/DMM-1.0"
        <packageNameInUppercase>_ENV will contain the name of the conda enviroment for that package. For example: "DMM-1.0"
        """
        # DMM
        cls._defineEmVar(DMM_HOME, cls._DMMHome)
        cls._defineVar('DMM_ENV', 'DMM-' + cls.DMMDefaultVersion)

    @classmethod
    def defineBinaries(cls, env):
        """
        This function defines the binaries for each protocol.
        """
        cls.addDMM(env)

    
    @classmethod    
    def addDMM(cls, env):
        """
        This function provides the neccessary commands for installing DMM.
        """
        # Defining protocol variables
        packageName = 'DMM'

        # Instanciating installer
        installer = InstallHelper(packageName, packageVersion=cls.DMMDefaultVersion)

        # Installing protocol
        installer.getCloneCommand('https://github.com/dmmainMast.git', binaryFolderName=packageName)\
            .getCondaEnvCommand(pythonVersion='3.8.5', binaryPath=cls._DMMBinary)\
            .addPackage(env, dependencies=['git', 'conda', 'pip'])

    # ---------------------------------- Utils functions  -----------------------
    @classmethod
    def getProtocolEnvName(cls, protocolName, repoName=None):
        """
        This function returns the env name for a given protocol and repo.
        """
        return (repoName if repoName else protocolName) + "-" + getattr(cls, protocolName + 'DefaultVersion')
    
    @classmethod
    def getProtocolActivationCommand(cls, protocolName, repoName=None):
        """
        Returns the conda activation command for the given protocol.
        """
        return "conda activate " + cls.getProtocolEnvName(protocolName, repoName)