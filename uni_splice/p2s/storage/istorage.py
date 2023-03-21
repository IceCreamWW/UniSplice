class IStorage:
    def __getitem__(self, idx):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def open(self):
        pass

    def close(self):
        pass
