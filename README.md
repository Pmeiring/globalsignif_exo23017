# README.md

This file provides instructions to set up the tools on CMS Connect for generating toys and computing significances for the large number of signal hypotheses in CMS-EXO-23-017. 

## Step 1: Set up CMS-Connect
CMS Connect is a service designed to provide a Tier3-like environment for condor analysis jobs and enables users to submit to all resources available in the CMS Global Pool. A quickstart guide is available here:

https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookCMSConnect#QuickStart

**In the guide, follow the steps under:**
- "Sign-up to CMS Connect" --> to open a CMS Connect account
- "Create and Upload SSH Keys" --> to create an SSH key and upload it to the registration page, in order to access CMS Connect

Note that - while opening the account is quick - it might take a while (>hours) for the SSH key to propagate and you to have access to CMS Connect. Eventually, you should be able to connect without it asking for a login-password (only for the pass-phrase you set in generating the SSH key):
```
ssh [replace.username]@login.uscms.org
```

## Step 2: Set up git-key & voms-proxy
To use these tools and submit condor jobs, you'll need to set up a git-key and voms-proxy. 

For the git-key, follow [these instructions](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) to generate the key. Then upload the key contents on your github page --> Settings --> SSH and GPG keys --> New SSH key.

For the voms-proxy, use the above quick-start guide ("Setting up your proxy certificates"). Basically, there is already a script on CMS Connect that copies the your voms key from the ~/.globus folder on lxplus, so you can simply use that.

## Step 3: Set up Toy/Significance tools
On CMS Connect:

```
git clone git@github.com:Pmeiring/globalsignif_exo23017.git
```

## Step 4a: Test interactively


## Step 4b: Submit (many!) remote jobs
