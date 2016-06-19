class Node(object):
    def __init__(self, data=None, next=None):
        self.data = data
        self.next = next

    def get_data(self):
        return self.data

    def get_next(self):
        return self.next

    def set_next(self, new_next):
        self.next = new_next

class LinkedList(object):
    def __init__(self, head=None):
        self.head = head

    def size(self):
        count = 0
        current = self.head
        while current:
            current = current.get_next()
            count += 1
        return count

    def insert(self, data):
        new = Node(data)
        new.set_next(self.head)
        self.head = new

