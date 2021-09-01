
SHELL=/bin/bash

YELLOW=`tput setaf 3`
RED=`tput setaf 1`
RESET=`tput sgr 0`

OUTDIR='out'


.PHONY: pdf
pdf:
	mkdir -p ${OUTDIR}
	pdflatex --output-directory ${OUTDIR} main.tex
	bibtex ${OUTDIR}/main
	pdflatex --output-directory ${OUTDIR} main.tex
	pdflatex --output-directory ${OUTDIR} main.tex

.PHONY: single
single:
	pdflatex --output-directory ${OUTDIR} main.tex
