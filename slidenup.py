#!/usr/bin/env python3
import sys
import os
import subprocess
from termcolor import colored
import tempfile

NUPARGS = ['--nup', '3x2', '--landscape']
MERGEARGS = ['--landscape']

TEXPREAMBLE = [
    r'\documentclass[12pt, a4paper]{article}',
    r'\usepackage{multido}',
    r'\usepackage[landscape]{geometry}',
    r'\voffset = -2cm',
    r'\topmargin = 0cm',
    r'\headheight = 1cm',
    r'\headsep = 0cm',
    r'\textheight = 18cm',
    r'\footskip = 0cm',
    r'\usepackage{fancyhdr}',
    r'\pagestyle{fancy}',
    r'\renewcommand{\headrulewidth}{0pt}',
]
TEXDOCUMENT = [
    r'\begin{document}',
    r'\multido{}{\pagecnt}{\vphantom{x}\newpage}',
    r'\end{document}'
]
def TEXLABELS(header, label, pagecnt):
    ret = []
    ret.append(r'\newcommand{\pagecnt}{' + str(pagecnt) + r'}')
    if header:
        ret.append(r'\chead{' + label + r'}')
        ret.append(r'\rhead{\thepage ~/~ ' + str(pagecnt) + r'}')
        ret.append(r'\cfoot{}')
    else:
        ret.append(r'\cfoot{' + label + r'}')
        ret.append(r'\rfoot{\thepage ~/~ ' + str(pagecnt) + r'}')
    return ret

if len(sys.argv) < 3:
    print('Usage:', sys.argv[0], 'output-file', 'input-files')
    sys.exit(1)

FNULL = open(os.devnull, 'w')
def call(args):
    print(colored('Executing', 'green'), colored(args[0], 'blue'), ' '.join(args[1:]))
    #res = subprocess.call(args)
    res = subprocess.call(args, stdout=FNULL, stderr=FNULL)
    if res != 0:
        print('\t', colored('FAILED', 'yellow'))
        return False
    return True
def check_output(args):
    print(colored('Executing', 'green'), colored(args[0], 'blue'), ' '.join(args[1:]))
    try:
        res = subprocess.check_output(args, stderr=FNULL)
    except subprocess.CalledProcessError:
        print('\t', colored('FAILED', 'yellow'))
        return None
    return res

tempdir = tempfile.TemporaryDirectory()
print(colored('Working in temp directory', 'blue'), tempdir.name)

# First nup individual input files
print(colored('N-up-ing individual files together', 'blue'))
infiles = sys.argv[2:]
outfiles = []
for i,infile in enumerate(infiles):
    outfile = os.path.join(tempdir.name, 'nup-{}.pdf'.format(i))
    if not call(['pdfjam'] + NUPARGS + [infile, '--outfile', outfile]):
        print(colored('N-up failed, exiting', 'red'))
        sys.exit(1)
    outfiles.append(outfile)

def number_and_label(infile, outfile, label, header = True):
    print(colored('Numbering and labeling', 'green'), infile)

    # Use pdfinfo to count number of pages
    out = check_output(['pdfinfo', infile])
    if out is None:
        print(colored('Calling pdfinfo failed', 'yellow'))
        return False
    pagecnt = None
    for line in out.decode('utf-8').split('\n'):
        if line.startswith('Pages:'):
            pagecnt = int(line.split()[1])
            break
    if pagecnt is None:
        print(colored('Weird pdfinfo output', 'yellow'))
        return False
    print(pagecnt)

    # Generate tex file for numbering
    texfile = os.path.join(tempdir.name, 'numbering.tex')
    with open(texfile, 'w') as texf:
        texf.writelines(TEXPREAMBLE)
        texf.writelines(TEXLABELS(header, label, pagecnt))
        texf.writelines(TEXDOCUMENT)
    
    # Compile using pdflatex
    if not call(['pdflatex', '-aux_directory='+tempdir.name, '-output-directory='+tempdir.name, texfile]):
        print(colored('Running pdflatex failed', 'yellow'))
        return False

    numfile = os.path.join(tempdir.name, 'numbering.pdf')

    # Merge with input file
    if not call(['pdftk', infile, 'multistamp', numfile, 'output', outfile]):
        print(colored('Combining file with labels failed', 'yellow'))
        return False

    return True

# Number and label each nuped file first
print(colored('Numbering the N-up-ed files individually', 'blue'))
infiles = outfiles
outfiles = []
for i,infile in enumerate(infiles):
    outfile = os.path.join(tempdir.name, 'nup-numbered-{}.pdf'.format(i))
    if not number_and_label(infile, outfile, os.path.basename(sys.argv[2+i]), True):
        print(colored('Numbering and labeling failed, exiting', 'red'))
        sys.exit(1)
    outfiles.append(outfile)


# Merge numbered nuped files together
print(colored('Merging together to form single file', 'blue'))
mergefile = os.path.join(tempdir.name, 'merged.pdf')
if not call(['pdfjam'] + MERGEARGS + outfiles + ['--outfile', mergefile]):
    print(colored('Merge failed, exiting', 'red'))
    sys.exit(1)

# Number and label merged file
print(colored('Numbering the final merged file', 'blue'))
if not number_and_label(mergefile, sys.argv[1], '', False):
    print(colored('Final numbering failed, exiting', 'red'))
    sys.exit(1)

print(colored('Finished, output written to', 'green'), colored(sys.argv[1], 'blue'))

