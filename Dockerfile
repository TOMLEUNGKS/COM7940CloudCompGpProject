FROM python
COPY requirements.txt /requirements.txt
COPY chatbot.py  /chatbot.py
RUN pip install pip update
RUN pip install -r /requirements.txt 
CMD python chatbot.py

