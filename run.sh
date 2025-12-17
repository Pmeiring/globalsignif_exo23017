#!/bin/sh
set -e
unset PERL5LIB

# Datacard folder (and rew scenario)
eos=/eos/cms/store/group/phys_susy/SOS/limits_TChiWZ_neg_static_20251124_merged/
rew=neg

# Output directory for toys and significances. Should contain subdirectories "toys" and "signif"
toy=/eos/cms/store/group/phys_susy/SOS/limits_TChiWZ_neg_static_20251124_toys/

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Parse inputs
NTOYS=$1; shift
MP=$1; shift
SEED=$1; shift
GENERATE=$1; shift
SIGNIFICANCE=$1; shift
CWD=$PWD

# Make temporary workdir
TMP=$CWD/tmp_${MP}_${SEED}
mkdir -p ${TMP}
cd ${TMP}

# --- Setup CMSSW environment ---
echo ">>> Setting up CMSSW environment"
cp ${CWD}/CMSSW_10_6_26.tgz ${TMP}/
tar -xzf ${TMP}/CMSSW_10_6_26.tgz
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd ${TMP}/CMSSW_10_6_26/src
scramv1 b ProjectRename
scram b -j 8
cmsenv
cd ${TMP}

get_card() {
    echo "Getting datacard and workspace from EOS"
    masspoint="$1"
    xrdcp root://eoscms.cern.ch/${eos}/cards/TChiWZ_Disp-${rew}_${masspoint}/card_TChiWZ_Disp-${rew}_${masspoint}_allEEMM.root ${TMP}/
    xrdcp root://eoscms.cern.ch/${eos}/cards/TChiWZ_Disp-${rew}_${masspoint}/card_TChiWZ_Disp-${rew}_${masspoint}_allEEMM.txt ${TMP}/
    mv ${TMP}/card_TChiWZ_Disp-${rew}_${masspoint}_allEEMM.root ${TMP}/mycard_${masspoint}.root
    mv ${TMP}/card_TChiWZ_Disp-${rew}_${masspoint}_allEEMM.txt ${TMP}/mycard_${masspoint}.txt
}

get_toys() {
    echo "Getting toys file from EOS"
    xrdcp root://eoscms.cern.ch/${toy}/toys/higgsCombineTest.GenerateOnly.mH120.${SEED}.root ${TMP}/
}

save_signif(){
    echo "Sending significance file to EOS"
    masspoint="$1"
    xrdcp ${TMP}/higgsCombineTest.Significance.mH120.${SEED}.root root://eoscms.cern.ch/${toy}/signif/higgsCombineTest.Significance.${masspoint}.${SEED}.root
}

save_toys(){
    echo "Sending toys file to EOS"
    xrdcp ${TMP}/higgsCombineTest.GenerateOnly.mH120.${SEED}.root root://eoscms.cern.ch/${toy}/toys/
}

# The b-only toys are always generated from the same card
if [ "$GENERATE" == 1 ]; then
    echo "Generating toys"
    get_card 175_165_0
    combine -M GenerateOnly -d ${TMP}/mycard_175_165_0.root -t ${NTOYS} --toysFreq --saveToys --seed ${SEED}
    save_toys
fi

# Use the b-only toys as input to compute local significance for MP
if [ "$SIGNIFICANCE" == 1 ]; then
    echo "Computing significance"
    get_card ${MP}
    get_toys
    combine -M Significance -d ${TMP}/mycard_${MP}.root -t ${NTOYS} --toysFreq --toysFile=${TMP}/higgsCombineTest.GenerateOnly.mH120.${SEED}.root --seed ${SEED}
    save_signif ${MP}
fi

cd ${TMP}/..
rm -rf ${TMP}
