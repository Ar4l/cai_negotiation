from geniusweb.bidspace.AllBidsList import AllBidsList
from geniusweb.issuevalue import Bid
from random import randint


class BiddingStrategy:
    # Makes concession of 0.05 if stuck
    ISO_TOLERANCE = 0.05
    # Starting reservation value
    RESERVATION_VALUE = 0.95
    # The boulware speed at which the agent concedes -> 0.000045 results in a hardliner agent
    CONCEDING_SPEED = 0.000045

    def __init__(self, profile, opponent_model, domain):
        self._profile = profile
        self._opponent_model = opponent_model
        self._domain = domain

        self._iso_tolerance = self.ISO_TOLERANCE
        self._offer_acceptance = self.RESERVATION_VALUE

        self._sorted_bids = self._sort_bids(AllBidsList(self._domain))
        self._issues = domain.getIssues()

    # Return a random bid
    def _get_random_bid(self):
        bids = AllBidsList(self._domain)
        return bids.get(randint(0, bids.size() - 1))

    # Return the first n bids with iso-level of own utility function that is closer to the current opponent’s bid
    # If the number of bids to be returned is not provided, return the first 7 ones
    def _iso_curve_bids(self, n=7):
        bids = []
        i = 0
        for bid in self._sorted_bids:
            if self._offer_acceptance + self._iso_tolerance > bid['utility'] > self._offer_acceptance - self._iso_tolerance:
                bids.append(bid['bid'])
                i += 1
            if i == n:
                break
        return bids

    # Sort bids descending on utility
    def _sort_bids(self, bids):
        sorted_bids = []
        for each_bid in bids:
            bid = {"bid": each_bid, "utility": self._profile.getUtility(each_bid)}
            sorted_bids.append(bid)
        return sorted(sorted_bids, key=lambda x: x['utility'], reverse=True)

    # Decrease the agent's accepted utility if no progress is being made
    # The decrease starts after the agent has offered 5 bids, and no acceptance was reached
    def _decrease_offer(self, agent_bids, opponent_bids, boulware):
        if len(agent_bids) > 5:
            # Calculate the agent's utility of its last bid and of the bid from the beginning of the window
            agentLastUtil = self._profile.getUtility(agent_bids[len(agent_bids) - 1])
            agentFirstWindowUtil = self._profile.getUtility(agent_bids[len(agent_bids) - 6])

            # Calculate the opponent's utility of its last bid
            opponentLastUtil = self._profile.getUtility(opponent_bids[len(opponent_bids) - 1])
            opponentPenlastUtil = self._profile.getUtility(opponent_bids[len(opponent_bids) - 2])

            # If the agent's utility hasn't changed throughout the bidding window and the opponent's utility is
            # decreasing, decrease agent's utility based on the boulware tolerance
            if agentLastUtil == agentFirstWindowUtil and opponentLastUtil <= opponentPenlastUtil:
                self._offer_acceptance = boulware

    # Find a bid using Trade-off strategy
    def find_bid(self, last_opponent_bid, opponent_bids, agent_bids, boulware) -> Bid:
        # TODO: I don't think we need to update the opponent_model here, but just in case leaving it here. If so also add it as a param
        # self._opponent_model = opponent_model

        # Decrease the agent's accepted utility with each passing bid
        self._decrease_offer(opponent_bids, agent_bids, boulware)

        # Generate n = 7 bids on the same ISO curve level
        bids = self._iso_curve_bids()

        # If the agent hasn't generated any ISO curve bids, start the negotiation by offering a random bid
        if len(bids) == 0:
            return self._get_random_bid()

        # If we reached this point in the code it means a set of ISO curve bids were generated
        # If the opponent has not offered any bids, return the first ISO curve generated bid
        if last_opponent_bid is None:
            return bids[0]

        # If both the agent and the opponent have generated bids,
        # Choose the bid with the maximum utility for the opponent (Trade-off/T4T hybrid) from the ISO curve bids
        max_util = 0
        best_bid = bids[0]
        for bid in bids:
            opponent_util = self._opponent_model.predict_utility(bid)
            if opponent_util > max_util:
                max_util = opponent_util
                best_bid = bid

        return best_bid
