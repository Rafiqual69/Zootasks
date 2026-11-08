from allauth.account.adapter import DefaultAccountAdapter


class ExistingRegistrationOnlyAccountAdapter(DefaultAccountAdapter):
    """Prevent allauth's generic signup route bypassing ZooTasks registration."""

    def is_open_for_signup(self, request):
        return False
