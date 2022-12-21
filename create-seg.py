# A segmentation model using TotalSegmentator by WJakob Wasserthal (https://arxiv.org/abs/2208.05868)
#
# This script contains a pipeline from DICOM, to segmentation, then to RTSTRUCT
# Virtual env: /physical_sciences/yusun/totalseg
#
# Yu Sun
# Dec 2022 (some work before Christmas)
#

import os
import argparse
from pathlib import Path
import SimpleITK as sitk
import nibabel as nib
import numpy as np
from rt_utils import RTStructBuilder
from totalsegmentator.map_to_binary import class_map


def dcm2nii(src_path: str, save_path: str):
    """Convert DICOM series to NIfTI

    Args:
        src_path (Union[str, Path]): DICOM source folder
        save_path (Union[str, Path]): NIfTI output path
    """
    reader = sitk.ImageSeriesReader()
    fl = reader.GetGDCMSeriesFileNames(src_path)  # will sort by instance id
    reader.SetFileNames(fl)
    img = reader.Execute()

    sitk.WriteImage(img, save_path)


def seg(src_path: str, save_path: str):
    """Perform the segmentation using the TotalSegmentator

    Args:
        src_path (Union[str, Path]): Input NIfTI file path
        save_path (Union[str, Path]): Output segmentation folder path
    """
    os.system(f"TotalSegmentator -i {src_path} -o {save_path} --ml")


def seg2struct(dcm_path: str, seg_path: str, strt_path: str):
    """Converts the segmentation to RTStruct

    Args:
        dcm_path (Union[str, Path]): DICOM folder path
        seg_path (Union[str, Path]): segmentation file path
        strt_path (Union[str, Path]): RTStruct file path to save
    """
    strt = RTStructBuilder.create_new(dicom_series_path=dcm_path)
    seg = nib.load(seg_path).get_fdata()
    seg = np.swapaxes(seg, 0, 1)

    uniq_vals = np.unique(seg).astype(np.uint8)
    for value in uniq_vals:
        if value == 0:
            continue
        strt.add_roi(mask=(seg == value), name=class_map["total"][value])
    strt.save(strt_path)


if __name__ == "__main__":
    dcm_path = "ct-dcm"
    nii_path = "ct.nii.gz"
    seg_path = "seg-test.nii"
    strt_path = "rtstruct.dcm"

    parser = argparse.ArgumentParser(
        description="A pipeline to segment DICOM and generate RTStruct",
        epilog="Set up by Yu Sun using TotalSegmentator by Jakob Wasserthal, https://arxiv.org/abs/2208.05868",
    )

    parser.add_argument(
        "-i", metavar="dicom-folder", dest="input", help="DICOM folder", required=True
    )

    parser.add_argument(
        "-o",
        metavar="output-path",
        dest="output",
        help="RTStruct save path",
        required=True,
    )

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True, parents=True)

    dcm_path = args.input
    nii_path = f"{args.output}/ct.nii.gz"
    seg_path = f"{args.output}/seg-test.nii.gz"
    strt_path = f"{args.output}/rtstruct.dcm"

    dcm2nii(dcm_path, nii_path)
    seg(nii_path, seg_path)
    seg2struct(dcm_path, seg_path, strt_path)
