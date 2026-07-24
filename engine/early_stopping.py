"""
==============================================================
BTSecBench_v2

Early Stopping Engine


==============================================================
"""


class EarlyStopping:
    """
    Early stopping utility.

    Parameters
    ----------
    patience : int
        Number of epochs to wait before stopping.

    min_delta : float
        Minimum improvement required.

    mode : str
        "min" -> lower metric is better (loss)
        "max" -> higher metric is better (accuracy)
    """

    def __init__(
        self,
        patience=10,
        min_delta=0.0,
        mode="max",
    ):

        assert mode in ["min", "max"]

        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode

        self.best_score = None
        self.counter = 0
        self.should_stop = False

    ############################################################

    def reset(self):

        self.best_score = None
        self.counter = 0
        self.should_stop = False

    ############################################################

    def step(self, score):

        if self.best_score is None:

            self.best_score = score

            return False

        ########################################################

        if self.mode == "max":

            improved = score > (
                self.best_score + self.min_delta
            )

        else:

            improved = score < (
                self.best_score - self.min_delta
            )

        ########################################################

        if improved:

            self.best_score = score

            self.counter = 0

        else:

            self.counter += 1

            if self.counter >= self.patience:

                self.should_stop = True

        return self.should_stop

    ############################################################

    def state_dict(self):

        return {

            "best_score": self.best_score,

            "counter": self.counter,

            "should_stop": self.should_stop

        }

    ############################################################

    def load_state_dict(self, state):

        self.best_score = state["best_score"]

        self.counter = state["counter"]

        self.should_stop = state["should_stop"]