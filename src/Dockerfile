FROM jupyter/base-notebook

LABEL Name=zerkel Version=0.0.1
EXPOSE 8888

USER root

ENV ROOT=$HOME/notebook

WORKDIR $ROOT

RUN pip install rise && \
    jupyter-nbextension install rise --py --sys-prefix && \
    jupyter-nbextension enable rise --py --sys-prefix

ADD src/tests src/tests
ADD src/zerkel src/zerkel
ADD src/README.rst src/README.rst
ADD src/setup.py src/setup.py

RUN pip install --no-cache-dir -e src

ADD notebooks notebooks

RUN chown -R $NB_UID:$NB_GID $ROOT

USER $NB_UID

CMD ["start-notebook.sh", "--NotebookApp.token="]