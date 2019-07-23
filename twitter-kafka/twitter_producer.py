#https://www.bmc.com/blogs/working-streaming-twitter-data-using-kafka/
# before you need to create a topic with kafkatopics
#kafka-topics.bat --create --zookeeper 0.0.0.0:2181 --replication-factor 1 --partitions 1 --topic twitter_topic

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import SimpleProducer, KafkaClient
import json
datastore = '../token.json'
def getToken() :
    with open(datastore) as json_file:
        data = json.load(json_file)
        return data
mytoken = getToken()
access_token = mytoken["access_token"]
access_token_secret =  mytoken["access_token_secret"]
consumer_key =  mytoken["consumer_key"]
consumer_secret =  mytoken["consumer_secret"]

class StdOutListener(StreamListener):
    def on_data(self, data):
        producer.send_messages("twitter_topic", data.encode('utf-8'))
        print (data)
        return True
    def on_error(self, status):
        print (status)

kafka = KafkaClient("localhost:9092")
producer = SimpleProducer(kafka)
l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, l)
stream.filter(track="global")

#On pourra vérifier que kafka enregitre bien les messages 
#kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic twitter_topic --from-beginning