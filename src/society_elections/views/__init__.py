from .election import index_view
from .nomination import (NominationFormView, NominationSuccessView,
                         verify_candidate_view)
from .vote import (VoteSubmittedView, create_vote_ajax, delete_vote_ajax,
                   vote_view)
from .voter import create_voter_view, verify_voter_view
