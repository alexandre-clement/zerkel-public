FROM python:3.7.1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        gosu sudo \
        curl make \
        dvipng graphviz \
        latexmk texlive-fonts-recommended texlive-latex-extra texlive-latex-recommended \
        texlive-xetex texlive-science \
        texlive-lang-french lmodern \
        texlive-bibtex-extra \
        git \
        pandoc \
 && pip install 'sphinx'    \
                'sphinx_rtd_theme'    \
                'ipython' \
                'numpydoc'    \
                'matplotlib' \
                'flask' \
                'nbsphinx' \
                'jupyter_client' \
                'ipykernel' \
 && apt-get autoremove -y \
 && rm -rf /var/cache/* \
 && rm -rf /var/lib/apt/lists/*

ADD deliveries deliveries

WORKDIR /deliveries

RUN mkdir -p /docs/source/_static \
 && pdflatex -synctex=1 -interaction=nonstopmode -file-line-error --extra-mem-bot=10000000 final.tex  \
 && bibtex final \
 && pdflatex -synctex=1 -interaction=nonstopmode -file-line-error --extra-mem-bot=10000000 final.tex \
 && pdflatex -synctex=1 -interaction=nonstopmode -file-line-error --extra-mem-bot=10000000 --output-directory='/docs/source/_static' final.tex
WORKDIR /

ADD src/tests src/tests
ADD src/zerkel src/zerkel
ADD src/README.rst src/README.rst
ADD src/setup.py src/setup.py

RUN pip install --no-cache-dir -e src

ADD docs docs

WORKDIR /docs

ADD notebooks source/notebooks

RUN make html

EXPOSE 8080

ENTRYPOINT [ "python" ]
CMD [ "server.py" ]