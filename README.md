# TotalSeg
A pipeline to segment on CT then convert to RTSTRUCT

Python version: 3.6.8

## Notes
* Weights downloaded to: ~/.totalsegmentator/nnunet/results
* `TotalSegmentator -i example_ct.nii.gz -o seg --ml`
  * `--ml`: multi-label, i.e. combine all label maps into one file
  * `-p`: generate a PNG preview (need a dependency called `Xvfb`)
