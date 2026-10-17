from allauth.account.adapter import DefaultAccountAdapter


class ExistingRegistrationOnlyAccountAdapter(DefaultAccountAdapter):
    """Keep password signup on ZooTasks' existing atomic registration view."""

    def is_open_for_signup(self, request):
        return False
