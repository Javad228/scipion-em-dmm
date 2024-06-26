# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors: Daniel Del Hoyo (ddelhoyo@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
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


"""
This protocol is used to perform a pocket search on a protein structure using the FPocket software
"""
import os, shutil, time

from pyworkflow.protocol import params
from pwem.protocols import EMProtocol
from pwem.objects import AtomStruct
from pwem.convert.atom_struct import toPdb, toCIF, AtomicStructHandler, addScipionAttribute
from pwem.convert import Ccp4Header
from pyworkflow.utils import Message, weakImport
from pwem.viewers.viewer_chimera import Chimera
from pwem.emlib.image import ImageHandler
from kiharalab import Plugin

class ProtDMM(EMProtocol):
    """
    Executes the DMM software to validate a structure model
    """
    _label = 'DMM'
    _ATTRNAME = 'DMM_score'
    _OUTNAME = 'outputAtomStruct'
    _possibleOutputs = {_OUTNAME: AtomStruct}

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ """
        form.addHidden(params.USE_GPU, params.BooleanParam, default=True,
                       label="Use GPU for execution: ",
                       help="This protocol has both CPU and GPU implementation.\
                                                 Select the one you want to use.")

        form.addHidden(params.GPU_LIST, params.StringParam, default='0', label="Choose GPU IDs",
                       help="Add a list of GPU devices that can be used")

        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('inputVolume', params.PointerParam,
			pointerClass='Volume',
			label="Input volume: ",
			help='Select the electron map of the structure')
        
        form.addParam('contourLevel', params.FloatParam,
                      default=0,
                      label='contourLevel', important=True,
                      help='contourLevel')

        form.addParam('inputSeq', params.PathParam,
                      label="Input Sequence",
                      help="Directory with the input files. \n"
                           "Check protocol help for more details.")
        
        form.addParam('path_training_time', params.IntParam,
                    label="path training time",
                    help="path training time\n")
        
        form.addParam('fragment_assembling_time', params.IntParam,
                    label="fragment assembling time",
                    help="fragment assembling time\n")
        
        form.addParam('af2Structure', params.PointerParam,
                allowsNull=True,
                pointerClass='AtomStruct',
                label="AlphaFold2 Structure: ",
                help='Select the corresponding af2 structure')

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        print("in _insertAllSteps")

        # Insert processing steps
        self._insertFunctionStep('convertInputStep')
        self._insertFunctionStep('DMMStep')
        self._insertFunctionStep('createOutputStep')

    def convertInputStep(self):
        print("in convertInputStep")

        inVol = self._getInputVolume()
        inVolFile, inVolSR = inVol.getFileName(), inVol.getSamplingRate()

        #Convert volume to mrc
        mrcFile = self._getTmpPath('inpVolume.mrc')
        ImageHandler().convert(inVolFile, mrcFile)
        Ccp4Header.fixFile(mrcFile, mrcFile, inVol.getOrigin(force=True).getShifts(),
                           inVolSR, Ccp4Header.START)

        # Volume header fixed to have correct origin
        Ccp4Header.fixFile(mrcFile, self.getLocalVolumeFile(), inVol.getOrigin(force=True).getShifts(),
                           inVolSR, Ccp4Header.ORIGIN)

    def DMMStep(self):
        print("in dmm step")

        """
        Run DMM script.
        """
        program_path = Plugin._DMMBinary
        args = self.getDMMArgs()
        for_gpu = ""
        if getattr(self, params.USE_GPU):
            for_gpu = 'export CUDA_VISIBLE_DEVICES={}'.format(self.getGPUIds()[0])
        envActivationCommand = "{} {}".format(Plugin.getCondaActivationCmd(), Plugin.getProtocolActivationCommandDeep('dmm'))
        fullProgram = '{} && {} && {}/dmm_full_multithreads.sh'.format(for_gpu,envActivationCommand,Plugin._DMMBinary)

        if 'dmm_full_multithreads.sh' not in args:
            args = '-o predictions -p {}{}'.format(Plugin._DMMBinary, args)
        print(fullProgram)
        print(args)
        self.runJob(fullProgram,args, cwd=program_path)

        # outDir = self._getExtraPath('predictions')

        # DMMDir = os.path.join(Plugin._DMMBinary, 'Predict_Result', self.getVolumeName())
        # shutil.copytree(DMMDir, outDir)
        # shutil.rmtree(DMMDir)
        
    def getDMMArgs(self):
        print("in dmm args")
        map_path = os.path.abspath(self.getLocalVolumeFile())
        fasta_path = os.path.abspath(self.getLocalSequenceFile())
        contour = self.contourLevel.get()
        path_training_time = self.path_training_time.get()
        fragment_assembling_time = self.fragment_assembling_time.get()
        output_path = os.path.abspath(self._getTmpPath('predictions'))
        print(self.af2Structure)
        if self.af2Structure.get() != None:
            alphafold_pdb_path = os.path.abspath(self.af2Structure.get().getFileName()) if self.af2Structure.get() else ""
            args = f" -m {map_path} -f {fasta_path} -A {alphafold_pdb_path} -c {contour} -o {output_path} -t {path_training_time} -T {fragment_assembling_time}"
        else:
            args = f" -m {map_path} -f {fasta_path} -c {contour} -o {output_path} -t {path_training_time} -T {fragment_assembling_time}"


        return args
    
    def createOutputStep(self):
        outStructFileName = self._getPath('Deepmainmast.cif')
        outPdbFileName = os.path.abspath(self._getTmpPath('predictions/DeepMainmast.pdb'))

        ASH = AtomicStructHandler()
        cryoScoresDic = self.parseDMMScores(outPdbFileName)

        outputVolume = toCIF(outPdbFileName, self._getTmpPath('inputStruct.cif'))
        cifDic = ASH.readLowLevel(outputVolume)
        cifDic = addScipionAttribute(cifDic, cryoScoresDic, self._ATTRNAME)
        ASH._writeLowLevel(outStructFileName, cifDic)

        # Create AtomStruct object with the CIF file
        AS = AtomStruct(filename=outStructFileName)

        # Set the volume of the AtomStruct object
        outVol = self._getInputVolume().clone()
        outVol.setLocation(self.getLocalVolumeFile())
        AS.setVolume(outVol)

        # Define the outputs for the protocol
        self._defineOutputs(**{self._OUTNAME: AS})


    # --------------------------- INFO functions -----------------------------------
    def _summary(self):
        summary = []
        return summary

    def _methods(self):
        methods = []
        return methods

    def _warnings(self):
        """ Try to find warnings on define params. """
        warnings=[]

        return warnings

    # --------------------------- UTILS functions -----------------------------------


    def _getInputVolume(self):
      if self.inputVolume.get() is None:
        fnVol = self.inputAtomStruct.get().getVolume()
      else:
        fnVol = self.inputVolume.get()
      return fnVol
    
    def _getinputSeq(self):
        return self.inputSeq.get()

    def getStructFile(self):
        return os.path.abspath(self.inputAtomStruct.get().getFileName())

    def getVolumeFile(self):
        return os.path.abspath(self._getInputVolume().getFileName())
    
    def getSequenceFile(self):    
        return self._getinputSeq()

    def getStructName(self):
        return os.path.basename(os.path.splitext(self.getStructFile())[0])

    def getVolumeName(self):
        return os.path.basename(os.path.splitext(self.getLocalVolumeFile())[0])

    def getPdbStruct(self):
        return self._getTmpPath(self.getStructName()) + '.pdb'

    def getLocalVolumeFile(self):
        oriName = os.path.basename(os.path.splitext(self.getVolumeFile())[0])
        return self._getExtraPath('{}_{}.mrc'.format(oriName, self.getObjId()))
    
    def getLocalSequenceFile(self):
        
        oriName = os.path.basename(os.path.splitext(self.getSequenceFile())[0])
        extrapath = self._getExtraPath('{}_{}.fasta'.format(oriName, self.getObjId()))
        parts = extrapath.split('/')
        res = '/'.join(parts[:-1])
        print("HAHA")
        print(os.path.abspath(extrapath))
        print(os.path.abspath(res))
        shutil.copyfile(self.getSequenceFile(),os.path.abspath(extrapath))
        # shutil.copy(os.path.abspath(extrapath),os.path.abspath(res))
        return extrapath


    def parseDMMScores(self, pdbFile):
        '''Return a dictionary with {spec: value}
        "spec" should be a chimera specifier. In this case:  chainId:residueIdx'''
        DMMDic = {}
        with open(pdbFile) as f:
            for line in f:
                if line.startswith('ATOM') or line.startswith('HETATM'):
                    resId = '{}:{}'.format(line[21].strip(), line[22:26].strip())
                    if not resId in DMMDic:
                      DMMScore = line[60:66].strip()
                      DMMDic[resId] = DMMScore
        return DMMDic
    
    def getGPUIds(self):
        return getattr(self, params.GPU_LIST).get().split(',')

    def getDMMScoreFile(self):
      return self._getPath('{}.defattr'.format(self._ATTRNAME))

    def chimeraResampleScript(self, inVolFile, newSampling, outFile):
        scriptFn = self._getExtraPath('resampleVolume.cxc')
        with open(scriptFn, 'w') as f:
            f.write('cd %s\n' % os.getcwd())
            f.write("open %s\n" % inVolFile)
            f.write('vol resample #1 spacing {}\n'.format(newSampling))
            f.write('save {} model #2\n'.format(outFile))
            f.write('exit\n')
        return scriptFn

    def chimeraResample(self, inVolFile, newSR, outFile):
        with weakImport("chimera"):
            from chimera import Plugin as chimeraPlugin
            resampleScript = self.chimeraResampleScript(inVolFile, newSampling=newSR, outFile=outFile)
            chimeraPlugin.runChimeraProgram(chimeraPlugin.getProgram() + ' --nogui --silent',
                                            resampleScript, cwd=os.getcwd())
            while not os.path.exists(outFile):
              time.sleep(1)
        return outFile


def chimeraInstalled():
  return Chimera.getHome() and os.path.exists(Chimera.getProgram())
