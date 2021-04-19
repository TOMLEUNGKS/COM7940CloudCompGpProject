FROM python
COPY requirements.txt /tmp/requirements.txt
WORKDIR /tmp
RUN pip install -r /tmp/requirements.txt &&\
    git clone https://github.com/TOMLEUNGKS/COM7940CloudCompGpProject.git

CMD cd COM7940CloudCompGpProject && git pull origin main && python chatbot.py
