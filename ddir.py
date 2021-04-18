"""
Compares two directories for files thare missing on either side and runs
a diff command on each file that differs. Prints statistics.
Written by Kevin P. Inscoe - https://github.com/KevinPInscoe/ddir
"""

import filecmp
import sys
import os
from pathlib import Path

def check_path_for_dots(file, pathsep):
    # If one of the directories in this path or the file itself have a
    # leading dot in it's name we want to ignore it (like .git or .terraform)
    paths = str(file).split(pathsep)
    for path in paths:
        if len(path) > 0:
            if path[0] == '.':
                return False

    return True

def compare(filea, fileb, diffcmd):
    if not filecmp.cmp(filea, fileb, shallow=False):
        cmd = diffcmd + " " + filea + " " + fileb
        print("** %s and %s differ:\n" % (filea, fileb))
        os.system(cmd)

    return

def files(dir, pathsep):
    tree = []
    p = Path(dir)
    files = list(Path(dir).rglob('*'))
    for file in files:
        if file.is_file():
            # Ignore files that start with a dot
            if str(file)[0] != '.':
                # Ignore any files in a subdirectory that begins with a dot
                if check_path_for_dots(file, pathsep):
                    thefile = str(file.resolve())
                    tree.append(thefile)

    return tree

def get_file_suffix(file, dir):
    file_suffix = file.replace(dir, "")

    return file_suffix

def compare_tree(dir, tree, comparisondir, bothfilesexisttable):
    # Find files that exists in tree but are missing from the same
    # relative path in comparisondir.
    # Files that exist in both paths get appended to bothfilesexisttable.
    missing = []
    for file in tree:
        filepathsuffix = get_file_suffix(file, dir)
        comparefile = comparisondir + filepathsuffix
        if not os.path.exists(comparefile):
            missing.append(file)
            print("-- Missing %s" % (comparefile))
        else:
            if filepathsuffix not in bothfilesexisttable:
                bothfilesexisttable.append(filepathsuffix)

    return bothfilesexisttable, missing

def compare_directories(dirafiles, dirbfiles, dira, dirb):
    bothfilesexisttable = []
    missinga = []
    missingb = []

    # Find missing files from dira to dirb
    bothfilesexisttable, missinga = compare_tree(dira, dirafiles, dirb, bothfilesexisttable)

    # Find missing files from dirb to dira
    bothfilesexisttable, missingb = compare_tree(dirb, dirbfiles, dira, bothfilesexisttable)

    return bothfilesexisttable, missinga, missingb

def main():
    if len(sys.argv) < 3:
        print("Usage: ddir dir-a dir-b")
        sys.exit(1)

    a = sys.argv[1]
    b = sys.argv[2]

    dira = a.strip()
    dirb = b.strip()

    if not os.path.exists(dira):
        print("Directory a %s does not exist" % (dira))
        sys.exit(1)
    if not os.path.exists(dirb):
        print("Directory b %s does not exist" % (dirb))
        sys.exit(1)

    if os.name == 'nt':
        pathsep = "\\"
        # Assumes cygwin
        diffcmd = "C:\\cygwin64\\bin\\diff --side-by-side --width=120 --color=always"
    else:
        # Assumes unix
        pathsep = "/"
        diffcmd = "diff --side-by-side --width=120 --color=always"

    # Get list of dira files
    dirafiles = files(dira, pathsep)
    # Get list of dirb files
    dirbfiles = files(dirb, pathsep)
    # Build a table of files that are missing
    bothfilesexisttable, missinga, missingb = compare_directories(dirafiles, dirbfiles, dira, dirb)

    # Run diff against those files that are different
    if len(bothfilesexisttable) > 0:
        for file in bothfilesexisttable:
            afile = dira + file
            bfile = dirb + file
            compare(afile, bfile, diffcmd)

    # Print statistics
    print("\n%s files in %s" % (len(dirafiles), dira))
    print("%s files in %s" % (len(dirbfiles), dirb))
    print("%s files missing from %s" % (len(missinga), dira))
    print("%s files missing from %s" % (len(missingb), dirb))
    print("%s files were different" % (len(bothfilesexisttable)))

if __name__ == '__main__':
    main()

