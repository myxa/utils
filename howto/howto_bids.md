## BIDS directory structure for fMRI 



```
sub-<label>/

   \[ses-<label>/]

       anat/

           sub-<label>\[\_ses-<label>]\[\_task-<label>]\[\_run-<index>]\_T1W.json

           sub-<label>\[\_ses-<label>]\[\_task-<label>]\[\_run-<index>]\_T1W.nii.gz

       func/

           sub-<label>\[\_ses-<label>]\[\_task-<label>]\[\_run-<index>]\_bold.json

           sub-<label>\[\_ses-<label>]\[\_task-<label>]\[\_run-<index>]\_bold.nii.gz

           sub-<label>\[\_ses-<label>]\[\_task-<label>]\[\_run-<index>]\_events.json

```



## Dataset sidecar json


### anat 
T1w sidecar JSON files are optional.


### func

#### dataset\_description.json 

(is like readme)


```
{
   "Name": "",
   "BIDSVersion": "1.10.0",
   "HEDVersion": "8.2.0",
   "DatasetType": "raw",
   "License": "",
   "Authors": [],
   "Acknowledgements": "",
   "HowToAcknowledge": "",
   "Funding": [],
   "EthicsApprovals": [],
   "ReferencesAndLinks": [],
   "DatasetDOI": "doi:"
}

```

#### MINIMAL JSON FOR BOLD

All the required fields to successfully process bold with fmriprep.

```
{
 "TaskName": "rest",
 "RepetitionTime": 0.72,
 "SliceTiming": [
   0.0,
   0.36
 ]
}
```




##### Slice timing formula 


```
TRsec = 2.5 
nSlices = 32 
TA = TRsec / nSlices 
bidsSliceTiming = np.arange(0, TRsec - TA, TA)

```

nSlices can be found in nii header - 3rd axis of the image shape.


