"""This iterable will automatically show tqdm progress bars on each of its passes or on one specific pass"""
from tqdm import tqdm


class CustomTqdmIterator:
    def __init__(self, elements, specific_pass=-1, desc=""):
        self.elements = elements

        self.desc = desc

        self.specific_pass = specific_pass
        self.counter = 0

    def __len__(self):
        return len(self.elements)

    def __iter__(self):
        self.counter += 1
        if self.specific_pass == -1 or self.counter == self.specific_pass:
            return tqdm(self.elements, desc=self.desc).__iter__()

        return iter(self.elements)
