# README.md

This file provides instructions to set up the tools on CMS Connect for generating toys and computing significances for the large number of signal hypotheses in CMS-EXO-23-017. 

## Step 1: Set up CMS Connect
CMS Connect is a service designed to provide a Tier3-like environment for condor analysis jobs and enables users to submit to all resources available in the CMS Global Pool. A quickstart guide is available here:

https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookCMSConnect#QuickStart

**In the guide, follow the steps under:**
- "Sign-up to CMS Connect" --> to open a CMS Connect account
- "Create and Upload SSH Keys" --> to create an SSH key and upload it to the registration page, in order to access CMS Connect

Note that - while opening the account is quick - it might take a while (>hours) for the SSH key to propagate and you to have access to CMS Connect. Eventually, you should be able to connect without it asking for a login-password (only for the pass-phrase you set in generating the SSH key):
```
ssh [replace.username]@login.uscms.org
```
If you stored your SSH key not in the default path (```~/.ssh/id_rsa```), but in another path (eg. ```~/.ssh/id_rsa_cmsconnect```), you should explicitely point to that path when trying to access CMS Connect:
```
ssh -i ~/.ssh/id_rsa_cmsconnect [replace.username]@login.uscms.org
```

## Step 2: Set up git-key & voms-proxy
To use these tools and submit condor jobs, you'll need to set up a git-key and voms-proxy. 

For the git-key, follow [these instructions](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) to generate the key. Then upload the key contents on your github page --> Settings --> SSH and GPG keys --> New SSH key.

For the voms-proxy, use the above quick-start guide ("Setting up your proxy certificates"). Basically, there is already a script on CMS Connect that copies the your voms key from the ~/.globus folder on lxplus, so you can simply use that.

**Be sure to activate it as usual:**
```
voms-proxy-init -voms cms -valid 192:00 
```

## Step 3: Set up Toy/Significance tools
On CMS Connect:

```
git clone git@github.com:Pmeiring/globalsignif_exo23017.git
cd globalsignif_exo23017
xrdcp root://eoscms.cern.ch//eos/cms/store/group/phys_susy/SOS/CMSSW_10_6_26.tgz ./
```
The ```CMSSW_10_6_26.tgz``` files is a pre-compiled release that includes combine. For simplicity it can be copied from EOS as shown above, but one could also set it up with a singularity image on CMS Connect.

## Step 4a: Test interactively

Interactive testing should be done on a singularity. Set this up as:
```
cmssw-el7
```

The ```run.sh``` script can be used both for toy generation and signficance computation. It takes a few arguments:
```
./run.sh NTOYS MP SEED GENERATE SIGNIFICANCE
```
where:
- NTOYS = number of toys per mass-point (and per condor job)
- MP = signal point, formatted as mN2_mN1_ctau (eg. 100_60_0)
- SEED = random seed. When running on condor, we fix the seed to the job number
- GENERATE = boolean indicating if you want to generate the toys
- SIGNIFICANCE = boolean indicating if you want to compute significances

For example, try running the toy generation:
```
./run.sh 10 100_60_0 42 1 0
```
If successful, this should unpack the CMSSW release in a temporary work-directory,  generate 10 toys for the ```100_60_0``` mass-point and save the toys on the ```toy``` location specified in ```run.sh```.


## Step 4b: Submit (many!) remote jobs

Once you've confirmed with step 4a that you can run the scripts successfully, you're ready to submit to condor. For this you don't need to run in a singularity.

We first need to generate the toys. The toy generation is by default configured to launch 330 jobs with 1000 toys per job. This is "relatively" quick:
```
condor_submit condor/generate_toys.sub
```

Once all toys are in place, the time-consuming second step is to compute for each toy the significance for all mass-points. In CMS-EXO-23-017 we have 294 (C1,dM) mass-hypotheses, so that's already 294*330=97020 jobs, each running 1000 significance computations over ~24h. From CMS Connect you cannot submit all 97k at once, so you'll have to submit them in batches. Submitting them in batches of 100 GeV in mC1 seems to work well, ie. ```100_50_0``` to ```175_174p4_0```.
```
condor_submit condor/compute_signif.sub
```

## Step 5: Compute global significance

The final step aggregates all significances for all toys and mass-points and computes the global significance. As this requires read access on EOS, it's easiest to run this on lxplus directly:
```
python3 process_signif.py --dryrun
```
This will first check if all the expected outputs (ie. significance files) are there without doing the computation. If you remove ```--dryrun```, it will also compute per toy the maximum significance across all mass-points, and stores those values in a numpy file. That numpy file can finally be used to make the global significance plot:
```
python3 plot_signif.py
```
This will make a histogram of the maximum significance per toy, count the number of toys above the maximum observed local significance, and compute the global p-value and significance.
