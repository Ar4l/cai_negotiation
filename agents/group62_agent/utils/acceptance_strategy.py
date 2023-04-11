import decimal
import numpy as np

THRESHOLD = 0.985

class AcceptanceStrategy:

    def __init__(self, progress, profile, opponent_model, received_bids, received_bid, next_bid, params=None):
        """
        Constructor for an acceptance strategy object.
        @param progress: the current negotiation progress from 0 to 1.
        @param received_bids: the history of all the opponent's bids so far.
        @param received_bid: the last received bid.
        @param next_bid: the next bid that will be offered by the agent if the received bid will not be accepted.
        """
        self._opponent_model = opponent_model
        self.progress = progress
        self.profile = profile
        self.received_bids = received_bids
        self.next_bid = next_bid
        self.received_bid = received_bid  # = received_bids[-1]

        self.threshold = params.get('threshold', THRESHOLD) if params else THRESHOLD

    def ac_combi_max_w(self, scale=1.0, utility_gap=0.0):
        """
        Combined strategy: Accepts when the bid is better than all offers seen in the previous time window
        """
        window = self._get_window()
        max_w = np.max(window) if len(window) != 0 else 0

        ac_time_and_constant = self._ac_time(self.threshold) and self.profile.getUtility(self.received_bid) >= max_w
        return self._ac_next(scale, utility_gap) or ac_time_and_constant

    def ac_combi_avg_w(self, scale=1.0, utility_gap=0.0):
        """
        Combined strategy:
        Accepts when the bid is better than the average utility of offers during the previous time window
        """
        window = self._get_window()
        avg_w = np.mean(window) if len(window) != 0 else 0

        ac_time_and_constant = self._ac_time(self.threshold) and self.profile.getUtility(self.received_bid) >= avg_w
        return self._ac_next(scale, utility_gap) or ac_time_and_constant

    def _ac_next(self, scale_factor, utility_gap):
        """
        Accepts bid when the opponent's bid is better than the agent's upcoming bid
            alpha * utility of the opponent's offer + beta >= utility of the bid agent is ready to send out
        αlpha: the scale factor by which we multiply the opponent’s bid (default: 1)
        beta: the minimal ‘utility gap’ that is sufficient to accept (default: 0)
        """
        own_utility = self.profile.getUtility(self.received_bid)

        result = decimal.Decimal(scale_factor) * own_utility + decimal.Decimal(utility_gap) \
                 >= self.profile.getUtility(self.next_bid)

        # TODO: play with these values and see what improves performance
        # opponent_util = self._opponent_model.predict_utility(self.received_bid)
        # constant = own_utility > decimal.Decimal(0.70)
        # difference = decimal.Decimal(own_utility - decimal.Decimal(opponent_util)).__abs__() < decimal.Decimal(0.50)

        return result  # and constant and difference

    def _ac_time(self, threshold):
        """Accepts bid when the time threshold has passed (default: 0.98)"""
        return self.progress >= threshold

    def _get_window(self):
        """ Returns the time window """
        if self.progress == 0:
            max_bids = 100
        else:
            max_bids = len(self.received_bids) // self.progress
        num_bids = int(max_bids * self.progress)
        remaining_bids = int(max_bids * (1 - self.progress))

        lower_bound = num_bids - remaining_bids
        upper_bound = num_bids if num_bids > 0 else 0

        if upper_bound > len(self.received_bids) - 1:
            upper_bound = len(self.received_bids) - 1

        window = self.received_bids[lower_bound: upper_bound]
        window_utility = []
        for bid in window:
            window_utility.append(self.profile.getUtility(bid))
        return window_utility
