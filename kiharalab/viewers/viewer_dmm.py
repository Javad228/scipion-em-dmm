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

from ..protocols import ProtDMM
from pwem.viewers import ChimeraAttributeViewer

class DMMViewer(ChimeraAttributeViewer):
  """ Viewer for attribute DMM score of an AtomStruct.
    Includes visualization in chimera and in histograms"""
  _targets = [ProtDMM]
  _label = 'Atomic structure attributes viewer'

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  def _defineParams(self, form):
      super()._defineParams(form)
      # Overwrite defaults
      from pwem.wizards.wizard import ColorScaleWizardBase
      group = form.addGroup('Color settings')
      ColorScaleWizardBase.defineColorScaleParams(group, defaultLowest=-1, defaultHighest=1, defaultIntervals=21,
                                                  defaultColorMap='RdBu_r')
