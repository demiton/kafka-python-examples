# kafka-python-examples
# installation Zookeeper sur windows 10

1. Télécharger la dernière version stable de zookeeper. En ce moment: [ttp://apache.mediamirrors.org/zookeeper/stable/apache-zookeeper-3.5.5-bin.tar.gz ](ttp://apache.mediamirrors.org/zookeeper/stable/apache-zookeeper-3.5.5-bin.tar.gz )
2. Décompresser le fichier avec 7zip dans un répertoire à la racine : `C:\apache-zookeeper-3.5.5\`
3. Créer un fichier zoo.cfg dans le dosser `/conf` de zookeeper et insérer : 
```
tickTime=2000
# dataDir : On indiquera le chemin associé à son installation perso, il faudra aussi créer un dossier /tmp, dans mon cas
dataDir=/apache-zookeeper-3.5.5/apache-zookeeper-3.5.5-bin/tmp
clientPort=2181
```
4. Ajouter un chemin vers les binaires de zoopkeeper dans les variables systemes:
  * On créera une variable systeme : `ZOOKEEPER_HOME = C:\apache-zookeeper-3.5.5\apache-zookeeper-3.5.5-bin`
  * On ajoutera la variable dans la variable system path : `%ZOOKEEPER_HOME%\bin`

5. On peut ainsi lancer un serveur zookeeper simplement en ligne de commande avec : `zkserver`

## Connexion au server zookeeper

```
zkCli -server 127.0.0.1:2181
```

### Lister les noeuds présents : 

Une fois connecté au server via zkCli, on peut lister les noeuds
```
ls /
```

### Créer un nouveau noeud

```
create /myZNode node-1
```
on affiche sa valeur  : 

```
get /myZNode
```

#Installation Kafka server

1. Télécharger Kafka depuis : [http://apache.crihan.fr/dist/kafka/2.3.0/kafka_2.12-2.3.0.tgz ](http://apache.crihan.fr/dist/kafka/2.3.0/kafka_2.12-2.3.0.tgz )
2. Décompresser le tgz à la racine : `C:\kafka_2.3.0 `
3. Dans le dossier `C:\kafka_2.3.0 `, créer un dossier `\logs`
4. Modifier le fichier `config\server.properties` en remplacant la ligne `log.dirs=/tmp/kafka-logs` par `log.dirs=C:\kafka_2.3.0\logs`


## Lancer un server Kafka
__Le serveur zookeeper doit déja être lancer avant de démarrer un serveur Kafka__

Dans le répertoire bin du dossier `C:\kafka_2.3.0 `, vous tapez : 
```
.\bin\windows\kafka-server-start.bat .\config\server.properties
```

Une fois lancé, on pourra verifier que le server est bien connecté à zookeeper en faisant `ls /l` dans zkcli, on devrait avoir : 
```
[zk: 127.0.0.1:2181(CONNECTED) 7] ls /
[admin, brokers, cluster, config, consumers, controller, controller_epoch, isr_change_notification, latest_producer_id_block, log_dir_event_notification, myZNode, zookeeper]
```

### Creation d'un topic
Un topic kafka est une catégorie de donnée ou kafka va stocker les infos qu'il reçoit
Dans le repertoire `\bin\windows`, on lance la commande : 

```
kafka-topics.bat --create --zookeeper 0.0.0.0:2181 --replication-factor 1 --partitions 1 --topic topic1
```
(ou 0.0.0.0 peut parfois etre remplacé par localhost)


#installation kafka-python ( python 3) Python Client for kafka
```
pip install kafka-python
```

## Produire des données avec le producer de Kafka via un script python

On crée un nouveau topic où seront stockées les données produites : 

```
kafka-topics.bat --create --zookeeper 0.0.0.0:2181 --replication-factor 1 --partitions 1 --topic topic-source
```
Dans un fichier `producer.py` , on insère les lignes suivantess : 
```
from time import sleep
from json import dumps
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

for e in range(1000):
    data = {'number' : e}
    producer.send('topic_source', value=data)
    sleep(5)
```

## Consommer des données provenant avec Kafka via python

On stockera les données lues par kafka dans un serveur mongodb
Il faudra l'installer si necessaire : [https://www.mongodb.com/download-center/community](https://www.mongodb.com/download-center/community)

Une fois installer, MongoDB server devrait se lancer automatiquement avec le client Compass

On créé un fichier `consumer.py` tel que : 
```
from kafka import KafkaConsumer
from pymongo import MongoClient
from json import loads

consumer = KafkaConsumer(
    'topic_source',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))

client = MongoClient('localhost:27017')
collection = client.topic_source.topic_source

for message in consumer:
    message = message.value
    print(message)
    collection.insert_one(message)
    print('{} added to {}'.format(message, collection))

```

## Demarrer les tests

1. dans un nouveau terminal , on lance la commande `python producer.py`
2. dans un autre terminal, on lance la commande `python consumer.py`

On pourra alors vérifier que Kafka produit et consomme bien les données, le terminal devrait afficher des logs : 

```
{'number': 0}
{'number': 0, '_id': ObjectId('5d36fb8f1b1e95494501607b')} added to Collection(Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'topic_source'), 'topic_source')
{'number': 1}
{'number': 1, '_id': ObjectId('5d36fb8f1b1e95494501607c')} added to Collection(Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'topic_source'), 'topic_source')
{'number': 2}
{'number': 2, '_id': ObjectId('5d36fb8f1b1e95494501607d')} added to Collection(Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'topic_source'), 'topic_source')
...
```

En allant sur le client Compass, une nouvelle catégorie devrait etre apparue : `topic_source` où l'on retoruvera les logs receptionnés par Kafka.

Sources : 
* [https://towardsdatascience.com/kafka-python-explained-in-10-lines-of-code-800e3e07dad1](https://towardsdatascience.com/kafka-python-explained-in-10-lines-of-code-800e3e07dad1)