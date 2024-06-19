========================================
Kihara Lab plugin
========================================
This is a **Scipion** plugin that offers different `Kihara Lab tools <https://kiharalab.org/>`_.
These tools will make it possible to carry out different functions for working with electron density maps.
The code involving these functionalities can be found at https://github.com/kiharalab.

This plugin allows the use of CryoREAD and DeepMainmast algorithms.

========================================
Install this plugin
========================================
Installation
============

1. If you do not have **conda** already installed (run ``which conda`` in your console), install `Miniconda <https://docs.conda.io/en/latest/miniconda.html#linux-installers>`__ as in example below. Alternatively, proceed to step 3.

::

    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /path/for/miniconda

2. Make sure you are running **bash** shell (run ``echo $SHELL`` in your console), then initialize conda:

::

    source /path/for/miniconda/etc/profile.d/conda.sh

3. Activate **base** conda environment and install Scipion installer with **pip3** provided by **conda**.

::

    conda activate
    pip3 install --user scipion-installer

4. Install Scipion core and generate default config files

::

    python3 -m scipioninstaller -conda -noXmipp -noAsk /path/for/scipion
    /path/for/scipion/scipion3 config --overwrite

5. Open **/path/for/scipion/config/scipion.conf** file and append the variables below to the end of the file. Make sure they point to correct locations for CUDA, OpenMPI and other software necessary for Xmipp:

::

    CUDA = True
    CUDA_BIN = /usr/local/cuda-11.4/bin
    CUDA_LIB = /usr/local/cuda-11.4/lib64
    MPI_BINDIR = /usr/lib64/mpi/gcc/openmpi/bin
    MPI_LIBDIR = /usr/lib64/mpi/gcc/openmpi/lib
    MPI_INCLUDE = /usr/lib64/mpi/gcc/openmpi/include
    OPENCV = False

See `Configuration guide <scipion-configuration>`_ for more details about these and other possible variables.

6. Install `Xmipp <https://github.com/I2PC/xmipp#xmipp>`__ plugin. We have tested Xmipp compilation on the following operating systems: `Ubuntu 16.04 <https://github.com/I2PC/xmipp/wiki/Installing-Xmipp-on-Ubuntu-16.04>`__, `Ubuntu 18.04 <https://github.com/I2PC/xmipp/wiki/Installing-Xmipp-on-Ubuntu-18.04>`__, `Ubuntu 20.04 <https://github.com/I2PC/xmipp/wiki/Installing-Xmipp-on-Ubuntu-20.04>`__, `Ubuntu 22.04 <https://github.com/I2PC/xmipp/wiki/Installing-Xmipp-on-Ubuntu-22.04>`_ and `Centos 7 <https://github.com/I2PC/xmipp/wiki/Installing-Xmipp-on-CentOS-7-9.2009>`__. A list of dependencies can be found `here <https://github.com/I2PC/xmipp#additional-dependencies>`__. Command example below is using 12 threads

::

    /path/for/scipion/scipion3 installp -p scipion-em-xmipp -j 12 | tee -a install.log

7. Create an alias for Scipion launcher in your ``.bashrc`` file:

::

   alias scipion3="/path/for/scipion/scipion3"

If any of the steps above fails, check `install.log` file for errors and refer to the :ref:`Troubleshooting <troubleshooting>` guide.

DMM and Cryoread are installed automatically by scipion.

.. code-block::

    scipion3 installp -p scipion-em-kiharalab  --devels

========================================
Protocols
========================================
scipion-em-kiharalab contains the following protocols:

- **DeepMainmast**: Build an entire protein 3D model directly from a EM map of up to 5 A resolution.
- **CryoREAD**: DNA/RNA structure modeling tool using deep learning for a cryo-EM map of up to 10 Å resolution.

========================================
Packages & enviroments
========================================
Packages installed by this plugin can be located in ``/path/to/scipion/software/em/``.

The following packages will be created:

- DMM-``version``
- CryoREAD-``version``

Where ``version`` is the current version of that specific package.

Also, the following conda enviroments will be created:

- DMM-``version``
- CryoREAD-``version``

As of today, Scipion does not automatically uninstall the conda enviroments created in the installation process when uninstalling a plugin, so keep this list in mind if you want to clean up some disk space if you need to uninstall scipion-em-kiharalab.

========================================
Tests
========================================
scipion-em-kiharalab contains the following tests:

- **test_cryoread_seq.py**: Test cryoread with sequence input. Inputs: 21051.fasta, 21051.mrc
- **test_cryoread.py**: Test cryoread without sequence input. Inputs: 21051.mrc
- **test_dmm.py**: Test DeepMainmast without af2 input. Inputs: emd_2513.fasta, emd_2513.mrc
- **test_dmm_af2.py**: Test DeepMainmast with af2 input. Inputs: emd_2513.fasta, emd_2513.mrc, emd_2513_af2.pdb

.. code-block::

    ~/scipion/scipion3 tests kiharalab.tests.test_cryoread
    ~/scipion/scipion3 tests kiharalab.tests.test_cryoread_seq
    ~/scipion/scipion3 tests kiharalab.tests.test_dmm
    ~/scipion/scipion3 tests kiharalab.tests.test_dmm_af2

========================================
Running with GUI
========================================
1.

.. code-block::

    ~/scipion/scipion3

run local scipion version which will open GUI

2.  Click Create Project
3.  From the left menu choose import volume protocol and input the necessary fields
4.  Find the DMM, Cryoread protocol from the left. It should be under kiharalab.
5.  Link the import volume to the DMM/Cryoread input
6.  This will have to be done with af2 model as well.
7.  Fasta sequence can be linked directly from file path.