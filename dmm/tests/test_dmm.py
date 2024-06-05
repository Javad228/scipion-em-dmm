# **************************************************************************
# *
# * Authors:     Daniel Del Hoyo (ddelhoyo@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
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

from pyworkflow.tests import BaseTest, setupTestProject, DataSet
from pwem.protocols import ProtImportPdb, ProtImportVolumes, ProtImportSequence, ProtImportFiles
from ..protocols import ProtDMMValidation

class TestDMM(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.ds = DataSet.getDataSet('model_building_tutorial')

        setupTestProject(cls)
        cls._runImportPDB()
        # cls._runImportFasta()
        cls._runImportVolume()

    @classmethod
    def _runImportPDB(cls):
        protImportPDB = cls.newProtocol(
            ProtImportPdb,
            inputPdbData=1,
            pdbFile=cls.ds.getFile('PDBx_mmCIF/emd_2513_af2.pdb'))
        cls.launchProtocol(protImportPDB)
        cls.protImportPDB = protImportPDB

    # @classmethod
    # def _runImportFasta(cls):

    #     args = {
	# 		'inputProteinSequence': ProtImportFiles,
	# 		'fileSequence': cls.ds.getFile('Sequences/emd_2513.fasta')
	# 	}
    #     protImportSequence = cls.newProtocol(ProtImportSequence, **args)
    #     cls.launchProtocol(protImportSequence)
    #     cls.protImportSequence = protImportSequence

    @classmethod
    def _runImportVolume(cls):
        args = {'filesPath': cls.ds.getFile(
            'volumes/emd_2513.mrc'),
            'samplingRate': 1.05,
            'setOrigCoord': True,
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
        protImportVolume = cls.newProtocol(ProtImportVolumes, **args)
        cls.launchProtocol(protImportVolume)
        cls.protImportVolume = protImportVolume

    def _runDMM(self):
        protDMM = self.newProtocol(
            ProtDMMValidation,
            af2Structure=self.protImportPDB.outputPdb,
            inputVolume=self.protImportVolume.outputVolume,
            inputSeq='/home/kihara/jbaghiro/scipion/data/tests/model_building_tutorial/Sequences/emd_2513.fasta',
            contourLevel=0)

        self.launchProtocol(protDMM)
        pdbOut = getattr(protDMM, 'outputAtomStruct', None)
        self.assertIsNotNone(pdbOut)

    def testDMM(self):
        self._runDMM()




