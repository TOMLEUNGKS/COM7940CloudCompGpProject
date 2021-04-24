FROM python
COPY requirements.txt requirements.txt
COPY chatbot.py chatbot.py
COPY config.ini config.ini
RUN pip install pip update
RUN pip install -r requirements.txt 
CMD python chatbot.py

