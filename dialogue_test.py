import socket
import time
import requests
import json


access_token = ''
        

# get access to COTOHA webAPI
def get_access_to_COTOHA():
    headers = {
        'Content-Type': 'application/json',
    }
    
    
    data = '{\
                "grantType": "client_credentials", \
                "clientId": "XcfxEBpUO4H1E6l6GkrIEcP9varJAuma", \
                "clientSecret": "DYeyWcJr2PHLy89U"\
            }'
        
    response = requests.post('https://api.ce-cotoha.com/v1/oauth/accesstokens', headers=headers, data=data)
    
    print(response.json()) # JSON files about access information
    global access_token
    access_token = response.json()['access_token']

# invoke keyword API
def keywordExtraction (input_Sentence):
    headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Authorization': 'Bearer '+access_token, # access_token is valid only for 24 hours
    }

    data = '{\
        "document":"' +input_Sentence+'",\
        "type": "default","do_segment":true,"max_keyword_num":5}'
    response = requests.post('https://api.ce-cotoha.com/api/dev/nlp/v1/keyword', headers=headers, data=data.encode('utf-8'))
    
    print(response.json())

# invoke NER API    
def named_entity_extraction (input_Sentence):
    headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Authorization': 'Bearer '+access_token, # access_token is valid only for 24 hours
    }

    data = '{\
        "sentence":"' +input_Sentence+'",\
        "type": "default"}'
    response = requests.post('https://api.ce-cotoha.com/api/dev/nlp/v1/ne', headers=headers, data=data.encode('utf-8'))
    
    print(response.json())

    for i in response.json()['result']:
        if i['class'] == 'PSN':
            global guest_name 
            guest_name = response.json()['result'][0]['form']
            
# invoke sentence type API          
def sentence_type_classification (input_Sentence):
    headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Authorization': 'Bearer '+access_token, # access_token is valid only for 24 hours
    }

    data = '{\
        "sentence":"' +input_Sentence+'",\
        "type": "default"}'
    response = requests.post('https://api.ce-cotoha.com/api/dev/nlp/v1/sentence_type', headers=headers, data=data.encode('utf-8'))
    
    print(response.json())

    for i in response.json()['result']['dialog_act']:
        if i == 'agreement':
            global speech_act
            speech_act = 'agreement'
 
class SpeechRecognitionController(object):
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))

    def disconnect(self):
        self.sock.close()

    def send_command(self,command):
        command_ln = command + "\n"
        self.sock.send(command_ln.encode('utf-8'))
        print(command_ln.encode('utf-8'))

    def sppech_get(self):
        msg_dec = ""
        while msg_dec.startswith('result:') == False:
            msg = self.sock.recv(1024)
            msg_dec = msg.decode("utf-8")
            if msg_dec.startswith('result:') == True:
                return msg_dec
                break
            time.sleep(0.5)

class SpeechGenerator(object):
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))

    def disconnect(self):
        self.sock.close()

    def send_command(self,command):
        command_ln = command + "\n"
        self.sock.send(command_ln.encode('utf-8'))

    def say(self,message):
        m_tag = "<speak><amazon:effect phonation='soft' vocal-tract-length='-15%'>{}</amazon:effect></speak>"
        message_f = m_tag.format(message)
        message_dict = {"engine":"POLLY-SSML", "speaker":"Mizuki",  "text":message_f}
        message_json = json.dumps(message_dict)
        #音声メッセージを発信
        robot_SpeechGenerator.send_command(message_json)

def aisatsu ():
    robot_SpeechGenerator.say("こんにちは、ロボットの翔子と申します。本日は、お客さまにあった観光地をお勧めさせていただきますので、よろしくお願いします。")
    robot_SpeechGenerator.say("お客様のお名前をお聞きしてよろしいでしょうか？")
    msg_d = robot_SpeechRecognition_controller.sppech_get()
    named_entity_extraction (msg_d.splitlines()[0][7:])
    robot_SpeechGenerator.say(guest_name + "様ですよね。本日はよろしくお願いします")
    robot_SpeechGenerator.say(guest_name + "さまが２つの候補としてお選びになった観光地は," + placeA + "と" +placeB + "でよろしいでしょうか？")
    msg_d = robot_SpeechRecognition_controller.sppech_get()
    sentence_type_classification (msg_d.splitlines()[0][7:])
    if speech_act == 'agreement':
        robot_SpeechGenerator.say("２つともいいところですよね！　私もこの中ならこの２つを選びます。")
        
def spot_instruction(placeA, placeB):
    spot_info = {'国立民族学博物館':'紹介文はAです', \
                 '茨城私立川端康成文学館':'紹介文はBです', \
                 'spotC':'紹介文はCです'}
    if spot_info[placeA]:
        robot_SpeechGenerator.say(spot_info[placeA])
    if spot_info[placeB]:
        robot_SpeechGenerator.say(spot_info[placeB])
        
# def q_and_a ():

# def reason ():
        
# def end ():


if __name__ == "__main__":
    # connect with external API
    get_access_to_COTOHA()
    
    #各システムに接続
    robot_SpeechRecognition_controller = SpeechRecognitionController("150.65.239.80", 8888)
    robot_SpeechGenerator = SpeechGenerator("150.65.239.80", 3456)

    placeA = "国立民族学博物館"
    placeB = "茨城私立川端康成文学館"
    
    # #音声認識停止
    # robot_SpeechRecognition_controller.send_command("stop")

    # #音声認識開始
    # time.sleep(6)
    # robot_SpeechRecognition_controller.send_command("start")
    
    # dialogue
    aisatsu ()
    spot_instruction (placeA, placeB)
    # q_and_a ():
    # reason ():
    # end ():
    
    # while True:
    #     # msg_d = robot_SpeechRecognition_controller.sppech_get()
        
    #     if msg_d.splitlines()[0] == 'result:終わり':
    #         break
    #     print("msg_d:" + msg_d)
        
    #     print('\n')

    #各システム切断
    robot_SpeechRecognition_controller.disconnect()
    # robot_SpeechGenerator.disconnect()
    print('\nEnd')