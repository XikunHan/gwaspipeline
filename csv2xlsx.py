#!/usr/bin/env python3
###
#  csv2xlsx.py - script for the convert CSV files to Excel tables
#  Copyright (C) 2016 Giulio Genovese
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  Written by Giulio Genovese <giulio.genovese@gmail.com>
###

import argparse, sys, csv, xlsxwriter # from http://www.python-excel.org/

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-d', type=str, default=',')
parser.add_argument('-o', type=str)
parser.add_argument('-i', type=argparse.FileType('r'), nargs='+', default=sys.stdin)
parser.add_argument('-t', type=str, nargs='+')
parser.add_argument('-b', action='store_true', default = False)
parser.add_argument('-f', type=int, nargs=2)
args = parser.parse_args(sys.argv[1:])

if args.d=="tab":
  args.d="\t"

wb = xlsxwriter.Workbook(args.o)
if args.b:
  bold = wb.add_format({'bold': True})

for f in args.i:
  ws = wb.add_worksheet(args.t.pop(0) if args.t else None)
  reader = csv.reader(f,delimiter=args.d)
  for r, row in enumerate(reader):
      for c, col in enumerate(row):
          ws.write(r, c, col)
  if args.b:
    ws.set_row(0, None, bold)
  if args.f:
    ws.freeze_panes(args.f[0], args.f[1])
wb.close()
