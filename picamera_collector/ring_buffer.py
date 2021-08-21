class RingBuffer(object):
    def __init__(self,capacity):
        self.pos = 0
        self.last_image = 0
        self.end = 0
        self.capacity = capacity
        self.buffer = [ None for i in range(self.capacity)]

    def add_to_buffer(self,image):
        self.buffer[self.pos]=image
        self.last_image = self.pos
        self.pos += 1
        self.pos = self.pos % self.capacity
        self.end = max(self.last_image,self.end)

    def get(self,i):
        return self.buffer[i]

    def get_state(self):
        return (self.last_image,self.end)

if __name__ == '__main__':
    b = RingBuffer(3)

    for i in range(5):
        b.add_to_buffer(i)
        print(b.get_state())
