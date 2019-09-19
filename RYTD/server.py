#!/usr/bin/env python3
import socket, threading, mysql.connector, re, signal, json
class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print("New Connection")
    def run(self):
        msg = ""
        while True:
            try:
                data = self.csocket.recv(2048)
            except KeyboardInterrupt:
                print("Thread interupted")
                break
            msg = "".join(data.decode("utf-8").lower().split())
            print(msg)
            answer = ""
            if msg=="bye" or msg=="":
                break
            elif msg.startswith("hello"):
                msg = msg[len("hello"):]
                answer = "Option error - No options implemented yet"
            elif msg.startswith("search"):
                msg = msg[len("search"):]
                urls = []
                try:
                    urls = json.loads(msg)
                except json.decoder.JSONDecodeError:
                    answer = "Argument Error - The argument must be an json array of string urls"
                print(type(urls))
                if type(urls) != type([]):
                    answer = "Argument Error - The argument must be an json array of string urls"
                else:
                    urlPattern = re.compile(URL_REGEX)
                    for url in urls:
                        if not urlPattern.match(url):
                            answer = "Argument Error - At least one of the passed urls wasn't a valid url"
                if answer == "":
                    query = "SELECT url, resolve_to_url FROM links WHERE url IN (%s)" % (",".join(["%s"]*len(urls)))
                    args = tuple(urls)
                    dbCursor.execute(query, args)
                    result = dbCursor.fetchall()
                    data = {}
                    for row in result:
                        data[row[0]] = row[1]
                    answer = json.dumps(data)
            elif msg.startswith("check"):
                msg = msg[len("check"):]
                answer = "Command error - Not implemented yet"
            elif msg.startswith("mark"):
                msg = msg[len("mark"):]
                answer = "Command error - Not implemented yet"
            elif msg.startswith("servers"):
                answer = "Command error - Not implemented yet"
            elif msg.startswith("help"):
                answer = "hello [option list] - initiates session, no option introduced at the moment, planning options such as user has a subscription for a special service\nsearch [list of urls] - searches for the urls that were passed as an argument in the database and returns the best quality url alternative for the urls in the order they were passed\nmark [list of urls] - markes the given urls to be checked for availability\nservers - returns a list of urls or ip addresses for servers who are included in the video url network and function as a mirror server (not-implemented)\nbye - tell server to close the connection\nhelp - prints this page"
            else:
                answer = "Command error - Invalid Command"
            self.csocket.send(answer.encode("utf-8"))
        print("Client Disconnected")
        self.csocket.close()

HOST = ""
PORT = 10000

# FROM https://stackoverflow.com/a/840014
URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:"".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))

print("Server started")

#f = open("password", "r")
password = "Tabasco1!"

dbConnection = mysql.connector.connect(
    host="localhost",
    user="riedler",
    passwd=password,
    database="VideoURLs"
)

#f.close()

dbCursor = dbConnection.cursor()

client_sockets = []

print("Database Connection Established")

try:
    while True:
        server.listen(1)
        clientsock, clientAddress = server.accept()
        client_sockets.append(clientsock)
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()
except KeyboardInterrupt:
    pass

print("Closing Client Connections...")

for client_socket in client_sockets:
    try:
        client_socket.send("bye".encode("UTF-8"))
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
    except OSError:
        continue


print("Shutting Down Server...")

server.close()


print("Closing MySQL Connection")

dbCursor.close()
dbConnection.close()
