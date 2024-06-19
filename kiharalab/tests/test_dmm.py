
from pyworkflow.tests import BaseTest, setupTestProject, DataSet
from pwem.protocols import ProtImportPdb, ProtImportVolumes

from ..protocols import ProtDMM

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
            ProtDMM,
            inputVolume=self.protImportVolume.outputVolume,
            inputSeq='/home/kihara/jbaghiro/scipion/data/tests/model_building_tutorial/Sequences/emd_2513.fasta',
            af2Structure=self.protImportPDB.outputPdb,
            path_training_time=600,
            fragment_assembling_time=600,
            contourLevel=0.0)
        print(self.protImportVolume.outputVolume)
        self.launchProtocol(protDMM)
        # pdbOut = getattr(protDMM, 'outputAtomStruct', None)
        # self.assertIsNotNone(pdbOut)

    def testDMM(self):
        self._runDMM()




