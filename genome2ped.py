#!/usr/bin/env python3
"""
   genome2ped.py - create a plink ped file from a plink genome file
   Copyright (C) 2016 Giulio Genovese

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.

   Written by Giulio Genovese <giulio.genovese@gmail.com>
"""

import argparse, pandas as pd

parser = argparse.ArgumentParser(description = 'genome2ped.py: create a plink ped file from a plink genome file (Oct 3rd 2016)', add_help = False, usage = 'genome2ped.py [options]')
parser.add_argument('--genome', metavar = '<in.genome>', type = str, required = True, help = 'Specify genome file')
parser.add_argument('--zip', action = 'store_true', default = False, help = 'whether input genome file is compressed [FALSE]')
parser.add_argument('--fam', metavar = '[filename]', type = str, help = 'Specify fam file')
parser.add_argument('--out', metavar = '[filename]', type = str, required = 'True', help = 'Specify output filename')
parser.add_argument('--pdf', metavar = '[filename]', type = str, help = 'Specify output filename for pdf')
parser.add_argument('--par-thr', metavar = 'FLOAT', type = float, default = 0.37, help = 'maximum Z0 for parent child duos [0.37]')
parser.add_argument('--sib-thr', metavar = 'FLOAT', type = float, default = 0.7, help = 'minimum Z0 for siblings [0.7]')
parser.add_argument('--pi-hat', metavar = 'FLOAT', type = float, default = 0.15, help = 'minimum PI_HAT [0.15]')

try:
  parser.error = parser.exit
  args = parser.parse_args()
except SystemExit:
  parser.print_help()
  exit(2)

if args.zip:
  df = pd.read_csv(args.genome, delim_whitespace = True, compression = 'gzip', low_memory = False)
else:
  df = pd.read_csv(args.genome, delim_whitespace = True, low_memory = False)

if df.empty:
  exit()

fam = pd.read_csv(args.fam, delim_whitespace = True, header = None, names = ['FID', 'IID', 'PAT', 'MAT', 'SEX', 'PHE'], low_memory = False)
sex = {(x[0], x[1]): x[2] for x in zip(fam['FID'], fam['IID'], fam['SEX'])}
phe = {(x[0], x[1]): x[2] for x in zip(fam['FID'], fam['IID'], fam['PHE'])}

df = df[df['PI_HAT'] > args.pi_hat] # subset the dataframe
if df.empty:
  exit()
dflite = df[df['Z0'] < args.sib_thr] # generous threshold for siblings and parents

# generate a dictionary structure for each sample using the late version of the database
parents = {x:[] for x in sex}
rels = {x:[] for x in sex}

# for each sample check whether 
for idx in dflite.index:
  if dflite['Z0'][idx] < args.par_thr:
    parents[(dflite['FID1'][idx], dflite['IID1'][idx])] += [(dflite['FID2'][idx], dflite['IID2'][idx])]
    parents[(dflite['FID2'][idx], dflite['IID2'][idx])] += [(dflite['FID1'][idx], dflite['IID1'][idx])]
  rels[(dflite['FID1'][idx], dflite['IID1'][idx])] += [(dflite['FID2'][idx], dflite['IID2'][idx])]
  rels[(dflite['FID2'][idx], dflite['IID2'][idx])] += [(dflite['FID1'][idx], dflite['IID1'][idx])]

trios = []
for proband in parents:
  # test all pairs of parents
  x = parents[proband]
  while x:
    a = x.pop()
    for b in x:
      if not a in rels[b]:
        if sex[a] == 1 and sex[b] == 2:
          trios += [(proband[0], proband[1], a[1], b[1], sex[proband], phe[proband])]
        if sex[a] == 2 and sex[b] == 1:
          trios += [(proband[0], proband[1], b[1], a[1], sex[proband], phe[proband])]

if trios:
  pd.DataFrame(trios).to_csv(args.out, header = ['FID', 'IID', 'PAT', 'MAT', 'SEX', 'PHE'], index = False, sep = '\t')

if args.pdf:
  import numpy as np
  from matplotlib.backends.backend_pdf import PdfPages
  from matplotlib.patches import Polygon
  with PdfPages(args.pdf) as pdf:
    ax = df.plot(kind='scatter', x='PI_HAT', y='Z1', xlim=(0,1), ylim=(0,1))
    ax.set_xlabel('Proportion IBD (PI_HAT)')
    ax.set_ylabel('Proportion IBD1 (Z1)')
    ax.axvline(args.pi_hat, color='r', linestyle='--', lw=2)
    pts = np.array([[1,0], [1,1], [1/2,1]])
    p = Polygon(pts, color='gray', alpha=1/2, closed=True)
    ax.add_patch(p)
    pts = np.array([[0,0], [0,1], [1/2,1]])
    p = Polygon(pts, color='gray', alpha=1/2, closed=True)
    ax.add_patch(p)
    pdf.savefig(ax.get_figure())
