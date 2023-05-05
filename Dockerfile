FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y libaio1 netcat dos2unix
WORKDIR /opt/oracle
RUN wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip && \
    unzip instantclient-basiclite-linuxx64.zip && rm -f instantclient-basiclite-linuxx64.zip && \
    cd /opt/oracle/instantclient* && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci && \
    echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf && ldconfig
WORKDIR /alphilia/app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /alphilia/app
LABEL name=$IMAGE_NAME
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
