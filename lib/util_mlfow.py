import atexit
import subprocess
import sys
import time

import mlflow

from definitions import MLFLOW_SERVER_PORT, MLFLOW_SERVER_URI


def setup_mlflow_tracking(experiment_name="dspy-aid-activity-classification"):
    """Configure MLflow tracking."""
    mlflow.dspy.autolog(
        log_compiles=True,
        log_evals=True,
        log_traces_from_compile=True,
    )
    mlflow.set_experiment(experiment_name)
    mlflow.set_tracking_uri(MLFLOW_SERVER_URI)


class MLflowServerManager:
    """Manages MLflow server lifecycle."""

    def __init__(
        self,
        host="127.0.0.1",
        port=MLFLOW_SERVER_PORT,
        db_path="jordan_activities.sqlite",
    ):
        self.host = host
        self.port = port
        self.db_path = db_path
        self.process = None

    def start(self):
        """Start MLflow server in background."""
        try:
            self.process = subprocess.Popen(
                [
                    "mlflow",
                    "server",
                    "--host",
                    self.host,
                    "--port",
                    str(self.port),
                    "--backend-store-uri",
                    f"sqlite:///{self.db_path}",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait a moment for server to start
            time.sleep(3)

            if self.process.poll() is None:  # Still running
                print(f"MLflow server started on {self.host}:{self.port}")
                # Register cleanup on exit
                atexit.register(self.stop)
                return True
            else:
                print("Failed to start MLflow server", file=sys.stderr)
                return False

        except FileNotFoundError:
            print(
                "Error: mlflow command not found. Make sure MLflow is installed.",
                file=sys.stderr,
            )
            return False

    def stop(self):
        """Stop MLflow server."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()
            print("MLflow server stopped")
