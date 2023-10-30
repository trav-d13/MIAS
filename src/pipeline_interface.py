from abc import ABC, abstractmethod


class Pipeline(ABC):
    @staticmethod
    @abstractmethod
    def data_pipeline(df, tf=None):
        pass
