from dhooks import Embed, File, Webhook 
from config import Config 
import requests
import os
cc = Config()

class _WebhookX():
    def __init__(self):
        self.webx = Webhook(cc.get_webhook())
        self.webx = Webhook(cc.get_dhooh())
        self.webx.modify(name=cc.get_name(), avatar=requests.get(cc.get_avatar()).content)
