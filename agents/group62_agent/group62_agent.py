import logging
from time import time
from typing import cast

from geniusweb.actions.Accept import Accept
from geniusweb.actions.Action import Action
from geniusweb.actions.Offer import Offer
from geniusweb.actions.PartyId import PartyId
from geniusweb.inform.ActionDone import ActionDone
from geniusweb.inform.Finished import Finished
from geniusweb.inform.Inform import Inform
from geniusweb.inform.Settings import Settings
from geniusweb.inform.YourTurn import YourTurn
from geniusweb.issuevalue.Bid import Bid
from geniusweb.issuevalue.Domain import Domain
from geniusweb.party.Capabilities import Capabilities
from geniusweb.party.DefaultParty import DefaultParty
from geniusweb.progress.ProgressRounds import ProgressRounds
from geniusweb.profile.utilityspace.LinearAdditiveUtilitySpace import (
    LinearAdditiveUtilitySpace,
)
from geniusweb.profileconnection.ProfileConnectionFactory import (
    ProfileConnectionFactory,
)
from geniusweb.progress.ProgressTime import ProgressTime
from geniusweb.references.Parameters import Parameters
from tudelft_utilities_logging.ReportToLogger import ReportToLogger

from .utils.acceptance_strategy import AcceptanceStrategy
from .utils.opponent_model import OpponentModel
from .utils.bidding_strategy import BiddingStrategy


class Group62Agent(DefaultParty):
    """
    Group62 Agent.
    """

    def __init__(self):
        super().__init__()
        self.logger: ReportToLogger = self.getReporter()

        self.domain: Domain = None
        self.parameters: Parameters = None
        self.profile: LinearAdditiveUtilitySpace = None
        self.progress: ProgressTime = None
        self.me: PartyId = None
        self.other: str = None
        self.settings: Settings = None
        self.storage_dir: str = None

        self.last_received_bid: Bid = None
        self.opponent_model: OpponentModel = None
        self.bidding_strat: BiddingStrategy = None
        self.acceptance_strat = None
        self.logger.log(logging.INFO, "party is initialized")
        # List of all received bids
        self.received_bids: list[Bid] = []
        # Keep track of the bids the agent sends
        self.sent_bids: list[Bid] = []
        # Boulware value equals the reservation value at the start

    def notifyChange(self, data: Inform):
        """MUST BE IMPLEMENTED
        This is the entry point of all interaction with your agent after is has been initialised.
        How to handle the received data is based on its class type.

        Args:
            info (Inform): Contains either a request for action or information.
        """

        # a Settings message is the first message that will be send to your
        # agent containing all the information about the negotiation session.
        if isinstance(data, Settings):
            self.settings = cast(Settings, data)
            self.me = self.settings.getID()

            # progress towards the deadline has to be tracked manually through the use of the Progress object
            self.progress = self.settings.getProgress()

            self.parameters = self.settings.getParameters()
            self.storage_dir = self.parameters.get("storage_dir")

            # the profile contains the preferences of the agent over the domain
            profile_connection = ProfileConnectionFactory.create(
                data.getProfile().getURI(), self.getReporter()
            )
            self.profile = profile_connection.getProfile()
            self.domain = self.profile.getDomain()
            profile_connection.close()

            # TODO: Initialize the agent's components
            self.opponent_model = OpponentModel(self.domain, self.parameters.get("opponent_model"))
            self.bidding_strat = BiddingStrategy(self.profile, self.opponent_model, self.domain, self.parameters.get("bidding_strategy"))
            self.boulware = self.bidding_strat.reservation_value
            # self.acceptance_strat = AcceptanceStrategy(self.progress, self.profile)

        # ActionDone informs you of an action (an Offer or an Accept) that is performed by one of the agents (including yourself)
        elif isinstance(data, ActionDone):
            action = cast(ActionDone, data).getAction()
            actor = action.getActor()

            # If the action came from the opponent
            if actor != self.me:
                # Obtain the name of the opponent, cutting of the position ID
                self.other = str(actor).rsplit("_", 1)[0]

                # Process the action done by opponent
                self.opponent_action(action)

        # YourTurn notifies you that it is your turn to act
        elif isinstance(data, YourTurn):
            # execute a turn
            self.my_turn()

        # Finished will be sent if the negotiation has ended (through agreement or deadline)
        elif isinstance(data, Finished):
            self.save_data()
            # terminate the agent MUST BE CALLED
            self.logger.log(logging.INFO, "party is terminating:")
            super().terminate()
        else:
            self.logger.log(logging.WARNING, "Ignoring unknown info " + str(data))

    # Tell geniusweb what settings this agent can handle
    def getCapabilities(self) -> Capabilities:
        """Method to indicate to the protocol what the capabilities of this agent are.
        Leave it as is for the ANL 2022 competition

        Returns:
            Capabilities: Capabilities representation class
        """
        return Capabilities(
            set(["SAOP"]),
            set(["geniusweb.profile.utilityspace.LinearAdditive"]),
        )

    def send_action(self, action: Action):
        """Sends an action to the opponent(s)

        Args:
            action (Action): action of this agent
        """
        self.getConnection().send(action)

    # Return a description of the agent
    def getDescription(self) -> str:
        """Returns a description of your agent. 1 or 2 sentences.

        Returns:
            str: Agent description
        """
        # TODO: finalize the description
        return "Group 62 agent, implementing a hybrid Trade-off and T4T bidding strategy with boulware time dependency" \
               "and ac_combi_max_w and ac_combi_avg_w as acceptance strategies"

    def opponent_action(self, action):
        """Process an action that was received from the opponent.

        Args:
            action (Action): action of opponent
        """
        # if it is an offer, set the last received bid
        if isinstance(action, Offer):
            # create opponent model if it was not yet initialised
            if self.opponent_model is None:
                self.opponent_model = OpponentModel(self.domain)

            bid = cast(Offer, action).getBid()

            self.opponent_model.update(bid, self.progress)
            # Set the last received bid from the opponent
            self.last_received_bid = bid
            self.received_bids.append(self.last_received_bid)

            # self.opponent_model.update_frequencies(self._last_received_bid)

    def my_turn(self):
        """This method is called when it is our turn. It should decide upon an action
        to perform and send this action to the opponent.
        """
        # Decrease the boulware value as time passes
        self.decrease_boulware()

        # Generate a bid for the opponent using the bidding strategy
        bid = self.bidding_strat.find_bid(self.last_received_bid, self.received_bids,
                                          self.sent_bids, self.boulware)

        # Check if the bid received from the opponent is better than ours
        if self.accept_condition(self.last_received_bid, bid):
            # If so, accept the offer
            action = Accept(self.me, self.last_received_bid)
        else:
            # If not, propose our bid as counter offer
            action = Offer(self.me, bid)
            self.sent_bids.append(bid)

        # Advance the progress as more rounds pass
        if isinstance(self.progress, ProgressRounds):
            self.progress = self.progress.advance()

        # Send the action (either an Offer or an Accept)
        self.send_action(action)

    def save_data(self):
        """This method is called after the negotiation is finished. It can be used to store data
        for learning capabilities. Note that no extensive calculations can be done within this method.
        Taking too much time might result in your agent being killed, so use it for storage only.
        """
        data = "Data for learning (see README.md)"
        with open(f"{self.storage_dir}/data.md", "w") as f:
            f.write(data)

    def accept_condition(self, received_bid: Bid, bid: Bid) -> bool:
        if bid is None:
            return False
        if len(self.received_bids) == 0:
            return False

        # progress of the negotiation session between 0 and 1 (1 is deadline)
        progress = self.progress.get(time() * 1000)

        # very basic approach that accepts if the offer is valued above 0.7 and
        # 95% of the time towards the deadline has passed
        # conditions = [
        #    self.profile.getUtility(bid) > 0.8,
        #    progress > 0.95,
        # ]
        # return all(conditions)

        ac = AcceptanceStrategy(progress, self.profile, self.opponent_model, self.received_bids, received_bid, bid, self.parameters.get("acceptance_strategy"))
        return ac.ac_combi_max_w()

    # Decrease the boulware value in time based on the conceding speed
    def decrease_boulware(self):
        self.boulware = self.boulware - (self.bidding_strat.conceding_speed * self.progress.get(time() * 1000))

    # TODO: Delete the old template code and clean-up once we're sure our agent works
    """
    # Original find_bid method from the template
    def find_bid(self) -> Bid:
        # compose a list of all possible bids
        domain = self.profile.getDomain()
        all_bids = AllBidsList(domain)

        best_bid_score = 0.0
        best_bid = None

        # take 500 attempts to find a bid according to a heuristic score
        for _ in range(500):
            bid = all_bids.get(randint(0, all_bids.size() - 1))
            bid_score = self.score_bid(bid)
            if bid_score > best_bid_score:
                best_bid_score, best_bid = bid_score, bid

        return best_bid
    """

    """
    def score_bid(self, bid: Bid, alpha: float = 0.95, eps: float = 0.1) -> float:
        Calculate heuristic score for a bid

        Args:
            bid (Bid): Bid to score
            alpha (float, optional): Trade-off factor between self interested and
                altruistic behaviour. Defaults to 0.95.
            eps (float, optional): Time pressure factor, balances between conceding
                and Boulware behaviour over time. Defaults to 0.1.

        Returns:
            float: score
  
        progress = self.progress.get(time() * 1000)

        our_utility = float(self.profile.getUtility(bid))

        time_pressure = 1.0 - progress ** (1 / eps)
        score = alpha * time_pressure * our_utility

        if self.opponent_model is not None:
            opponent_utility = self.opponent_model.get_predicted_utility(bid)
            opponent_score = (1.0 - alpha * time_pressure) * opponent_utility
            score += opponent_score

        return score
    """
