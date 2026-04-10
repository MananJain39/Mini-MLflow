import os
import shutil
from mini_mlflow.server.storage.base import BaseStorage


class LocalStorage(BaseStorage):
    """Local file system storage backend."""

    def __init__(self, artifact_root: str = "storage/artifacts"):
        self.artifact_root = artifact_root

    def log_artifact(self, run_id: str, file_path: str) -> str:
        """
        Log an artifact to the local file system storage.

        Parameters
        ----------
        run_id : str
            The ID of the run the artifact belongs to.
        file_path : str
            The local path to the artifact to upload.

        Returns
        -------
        str
            The destination path where the artifact was stored.
        """
        run_dir = os.path.join(self.artifact_root, run_id)
        os.makedirs(run_dir, exist_ok=True)

        filename = os.path.basename(file_path)
        dest = os.path.join(run_dir, filename)

        if not os.path.isfile(file_path):
            raise ValueError(f"File not found: {file_path}")

        shutil.copy(file_path, dest)
        return dest
