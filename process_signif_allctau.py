#!/usr/bin/env python3
import os, argparse, re, uproot
import numpy as np
from tqdm import tqdm

import glob

# Directory configuration per ctau (supports glob patterns for multiple directories)
base_path = "/eos/cms/store/group/phys_susy/SOS/limits_TChiWZ_neg_static_20251124_toys"
ctau_dirs = {
    "0":    [f"{base_path}/signif/ctau0/"],
    "0p1":  [f"{base_path}/signif/ctau0p1/"],
    "1p0":  [f"{base_path}/signif/", f"{base_path}_1p0/M*00/"],
    "10p0":  [f"{base_path}/signif/"],
    "100p0":  [f"{base_path}/signif/"],
}

n_jobs = 330                    # number of toy jobs per mass point
n_toys_per_file = 1000          # number of toys in each ROOT file


def get_directories_for_ctau(ctau):
    """Expand glob patterns and return list of existing directories for a ctau."""
    dirs = []
    for pattern in ctau_dirs.get(ctau, []):
        expanded = glob.glob(pattern)
        if expanded:
            dirs.extend(expanded)
        elif os.path.isdir(pattern):  # Not a glob, just a regular path
            dirs.append(pattern)
    return dirs


def find_file_across_dirs(fname, directories):
    """Search for a file across multiple directories. Return path if found, None otherwise."""
    for d in directories:
        path = os.path.join(d, fname)
        if os.path.exists(path):
            return path
    return None

# Base mass points (without ctau suffix)
base_signals = [
    "100_50",  "100_60",     "100_70",   "100_80",   "100_85",   "100_90",   "100_92p5",   "100_95",   "100_97",   "100_98",   "100_98p5",   "100_99",   "100_99p2",   "100_99p4",  
    "125_75",  "125_85",     "125_95",  "125_105",  "125_110",  "125_115",  "125_117p5",  "125_120",  "125_122",  "125_123",  "125_123p5",  "125_124",  "125_124p2",  "125_124p4",  
    "150_100",  "150_110",  "150_120",  "150_130",  "150_135",  "150_140",  "150_142p5",  "150_145",  "150_147",  "150_148",  "150_148p5",  "150_149",  "150_149p2",  "150_149p4",  
    "175_125",  "175_135",  "175_145",  "175_155",  "175_160",  "175_165",  "175_167p5",  "175_170",  "175_172",  "175_173",  "175_173p5",  "175_174",  "175_174p2",  "175_174p4",  
    "200_150",  "200_160",  "200_170",  "200_180",  "200_185",  "200_190",  "200_192p5",  "200_195",  "200_197",  "200_198",  "200_198p5",  "200_199",  "200_199p2",  "200_199p4",  
    "225_175",  "225_185",  "225_195",  "225_205",  "225_210",  "225_215",  "225_217p5",  "225_220",  "225_222",  "225_223",  "225_223p5",  "225_224",  "225_224p2",  "225_224p4",  
    "250_200",  "250_210",  "250_220",  "250_230",  "250_235",  "250_240",  "250_242p5",  "250_245",  "250_247",  "250_248",  "250_248p5",  "250_249",  "250_249p2",  "250_249p4",  
    "275_225",  "275_235",  "275_245",  "275_255",  "275_260",  "275_265",  "275_267p5",  "275_270",  "275_272",  "275_273",  "275_273p5",  "275_274",  "275_274p2",  "275_274p4",  
    "300_250",  "300_260",  "300_270",  "300_280",  "300_285",  "300_290",  "300_292p5",  "300_295",  "300_297",  "300_298",  "300_298p5",  "300_299",  "300_299p2",  "300_299p4",  
    "325_275",  "325_285",  "325_295",  "325_305",  "325_310",  "325_315",  "325_317p5",  "325_320",  "325_322",  "325_323",  "325_323p5",  "325_324",  "325_324p2",  "325_324p4",  
    "350_300",  "350_310",  "350_320",  "350_330",  "350_335",  "350_340",  "350_342p5",  "350_345",  "350_347",  "350_348",  "350_348p5",  "350_349",  "350_349p2",  "350_349p4",  
    "375_325",  "375_335",  "375_345",  "375_355",  "375_360",  "375_365",  "375_367p5",  "375_370",  "375_372",  "375_373",  "375_373p5",  "375_374",  "375_374p2",  "375_374p4",  
    "400_350",  "400_360",  "400_370",  "400_380",  "400_385",  "400_390",  "400_392p5",  "400_395",  "400_397",  "400_398",  "400_398p5",  "400_399",  "400_399p2",  "400_399p4",  
    "425_375",  "425_385",  "425_395",  "425_405",  "425_410",  "425_415",  "425_417p5",  "425_420",  "425_422",  "425_423",  "425_423p5",  "425_424",  "425_424p2",  "425_424p4",  
    "450_400",  "450_410",  "450_420",  "450_430",  "450_435",  "450_440",  "450_442p5",  "450_445",  "450_447",  "450_448",  "450_448p5",  "450_449",  "450_449p2",  "450_449p4",  
    "475_425",  "475_435",  "475_445",  "475_455",  "475_460",  "475_465",  "475_467p5",  "475_470",  "475_472",  "475_473",  "475_473p5",  "475_474",  "475_474p2",  "475_474p4",  
    "500_450",  "500_460",  "500_470",  "500_480",  "500_485",  "500_490",  "500_492p5",  "500_495",  "500_497",  "500_498",  "500_498p5",  "500_499",  "500_499p2",  "500_499p4",  
    "525_475",  "525_485",  "525_495",  "525_505",  "525_510",  "525_515",  "525_517p5",  "525_520",  "525_522",  "525_523",  "525_523p5",  "525_524",  "525_524p2",  "525_524p4", 
    "550_500",  "550_510",  "550_520",  "550_530",  "550_535",  "550_540",  "550_542p5",  "550_545",  "550_547",  "550_548",  "550_548p5",  "550_549",  "550_549p2",  "550_549p4",  
    "575_525",  "575_535",  "575_545",  "575_555",  "575_560",  "575_565",  "575_567p5",  "575_570",  "575_572",  "575_573",  "575_573p5",  "575_574",  "575_574p2",  "575_574p4",  
    "600_550",  "600_560",  "600_570",  "600_580",  "600_585",  "600_590",  "600_592p5",  "600_595",  "600_597",  "600_598",  "600_598p5",  "600_599",  "600_599p2",  "600_599p4",
]

# All ctau hypotheses (must match keys in ctau_dirs)
ctau_values = list(ctau_dirs.keys())

# Build full list of expected signals (mass_ctau combinations)
expected_signals = [f"{mp}_{ctau}" for ctau in ctau_values for mp in base_signals]
print(f"Total expected signals: {len(expected_signals)} ({len(base_signals)} mass points × {len(ctau_values)} ctau values)")


def get_significance(path):
    """Return numpy array of 'limit' branch."""
    try:
        with uproot.open(path) as f:
            return f["limit"]["limit"].array(library="np")
    except Exception as e:
        return np.full(n_toys_per_file, np.nan)


parser = argparse.ArgumentParser()
parser.add_argument("--dryrun", action='store_true', default=False, help="Only check for missing significance files")
args = parser.parse_args()

if __name__ == '__main__':
    # ---------------------------
    # Step 1. Discover mass points (across all ctau)
    # ---------------------------
    mass_points_found = set()
    files_by_ctau = {}  # Track which files exist per ctau
    
    print("Scanning directories...")
    for ctau in ctau_values:
        dirs = get_directories_for_ctau(ctau)
        print(f"  ctau={ctau}: {len(dirs)} directories")
        for d in dirs:
            print(f"    - {d}")
        
        files_by_ctau[ctau] = []
        for d in dirs:
            if os.path.isdir(d):
                files = [f for f in os.listdir(d) if f.startswith("higgsCombineTest.Significance")]
                files_by_ctau[ctau].extend(files)
        
        # Extract mass points from filenames for this ctau
        points = set(re.findall(r"Significance\.([^.]+)\.", " ".join(files_by_ctau[ctau])))
        mass_points_found.update(points)
    
    mass_points_found = sorted(mass_points_found)
    print(f"\nFound {len(mass_points_found)} unique (mass, ctau) combinations across all directories.")

    # Group by ctau for reporting
    for ctau in ctau_values:
        points_for_ctau = [mp for mp in mass_points_found if mp.endswith(f"_{ctau}")]
        print(f"  ctau={ctau}: {len(points_for_ctau)} mass points")

    # Report extra or missing points
    extra_points = sorted(set(mass_points_found) - set(expected_signals))
    missing_points = sorted(set(expected_signals) - set(mass_points_found))

    if extra_points:
        print(f"\n⚠️ Found {len(extra_points)} unexpected (mass, ctau) combinations:")
        for mp in extra_points:
            print(f"  + {mp}")

    if missing_points:
        print(f"\n⚠️ Missing {len(missing_points)} expected (mass, ctau) combinations:")
        # Group by ctau for clearer output
        for ctau in ctau_values:
            missing_for_ctau = [mp for mp in missing_points if mp.endswith(f"_{ctau}")]
            if missing_for_ctau:
                print(f"  ctau={ctau}: {len(missing_for_ctau)} missing")
                for mp in missing_for_ctau[:5]:  # Show first 5
                    print(f"    - {mp}")
                if len(missing_for_ctau) > 5:
                    print(f"    ... and {len(missing_for_ctau) - 5} more")

    # ---------------------------
    # Step 2. Check completeness (for all ctau)
    # ---------------------------
    print("\n" + "="*60)
    print("Checking file completeness...")
    print("="*60)
    
    mp_tocheck = sorted(set(mass_points_found) - set(extra_points))
    missing_files = {}  # Dict: ctau -> list of (masspoint, seed)
    
    for ctau in ctau_values:
        missing_files[ctau] = []
    
    for mp in mp_tocheck:
        # Determine which ctau this mass point belongs to
        ctau_for_mp = None
        for ctau in ctau_values:
            if mp.endswith(f"_{ctau}"):
                ctau_for_mp = ctau
                break
        
        if ctau_for_mp is None:
            continue
            
        # Get directories for this ctau
        dirs = get_directories_for_ctau(ctau_for_mp)
        
        for i in range(n_jobs):
            fname = f"higgsCombineTest.Significance.{mp}.{i}.root"
            if find_file_across_dirs(fname, dirs) is None:
                missing_files[ctau_for_mp].append((mp, i))

    total_missing = sum(len(v) for v in missing_files.values())
    
    if total_missing > 0:
        print(f"\n❌ Missing {total_missing} files total:")
        for ctau in ctau_values:
            if missing_files[ctau]:
                print(f"\n  ctau={ctau}: {len(missing_files[ctau])} missing files")
                print("  Format: (masspoint, seed) --> can be copied into resub.sub for resubmission:")
                for mp, seed in missing_files[ctau][:20]:  # Show first 20 per ctau
                    print(f"    {mp}, {seed}")
                if len(missing_files[ctau]) > 20:
                    print(f"    ... and {len(missing_files[ctau]) - 20} more")
    else:
        print("\n✅ All expected files found for all ctau values.")

    if not args.dryrun:
        # ---------------------------
        # Step 3. Compute max significance per toy (across all mass points AND all ctau)
        # ---------------------------
        print("\n" + "="*60)
        print("Computing maximum significance per toy...")
        print("="*60)
        
        n_total_toys = n_jobs * n_toys_per_file
        max_sig = np.full(n_total_toys, -np.inf)

        # Process all mass points across all ctau values
        all_points_to_process = [mp for mp in mass_points_found if mp not in extra_points]
        
        for mp in tqdm(all_points_to_process, desc="Processing all (mass, ctau) points"):
            # Determine ctau for this mass point
            ctau_for_mp = None
            for ctau in ctau_values:
                if mp.endswith(f"_{ctau}"):
                    ctau_for_mp = ctau
                    break
            
            if ctau_for_mp is None:
                continue
                
            dirs = get_directories_for_ctau(ctau_for_mp)
            
            sig_all = np.full(n_total_toys, np.nan)
            for i in range(n_jobs):
                fname = f"higgsCombineTest.Significance.{mp}.{i}.root"
                path = find_file_across_dirs(fname, dirs)
                if path:
                    sig = get_significance(path)
                else:
                    sig = np.full(n_toys_per_file, np.nan)

                start = i * n_toys_per_file
                end = start + len(sig)
                sig_all[start:end] = sig

            # Update maximum across all mass points and ctau values
            max_sig = np.fmax(max_sig, sig_all)

        # ---------------------------
        # Step 4. Save results
        # ---------------------------
        output_file = "max_significance_per_toy_all_ctau.npy"
        np.save(output_file, max_sig)
        print(f"\n✅ Saved {n_total_toys} max significance values to {output_file}")
        print(f"   (maximum taken across {len(all_points_to_process)} (mass, ctau) combinations)")
        
        # Print some statistics
        valid_mask = ~np.isnan(max_sig) & ~np.isinf(max_sig)
        if np.any(valid_mask):
            print(f"\n   Statistics of max significance:")
            print(f"   - Valid entries: {np.sum(valid_mask)} / {n_total_toys}")
            print(f"   - Min: {np.min(max_sig[valid_mask]):.4f}")
            print(f"   - Max: {np.max(max_sig[valid_mask]):.4f}")
            print(f"   - Mean: {np.mean(max_sig[valid_mask]):.4f}")
            print(f"   - Median: {np.median(max_sig[valid_mask]):.4f}")