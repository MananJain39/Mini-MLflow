from abc import ABC, abstractmethod
import os


class BaseStorage(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def log_artifact(self, run_id: str, file_path: str) -> str:
        """
        Log an artifact to the storage backend.

        Parameters
        ----------
        run_id : str
            The ID of the run the artifact belongs to.
        file_path : str
            The local path to the artifact to upload.

        Returns
        -------
        str
            The path or URI where the artifact was stored.
        """
        pass
