import Chatrooms
import os
import sys
import inspect


def main(log, graph, journal_title, date_format, sender_name, sender_socket, room):

    class send:
    	def __init__(self, message):
    		self.room = room
    		self.server_name = "Server"
    		self.server_socket = list(room.client_list.keys())[0]
    		Chatrooms.message_broadcast(self.room, self.server_name, self.server_socket, message)
    
    username = sender_name
    
    BUFFER_SIZE = 2048
    
    is_journal_created_today = graph.run(f"MATCH (j: Journal), (u: User), (J: JournalMaster), (j: Journal), (j)-[*]->(J)-[r: link]->(u) WHERE j.name = '{journal_title}' AND u.name = '{username}' RETURN j.is_journal_created_today ", journal_title=journal_title, username=username).evaluate()


    if is_journal_created_today == 1:

        today  =  graph.run(f"\
                        MATCH (u: User),\
                        (j: Journal),\
                        (J: JournalMaster)\
                        WHERE j.name = '{journal_title}'\
                        AND u.name = '{username}'\
                        AND (j)-[*]->(J)-[*]->(u)\
                        RETURN j\
                        ", journal_title=journal_title).evaluate()
        
        journal_body = today["body"]
        journal_name = today["name"]

        mood = today["mood"]
        anxiety = today["anxiety"]
        depression = today["depression"]
        energy = today["energy"]

        send(f"You have already created a journal today, here it is\n Journal title: {journal_title}\n Body: {journal_body}\n Mood: {mood}\n Anxiety: {anxiety}\n Depression: {depression}\n Energy: {energy}\n")


    elif is_journal_created_today is None:

        graph.run(f"MATCH (u: User), (J: JournalMaster), (J)-[s: link]->(u) WHERE u.name = '{username}' CREATE (j: Journal)-[r: Journal_of]->(J) SET j.name = '{journal_title}', j.is_journal_created_today = 1", journal_title=journal_title, username=username)
        
        
        send(f"\n Let's create a new Journal entry\n Journal title: {journal_title}\n Journal body?\n")
        
        send("return "+"Journal body?")
        journal_body = sender_socket.recv(BUFFER_SIZE).decode()

        send(journal_body + "\n")

        graph.run(f"MATCH (u: User), (J: JournalMaster), (j: Journal), (j)-[*]->(J)-[r: link]->(u) WHERE u.name = '{username}' AND j.name = '{journal_title}' SET j.name = '{journal_title}', j.body = '{journal_body}' ", journal_title=journal_title, journal_body=journal_body)

        # Get user input for dicts

        send("Lets add an update to your day")
        send("On a scale of 1 - 10 how is your;\n")
        
        send("return "+"Mood?")
        mood = (sender_socket.recv(BUFFER_SIZE).decode())
        
        send("return "+"Anxiety?")
        anxiety = (sender_socket.recv(BUFFER_SIZE).decode())
        
        send("return "+"Depression?")
        depression = (sender_socket.recv(BUFFER_SIZE).decode())
        
        send("return " + "Energy")
        energy = (sender_socket.recv(BUFFER_SIZE).decode())
        
        send(f"\n Journal Title: {journal_title}\n Body: {journal_body}\n Mood: {mood}\n Anxiety: {anxiety}\n Depression: {depression}\n Energy: {energy}")
	
        # Convert dict to string, remove brackets

        journal_body = str(journal_body)
        journal_body = journal_body.replace('[', '')
        journal_body = journal_body.replace(']', '')
        journal_body = journal_body.replace("'", '')

        anxiety = str(anxiety)
        anxiety = anxiety.replace('[', '')
        anxiety = anxiety.replace(']', '')
        anxiety = anxiety.replace("'", '')

        mood = str(mood)
        mood = mood.replace('[', '')
        mood = mood.replace(']', '')
        mood = mood.replace("'", '')

        depression = str(depression)
        depression = depression.replace('[', '')
        depression = depression.replace(']', '')
        depression = depression.replace("'", '')

        energy = str(energy)
        energy = energy.replace('[', '')
        energy = energy.replace(']', '')
        energy = energy.replace("'", '')

        # Send changes to database

        graph.run(f"MATCH (j: Journal), (J: JournalMaster), (u: User), (j)-[*]->(J)-[r: link]->(u) WHERE j.name = '{journal_title}' AND u.name = '{username}' SET j.mood = '{mood}', j.anxiety = '{anxiety}', j.depression = '{depression}', j.energy = '{energy}' ", mood=mood, journal_title=journal_title, anxiety=anxiety, depression=depression, energy=energy, username=username)
