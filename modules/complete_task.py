import Chatrooms


def main(log, graph, sender_name, sender_socket, room):
    
    class send:
    	def __init__(self, message):
    		self.room = room
    		self.server_name = "Server"
    		self.server_socket = list(room.client_list.keys())[0]
    		Chatrooms.message_broadcast(self.room, self.server_name, self.server_socket, message)
    
    username = sender_name
    
    BUFFER_SIZE = 2048
    
    
    send("return " + "What's the id of the task you completed?")
    id_number = sender_socket.recv(BUFFER_SIZE).decode()

    graph.run(f"\
              MATCH (t: Task)-[*]->(u: User)\
              WHERE id(t) = {id_number}\
              AND u.name = '{username}'\
              SET t.completed = 'True'\
              ", id_number=id_number, username=username)


    send("Task completed")

    completed = graph.run(f"\
                          MATCH (t: Task)-[*]->(T)-[r: link]->(u)\
                          WHERE u.name = '{username}'\
                          AND T.name= 'TaskMaster'\
                          RETURN (t.completed)\
                          ", username=username).evaluate()


    if completed == 'True':

        graph.run(f"\
                  MATCH (t: Task)-[r: Task]->(T)-[R: link]->(u)\
                  WHERE u.name = '{username}'\
                  AND T.name = 'TaskMaster'\
                  AND t.completed = 'True'\
                  DELETE r\
                  ")

        graph.run(f"\
                  MATCH (t: Task),\
                  (TC)-[r: link]->(T)-[R: link]->(u)\
                  WHERE NOT (t)-[*]-()\
                  AND u.name = '{username}'\
                  AND TC.name= 'TaskCompleted'\
                  AND t.completed = 'True'\
                  AND T.name = 'TaskMaster'\
                  CREATE (t)-[l: link]->(TC)\
                  ", username=username)
