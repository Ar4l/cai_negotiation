import decimal
import numpy as np


class AcceptanceStrategy:

    def __init__(self, progress, profile, received_bids=None, received_bid=None, next_bid=None):
        """
        Constructs an acceptance strategy object.
        @param progress: the current negotiation progress from 0 to 1.
        @param received_bids: the history of all the opponent's bids so far.
        @param received_bid: the last received bid.
        @param next_bid: the next bid that will be offered by the agent if the received bid will not be accepted.
        """
        self.progress = progress
        self.profile = profile
        if received_bids and len(received_bids) == 0:
            print("No bid history received")
        elif received_bids:
            self.received_utility_hist = []
            for bid in received_bids:
                self.received_utility_hist.append(self.profile.getUtility(bid))
            self.received_bids = received_bids
        self.next_bid = next_bid
        self.received_bid = received_bid  # = received_bids[-1]

    def ac_combi_max_w(self, scale=1.0, utility_gap=0.0, threshold=0.98):
        """
        Combined strategy: Accepts when the bid is better than all offers seen in the previous time window
        """
        window = self._get_window()
        if len(window) != 0:
            # Take the maximum of the bid window
            max_w = np.max(window)
        else:
            max_w = 0

        ac_next = self.ac_next(scale, utility_gap)
        ax_time_and_constant = self.ac_time(threshold) and self.profile.getUtility(self.received_bid) >= max_w
        return ac_next or ax_time_and_constant

    def ac_combi_avg_w(self, scale=1.0, utility_gap=0.0, threshold=0.98):
        """
        Combined strategy:
        Accepts when the bid is better than the average utility of offers during the previous time window
        """
        window = self._get_window()
        if len(window) != 0:
            avg_w = np.mean(window)
        else:
            avg_w = 0

        ac_next = self.ac_next(scale, utility_gap)
        ax_time_and_constant = self.ac_time(threshold) and self.profile.getUtility(self.received_bid) >= avg_w
        return ac_next or ax_time_and_constant

    def ac_time(self, threshold):
        """Accepts bid when the time threshold has passed (default: 0.98)"""
        return self.progress >= threshold

    def ac_next(self, scale_factor, utility_gap):
        """
        Accepts bid when the opponent's bid is better than the agent's upcoming bid
            alpha * utility of the opponent's offer + beta >= utility of the bid agent is ready to send out
        αlpha: the scale factor by which we multiply the opponent’s bid (default: 1)
        beta: the minimal ‘utility gap’ that is sufficient to accept (default: 0)
        """
        result = decimal.Decimal(scale_factor) * self.profile.getUtility(self.received_bid) \
               + decimal.Decimal(utility_gap) >= self.profile.getUtility(self.next_bid)

        return result

    def _get_window(self):
        if self.progress == 0:
            max_bids = 100
        else:
            max_bids = len(self.received_utility_hist) // self.progress
        num_bids = int(max_bids * self.progress)
        remaining_bids = int(max_bids * (1 - self.progress))
        # compute bounds of the bid window
        lower_bound = num_bids - remaining_bids
        upper_bound = num_bids if num_bids > 0 else 0

        if upper_bound > len(self.received_utility_hist) - 1:
            upper_bound = len(self.received_utility_hist) - 1

        return self.received_utility_hist[lower_bound: upper_bound]
