class CLink:
    """
    Emulates a computational link using logic derived from MIPS assembly
    """
    def __init__(self, link_id=None):
        self.link_id = link_id
        self.child = None
        self.parent = None
        self.active = True
        self.metadata = {}

    def __del__(self):
        self.remove()
        self.metadata.clear()

    def add_link(self, link):
        if not link:
            return
        link.parent = self
        if self.child:
            link.child = self.child
            self.child.parent = link
        self.child = link

    def remove(self):
        if self.parent:
            self.parent.child = self.child
        if self.child:
            self.child.parent = self.parent
        self.parent = None
        self.child = None

    def del_child(self):
        current = self.child
        while current:
            next_link = current.child
            current.remove()
            current = next_link

    def remove_all(self):
        self.del_child()
        self.remove()

    def search_link(self, link_id):
        current = self
        while current:
            if current.link_id == link_id:
                return current
            current = current.child
        return None

    def action_link(self, file):
        file.seek(0)
        while True:
            line = file.readline()
            if not line:
                break
            print(f"Processing: {line.strip()}")

    def get_source(self):
        current = self
        while current.parent:
            current = current.parent
        return current
