
SHELL=/bin/bash

YELLOW=`tput setaf 3`
RED=`tput setaf 1`
RESET=`tput sgr 0`

OUTDIR='.'


.PHONY: pdf
pdf:	prepare
	pdflatex --output-directory ${OUTDIR} main.tex
	biber ${OUTDIR}/main
	pdflatex --output-directory ${OUTDIR} main.tex
	pdflatex --output-directory ${OUTDIR} main.tex

.PHONY: single
single:	prepare
	pdflatex --output-directory ${OUTDIR} main.tex

.PHONY: prepare
prepare:
	mkdir -p ${OUTDIR}