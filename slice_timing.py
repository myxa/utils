import numpy as np
import nibabel as nb


def slice_timing(TRsec, nSlices): 
    """
    Writes the slice timing information to a text file named 'slice_timing.txt'
    
    Parameters
    ----------
    TRsec : float
        Repetition time in seconds
    nSlices : int
        Number of slices
    
    Returns
    -------
    None
    """

    TA = TRsec / nSlices # slice acquisition time offset
    bidsSliceTiming = np.arange(0, TRsec - TA, TA)
    with open('slice_timing.txt', 'w') as f:
        for i in bidsSliceTiming:
            f.write(str(i) + ',\n')


def n_slices(nii_path):
    """
    Reads the number of slices from a NIfTI file and prints it to the console

    Parameters
    ----------
    nii_path : str
        Path to NIfTI file

    Returns
    -------
    int
        Number of slices
    """
    img = nb.load(nii_path)
    header = img.header
    slices = header.get_data_shape()[2]  # dim[3] in 1-based NIfTI indexing
    print(f"Number of slices: {slices}")
    return slices
